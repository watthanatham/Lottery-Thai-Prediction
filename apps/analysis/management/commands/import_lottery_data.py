"""
Management command to import Thai Lottery draw data from CSV file.
Converts Buddhist calendar dates to Gregorian calendar.
"""
import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from apps.analysis.models import LotteryDraw


class Command(BaseCommand):
    help = 'Import Thai Lottery draw data from CSV file (Thai Buddhist calendar format)'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file containing lottery data'
        )

    def convert_buddhist_date_to_gregorian(self, date_str, buddhist_year):
        """
        Convert Thai Buddhist date to Gregorian calendar.
        Buddhist Year = Gregorian Year + 543
        So Gregorian Year = Buddhist Year - 543
        """
        try:
            # Parse date in DD/MM/YYYY format
            day, month, year_str = date_str.split('/')
            day = int(day)
            month = int(month)

            # Convert Buddhist year to Gregorian
            buddhist_year_int = int(buddhist_year)
            gregorian_year = buddhist_year_int - 543

            # Create the date
            date_obj = datetime(gregorian_year, month, day).date()
            return date_obj
        except (ValueError, IndexError) as e:
            raise ValueError(f"Error parsing date '{date_str}' with Buddhist year {buddhist_year}: {e}")

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                created_count = 0
                skipped_count = 0
                error_count = 0

                for row_num, row in enumerate(reader, start=2):  # start=2 because header is row 1
                    try:
                        # Extract data from CSV
                        date_str = row['วันที่ออกรางวัล'].strip()
                        buddhist_year = row['ปีพุทธศักราช'].strip()
                        first_prize = row['เลขรางวัลที่ 1 (6 หลัก)'].strip()
                        three_front_1 = row['เลขหน้า 3 ตัว 1'].strip()
                        three_front_2 = row['เลขหน้า 3 ตัว 2'].strip()
                        three_back_1 = row['เลขท้าย 3 ตัว 1'].strip()
                        three_back_2 = row['เลขท้าย 3 ตัว 2'].strip()
                        two_back = row['เลขท้าย 2 ตัว'].strip()

                        # Skip empty rows
                        if not date_str or not first_prize:
                            skipped_count += 1
                            continue

                        # Convert date
                        draw_date = self.convert_buddhist_date_to_gregorian(date_str, buddhist_year)

                        # Check if this draw already exists
                        if LotteryDraw.objects.filter(draw_date=draw_date).exists():
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Row {row_num}: Draw on {draw_date} already exists. Skipping."
                                )
                            )
                            skipped_count += 1
                            continue

                        # Create the LotteryDraw record
                        draw = LotteryDraw(
                            draw_date=draw_date,
                            first_prize=first_prize,
                            three_front_1=three_front_1,
                            three_front_2=three_front_2,
                            three_back_1=three_back_1,
                            three_back_2=three_back_2,
                            two_back=two_back,
                        )
                        draw.save()
                        created_count += 1

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Row {row_num}: {draw_date} — {first_prize}"
                            )
                        )

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"✗ Row {row_num}: Error - {str(e)}"
                            )
                        )

                # Summary
                self.stdout.write("\n" + "=" * 70)
                self.stdout.write(self.style.SUCCESS(f"Created: {created_count} draws"))
                if skipped_count > 0:
                    self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count} rows"))
                if error_count > 0:
                    self.stdout.write(self.style.ERROR(f"Errors: {error_count} rows"))
                self.stdout.write("=" * 70)

        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" not found.')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')
