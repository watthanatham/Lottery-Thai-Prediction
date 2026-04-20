from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.analysis.models import LotteryDraw

import datetime
import requests
from bs4 import BeautifulSoup
import re
import tempfile
import os
from pdfminer.high_level import extract_text


class Command(BaseCommand):
    help = 'Import historical lottery draws from GLO website for a date range (no fallback)'

    def add_arguments(self, parser):
        parser.add_argument('--start', type=str, help='Start date YYYY-MM-DD (inclusive)')
        parser.add_argument('--end', type=str, help='End date YYYY-MM-DD (inclusive)')
        parser.add_argument('--dry-run', action='store_true', help='Do not save to DB; just report')

    def handle(self, *args, **options):
        start = options.get('start')
        end = options.get('end')
        dry_run = options.get('dry_run', False)

        if not start or not end:
            self.stderr.write('Please provide --start and --end in YYYY-MM-DD format')
            return

        try:
            start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        except ValueError:
            self.stderr.write('Invalid date format. Use YYYY-MM-DD')
            return

        # Build list of candidate draw dates (1st and 16th) between start and end
        dates = []
        cur = datetime.date(start_date.year, start_date.month, 1)
        while cur <= end_date:
            d1 = cur.replace(day=1)
            d16 = cur.replace(day=16)
            if start_date <= d1 <= end_date:
                dates.append(d1)
            if start_date <= d16 <= end_date:
                dates.append(d16)
            # advance to first of next month
            year = cur.year + (cur.month // 12)
            month = (cur.month % 12) + 1
            cur = datetime.date(year, month, 1)

        self.stdout.write(f'Found {len(dates)} candidate draw dates between {start} and {end}')

        url_templates = [
            'https://www.glo.or.th/results?date={date}',
            'https://www.glo.or.th/lotto-result?date={date}',
            'https://www.glo.or.th/lottery-result?date={date}',
            'https://www.glo.or.th/home-page/result?date={date}',
            'https://www.glo.or.th/?date={date}',
        ]

        created = 0
        exists = 0
        failed = 0

        session = requests.Session()
        headers = {
            'User-Agent': 'lottery-importer/1.0 (+https://example.local)'
        }

        for d in dates:
            date_str = d.isoformat()
            self.stdout.write(f'Processing {date_str}...')

            # Skip if exists
            if LotteryDraw.objects.filter(draw_date=d).exists():
                self.stdout.write(self.style.NOTICE(f'⊘ Exists:  {date_str}'))
                exists += 1
                continue

            page_text = None
            for tpl in url_templates:
                url = tpl.format(date=date_str)
                try:
                    r = session.get(url, headers=headers, timeout=15)
                except Exception as e:
                    # try next template
                    continue
                if r.status_code != 200:
                    continue
                text = r.text
                # cheap check: look for 6-digit number in text
                if re.search(r'\b\d{6}\b', text):
                    page_text = text
                    self.stdout.write(f'  Retrieved from {url}')
                    break

            if not page_text:
                # Try to find PDF links on the GLO results page
                pdf_found = False
                for tpl in url_templates:
                    url = tpl.format(date=date_str)
                    try:
                        r = session.get(url, headers=headers, timeout=15)
                    except Exception:
                        continue
                    if r.status_code != 200:
                        continue
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.lower().endswith('.pdf'):
                            pdf_url = href if href.startswith('http') else requests.compat.urljoin(url, href)
                            self.stdout.write(f'  Found PDF: {pdf_url}')
                            try:
                                pr = session.get(pdf_url, headers=headers, timeout=30)
                                if pr.status_code == 200:
                                    # write to temp file and extract text
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                                        tf.write(pr.content)
                                        tf.flush()
                                        tfname = tf.name
                                    try:
                                        pdf_text = extract_text(tfname)
                                    finally:
                                        try:
                                            os.remove(tfname)
                                        except Exception:
                                            pass
                                    if re.search(r'\b\d{6}\b', pdf_text):
                                        page_text = pdf_text
                                        pdf_found = True
                                        break
                            except Exception as e:
                                self.stderr.write(self.style.WARNING(f'  PDF download/parse failed: {e}'))
                    if pdf_found:
                        break
                if not page_text:
                    self.stderr.write(self.style.WARNING(f'! Could not retrieve result page or PDF for {date_str}'))
                    failed += 1
                    continue

            # Parse first 6-digit number as first_prize
            try:
                # Use BeautifulSoup to strip markup and search
                soup = BeautifulSoup(page_text, 'html.parser')
                # prefer visible text
                visible = ' '.join(soup.stripped_strings)
                m = re.search(r'\b(\d{6})\b', visible)
                if not m:
                    raise ValueError('No 6-digit number found')
                first_prize = m.group(1)

                if dry_run:
                    self.stdout.write(self.style.SUCCESS(f'✓ Found (dry-run): {date_str} → {first_prize}'))
                else:
                    obj, created_flag = LotteryDraw.objects.get_or_create(
                        draw_date=d,
                        defaults={
                            'first_prize': first_prize,
                            'notes': f'Imported from GLO on {timezone.now().isoformat()}'
                        }
                    )
                    if created_flag:
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f'✓ Created: {date_str} → {first_prize}'))
                    else:
                        exists += 1
                        self.stdout.write(self.style.NOTICE(f'⊘ Exists after all: {date_str}'))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'✗ Failed to parse {date_str}: {e}'))
                failed += 1

        self.stdout.write('---')
        self.stdout.write(self.style.SUCCESS(f'Created: {created} | Exists: {exists} | Failed: {failed}'))
