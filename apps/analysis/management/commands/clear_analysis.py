"""
Management command to clear all analysis history and predictions.
Usage: python manage.py clear_analysis
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from apps.analysis.models import AnalysisSession, PredictionEntry


class Command(BaseCommand):
    help = 'ลบข้อมูลประวัติการวิเคราะห์ทั้งหมด (Analysis Sessions + Predictions) เพื่อเริ่มใหม่'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='ยืนยันการลบข้อมูล (ไม่ต้องถามซ้ำ)',
        )

    def handle(self, *args, **options):
        """Clear all analysis sessions and predictions."""

        # Count records before deletion
        session_count = AnalysisSession.objects.count()
        prediction_count = PredictionEntry.objects.count()

        if session_count == 0 and prediction_count == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ ไม่มีข้อมูลที่ต้องลบ (ระบบสะอาดอยู่แล้ว)')
            )
            return

        # Show what will be deleted
        self.stdout.write(
            self.style.WARNING(
                f'\n⚠️  จะลบข้อมูลดังต่อไปนี้:\n'
                f'  • Analysis Sessions (งวดวิเคราะห์): {session_count} งวด\n'
                f'  • Predictions (เลขที่ทำนาย): {prediction_count} เลข\n'
            )
        )

        # Confirm deletion
        if not options['confirm']:
            confirm = input('❓ ต้องการดำเนินการลบข้อมูลจริงหรือ? (yes/no): ')
            if confirm.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.SUCCESS('❌ ยกเลิกการลบข้อมูล'))
                return

        # Delete predictions first (they have FK to sessions)
        try:
            PredictionEntry.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✓ ลบ {prediction_count} เลขที่ทำนาย')
            )

            # Delete sessions
            AnalysisSession.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✓ ลบ {session_count} งวดวิเคราะห์')
            )

            self.stdout.write(
                self.style.SUCCESS(
                    '\n✅ เสร็จสมบูรณ์!\n'
                    '  ข้อมูลประวัติการวิเคราะห์ทั้งหมดได้ถูกลบแล้ว\n'
                    '  📝 ข้อมูลการออกรางวัล (Lottery Draws) ยังอยู่\n'
                    '  🚀 พร้อมวิเคราะห์ใหม่ได้แล้ว!\n'
                )
            )

        except Exception as e:
            raise CommandError(f'❌ เกิดข้อผิดพลาด: {str(e)}')
