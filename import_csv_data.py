#!/usr/bin/env python
"""
Script to import Thai Lottery data from CSV file.
Run this from the project root: python import_csv_data.py <path_to_csv>

Example:
  python import_csv_data.py lottery_analysis_10years.csv
"""
import os
import sys
import csv
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_guide.settings')

import django
django.setup()

from apps.analysis.models import LotteryDraw


def convert_buddhist_to_gregorian(date_str, buddhist_year):
    """Convert Thai Buddhist calendar date to Gregorian calendar."""
    day, month, year_str = date_str.split('/')
    gregorian_year = int(buddhist_year) - 543
    return datetime(gregorian_year, int(month), int(day)).date()


def import_lottery_data(csv_file):
    """Import lottery data from CSV file."""
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        sys.exit(1)

    print(f"Importing lottery data from: {csv_file}")
    print("=" * 80)

    created = 0
    skipped = 0
    errors = 0

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                try:
                    date_str = row['วันที่ออกรางวัล'].strip()
                    buddhist_year = row['ปีพุทธศักราช'].strip()
                    first_prize = row['เลขรางวัลที่ 1 (6 หลัก)'].strip()

                    if not date_str or not first_prize:
                        skipped += 1
                        continue

                    # Convert date
                    draw_date = convert_buddhist_to_gregorian(date_str, buddhist_year)

                    # Check if exists
                    if LotteryDraw.objects.filter(draw_date=draw_date).exists():
                        print(f"Row {row_num}: {draw_date} — {first_prize} (skipped, already exists)")
                        skipped += 1
                        continue

                    # Create record
                    draw = LotteryDraw.objects.create(
                        draw_date=draw_date,
                        first_prize=first_prize,
                        three_front_1=row['เลขหน้า 3 ตัว 1'].strip(),
                        three_front_2=row['เลขหน้า 3 ตัว 2'].strip(),
                        three_back_1=row['เลขท้าย 3 ตัว 1'].strip(),
                        three_back_2=row['เลขท้าย 3 ตัว 2'].strip(),
                        two_back=row['เลขท้าย 2 ตัว'].strip(),
                    )
                    created += 1
                    print(f"Row {row_num}: ✓ {draw_date} — {first_prize}")

                except Exception as e:
                    errors += 1
                    print(f"Row {row_num}: ✗ Error - {str(e)}")

    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        sys.exit(1)

    print("=" * 80)
    print(f"Summary:")
    print(f"  Created: {created} draws")
    if skipped > 0:
        print(f"  Skipped: {skipped} rows")
    if errors > 0:
        print(f"  Errors:  {errors} rows")
    print("=" * 80)

    if created > 0:
        print("✓ Import completed successfully!")
    else:
        print("⚠ No new records were created.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_csv_data.py <path_to_csv_file>")
        print("\nExample:")
        print("  python import_csv_data.py lottery_analysis_10years.csv")
        sys.exit(1)

    csv_file = sys.argv[1]
    import_lottery_data(csv_file)
