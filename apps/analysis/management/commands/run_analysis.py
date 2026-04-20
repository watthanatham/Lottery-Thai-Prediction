from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime

from apps.analysis.models import LotteryDraw, FormulaConfig, AnalysisSession, PredictionEntry
from apps.analysis.formulas import FormulaEngine


class Command(BaseCommand):
    help = 'Run analysis programmatically (creates AnalysisSession and PredictionEntry rows)'

    def add_arguments(self, parser):
        parser.add_argument('--reference-id', type=int, help='Primary key of reference LotteryDraw')
        parser.add_argument('--reference-date', type=str, help='Reference draw date YYYY-MM-DD')
        parser.add_argument('--lottery-type', type=str, choices=['2D', '3D'], default='2D')
        parser.add_argument('--history-limit', type=int, default=50)

    def handle(self, *args, **options):
        ref_id = options.get('reference_id')
        ref_date = options.get('reference_date')
        lottery_type = options.get('lottery_type')
        history_limit = options.get('history_limit')

        # Resolve reference draw
        ref_draw = None
        if ref_id:
            try:
                ref_draw = LotteryDraw.objects.get(pk=ref_id)
            except LotteryDraw.DoesNotExist:
                raise CommandError(f'Reference draw id {ref_id} does not exist')
        elif ref_date:
            try:
                dt = datetime.strptime(ref_date, '%Y-%m-%d').date()
                ref_draw = LotteryDraw.objects.get(draw_date=dt)
            except Exception as e:
                raise CommandError(f'Could not find draw for date {ref_date}: {e}')
        else:
            ref_draw = LotteryDraw.objects.order_by('-draw_date').first()

        if not ref_draw:
            raise CommandError('No reference draw available. Insert LotteryDraw rows first.')

        # Pull historical draws up to and including reference draw
        all_draws = LotteryDraw.objects.filter(draw_date__lte=ref_draw.draw_date).order_by('draw_date')[:history_limit]

        numbers = []
        dates = []
        for d in all_draws:
            raw = d.get_number_for_type(lottery_type)
            if raw and raw.isdigit():
                numbers.append(int(raw))
                dates.append(datetime.combine(d.draw_date, datetime.min.time()))

        if len(numbers) < 3:
            raise CommandError('Not enough historical data (minimum 3 draws)')

        # Load formula configs
        formula_configs = FormulaConfig.objects.all()
        active_codes = {fc.formula_code for fc in formula_configs if fc.is_active}
        weights = {fc.formula_code: fc.weight for fc in formula_configs}

        num_digits = 2 if lottery_type == '2D' else 3
        engine = FormulaEngine(numbers=numbers, dates=dates, num_digits=num_digits)
        formula_results = engine.run_all(active_codes=active_codes, weights=weights)

        option_a = engine.aggregate_option_a(formula_results)
        option_b = engine.aggregate_option_b(formula_results)

        session = AnalysisSession.objects.create(
            reference_draw=ref_draw,
            lottery_type=lottery_type,
            target_draw_date=None,
            history_limit=len(numbers),
            formulas_run=len(formula_results),
            formulas_active=len(active_codes),
            formula_raw_results={k: v[:10] for k, v in formula_results.items()},
            option_a_results=option_a,
            option_b_results=option_b,
        )

        created = []
        for rank, (num_str, count) in enumerate(option_a, 1):
            pred = PredictionEntry.objects.create(
                session=session, option='A', rank=rank,
                number=num_str, frequency_count=int(count),
            )
            created.append(pred)
        for rank, (num_str, score) in enumerate(option_b, 1):
            pred = PredictionEntry.objects.create(
                session=session, option='B', rank=rank,
                number=num_str, ranking_score=float(score),
            )
            created.append(pred)

        self.stdout.write(self.style.SUCCESS(f'Created AnalysisSession id={session.pk} with {len(created)} predictions'))
        self.stdout.write('Option A:')
        for rank, (num, cnt) in enumerate(option_a, 1):
            self.stdout.write(f'  {rank}. {num} (count={cnt})')
        self.stdout.write('Option B:')
        for rank, (num, sc) in enumerate(option_b, 1):
            self.stdout.write(f'  {rank}. {num} (score={sc})')
