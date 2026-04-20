from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.analysis.models import LotteryDraw

import datetime
import requests
from bs4 import BeautifulSoup
import re


class Command(BaseCommand):
    help = 'Import historical lottery draws from Sanook archive between start and end dates'

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

        base_archive = 'https://news.sanook.com/lotto/archive/'
        session = requests.Session()
        headers = {'User-Agent': 'lottery-importer/1.0 (+https://example.local)'}

        seen_links = set()
        to_process = []

        # paginate archive pages until we reach older than start_date or no more pages
        page = 1
        while True:
            if page == 1:
                url = base_archive
            else:
                url = f'https://news.sanook.com/lotto/archive/page/{page}/'
            try:
                r = session.get(url, headers=headers, timeout=15)
            except Exception as e:
                self.stderr.write(f'Could not retrieve {url}: {e}')
                break
            if r.status_code != 200:
                break
            soup = BeautifulSoup(r.text, 'html.parser')
            # find all links to per-draw pages: /lotto/check/<digits>/
            for a in soup.find_all('a', href=True):
                href = a['href']
                m = re.search(r'/lotto/check/(\d{8})/', href)
                if m:
                    token = m.group(1)
                    if token in seen_links:
                        continue
                    seen_links.add(token)
                    # parse date from token: ddmmyyyy (Thai year) or ddmmyy? we expect 8-digit like 01042569
                    try:
                        day = int(token[0:2])
                        month = int(token[2:4])
                        year_be = int(token[4:8])
                        # if year looks like 4-digit BE (>=2500), convert to CE
                        if year_be > 2500:
                            year = year_be - 543
                        else:
                            year = year_be
                        draw_date = datetime.date(year, month, day)
                    except Exception:
                        # fallback: skip malformed token
                        continue
                    if not (start_date <= draw_date <= end_date):
                        continue
                    full_url = href if href.startswith('http') else requests.compat.urljoin('https://news.sanook.com', href)
                    to_process.append((draw_date, full_url))
            # stop if there is a "หน้าถัดไป" link; otherwise break when no new links found or oldest date < start
            # try to detect pagination end by checking presence of 'next' link
            next_link = soup.find('a', href=True, text=lambda t: t and 'หน้าถัดไป' in t)
            page += 1
            # safety: limit pages to 200
            if page > 200:
                break
            # small optimization: if we already collected many and the last added draw_date is earlier than start_date, we can break
            if to_process and min(d for d, _ in to_process) < start_date:
                break

        self.stdout.write(f'Found {len(to_process)} draw pages to process within range')

        created = 0
        exists = 0
        failed = 0

        for draw_date, draw_url in sorted(to_process):
            self.stdout.write(f'Processing {draw_date} — {draw_url}')
            if LotteryDraw.objects.filter(draw_date=draw_date).exists():
                self.stdout.write(self.style.NOTICE(f'⊘ Exists: {draw_date}'))
                exists += 1
                continue
            try:
                r = session.get(draw_url, headers=headers, timeout=15)
                if r.status_code != 200:
                    raise RuntimeError(f'HTTP {r.status_code}')
                soup = BeautifulSoup(r.text, 'html.parser')
                text = ' '.join(soup.stripped_strings)

                # Parse first prize specifically
                first_prize = None
                m_fp = re.search(r'รางวัลที่\s*1\s*[^(\d)]*?(\d{6})', text)
                if m_fp:
                    first_prize = m_fp.group(1)
                else:
                    # fallback to any 6-digit
                    m = re.search(r'\b(\d{6})\b', text)
                    if m:
                        first_prize = m.group(1)

                if not first_prize:
                    raise ValueError('No 6-digit first-prize number found on page')

                # Parse 3-digit fronts (เลขหน้า 3 ตัว)
                three_front_1 = ''
                three_front_2 = ''
                m_f = re.search(r'เลขหน้า\s*3\s*ตัว\s*([0-9]{3})[^0-9]*([0-9]{3})', text)
                if m_f:
                    three_front_1 = m_f.group(1)
                    three_front_2 = m_f.group(2)
                else:
                    m_f_single = re.search(r'เลขหน้า\s*3\s*ตัว\s*([0-9]{3})', text)
                    if m_f_single:
                        three_front_1 = m_f_single.group(1)

                # Parse 3-digit backs (เลขท้าย 3 ตัว)
                three_back_1 = ''
                three_back_2 = ''
                m_b = re.search(r'เลขท้าย\s*3\s*ตัว\s*([0-9]{3})[^0-9]*([0-9]{3})', text)
                if m_b:
                    three_back_1 = m_b.group(1)
                    three_back_2 = m_b.group(2)
                else:
                    m_b_single = re.search(r'เลขท้าย\s*3\s*ตัว\s*([0-9]{3})', text)
                    if m_b_single:
                        three_back_1 = m_b_single.group(1)

                # Parse 2-digit back (เลขท้าย 2 ตัว)
                two_back = ''
                m2 = re.search(r'เลขท้าย\s*2\s*ตัว\s*([0-9]{1,2})', text)
                if m2:
                    two_back = m2.group(1).zfill(2)

                if dry_run:
                    self.stdout.write(self.style.SUCCESS(f'✓ Found (dry-run): {draw_date} → {first_prize} / 3F: {three_front_1},{three_front_2} / 3B: {three_back_1},{three_back_2} / 2D: {two_back}'))
                else:
                    obj = None
                    created_flag = False
                    if LotteryDraw.objects.filter(draw_date=draw_date).exists():
                        obj = LotteryDraw.objects.get(draw_date=draw_date)
                        # update missing fields if empty
                        updated = False
                        if not obj.first_prize and first_prize:
                            obj.first_prize = first_prize
                            updated = True
                        if not obj.three_front_1 and three_front_1:
                            obj.three_front_1 = three_front_1
                            updated = True
                        if not obj.three_front_2 and three_front_2:
                            obj.three_front_2 = three_front_2
                            updated = True
                        if not obj.three_back_1 and three_back_1:
                            obj.three_back_1 = three_back_1
                            updated = True
                        if not obj.three_back_2 and three_back_2:
                            obj.three_back_2 = three_back_2
                            updated = True
                        if not obj.two_back and two_back:
                            obj.two_back = two_back
                            updated = True
                        if updated:
                            obj.notes = (obj.notes or '') + f'\nUpdated from Sanook {draw_url} on {timezone.now().isoformat()}'
                            obj.save()
                            self.stdout.write(self.style.SUCCESS(f'▲ Updated: {draw_date}'))
                        else:
                            exists += 1
                            self.stdout.write(self.style.NOTICE(f'⊘ Exists: {draw_date}'))
                    else:
                        obj = LotteryDraw.objects.create(
                            draw_date=draw_date,
                            first_prize=first_prize,
                            three_front_1=three_front_1,
                            three_front_2=three_front_2,
                            three_back_1=three_back_1,
                            three_back_2=three_back_2,
                            two_back=two_back,
                            notes=f'Imported from Sanook {draw_url} on {timezone.now().isoformat()}'
                        )
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f'✓ Created: {draw_date} → {first_prize}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'✗ Failed {draw_date}: {e}'))
                failed += 1

        self.stdout.write('---')
        self.stdout.write(self.style.SUCCESS(f'Created: {created} | Exists: {exists} | Failed: {failed}'))
