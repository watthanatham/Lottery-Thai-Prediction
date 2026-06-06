"""
Walk-forward backtest for the lottery formulas.

For every historical draw (after a warm-up window) it rebuilds the engine using
ONLY the draws that came before it, generates predictions, and checks whether the
number that actually came out was inside the predicted set. This is the only
honest way to measure accuracy — it never lets a formula "see" the answer.

Every hit-rate is reported next to the RANDOM BASELINE (= picks / number_space).
A formula only has real predictive power if it beats that baseline by a margin
that is larger than statistical noise. For a fair lottery draw, none will.

Usage:
    python manage.py backtest
    python manage.py backtest --lottery-type 2D --top-n 10 --history-limit 50
    python manage.py backtest --per-formula           # also rank all 75 formulas
"""
import math
from datetime import datetime

from django.core.management.base import BaseCommand

from apps.analysis.models import LotteryDraw
from apps.analysis.formulas import FormulaEngine


TYPE_DIGITS = {'2D': 2, '3F': 3, '3B': 3}


class Command(BaseCommand):
    help = 'Walk-forward backtest of the formulas vs the random baseline.'

    def add_arguments(self, parser):
        parser.add_argument('--lottery-type', choices=['2D', '3F', '3B', 'ALL'], default='ALL')
        parser.add_argument('--top-n', type=int, default=10,
                            help='How many numbers each prediction set contains.')
        parser.add_argument('--history-limit', type=int, default=50,
                            help='How many prior draws each prediction may use.')
        parser.add_argument('--warmup', type=int, default=20,
                            help='Skip the first N draws (need history to predict).')
        parser.add_argument('--per-formula', action='store_true',
                            help='Also rank every individual formula by its top-5 hit-rate.')

    # ------------------------------------------------------------------ #
    def handle(self, *args, **opts):
        types = ['2D', '3F', '3B'] if opts['lottery_type'] == 'ALL' else [opts['lottery_type']]
        for ltype in types:
            self._backtest_type(ltype, opts)
            self.stdout.write('')

    # ------------------------------------------------------------------ #
    def _load_sequence(self, ltype):
        seq = []
        for d in LotteryDraw.objects.order_by('draw_date'):
            raw = d.get_number_for_type(ltype)
            if raw and raw.isdigit():
                seq.append((int(raw), datetime.combine(d.draw_date, datetime.min.time())))
        return seq

    def _backtest_type(self, ltype, opts):
        ndig = TYPE_DIGITS[ltype]
        top_n = opts['top_n']
        hist = opts['history_limit']
        warm = opts['warmup']
        space = 10 ** ndig
        baseline = top_n / space * 100.0

        seq = self._load_sequence(ltype)
        if len(seq) <= warm + 1:
            self.stdout.write(self.style.WARNING(
                f'{ltype}: not enough data ({len(seq)} draws, need > {warm + 1}).'))
            return

        hits = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        formula_hits = {}      # code -> hit count (actual in formula top-5)
        trials = 0

        for i in range(warm, len(seq)):
            window = seq[max(0, i - hist):i]
            nums = [x[0] for x in window]
            dates = [x[1] for x in window]
            actual = str(seq[i][0]).zfill(ndig)

            eng = FormulaEngine(numbers=nums, dates=dates, num_digits=ndig)
            fr = eng.run_all()

            sets = {
                'A': [n for n, _ in eng.aggregate_option_a(fr, top_n)],
                'B': [n for n, _ in eng.aggregate_option_b(fr, top_n)],
                'C': [n for n, _ in eng.aggregate_option_c_enhanced(fr, top_n)],
                'D': [n for n, _ in eng.aggregate_coverage(fr, top_n, ndig)],
            }
            for opt, picks in sets.items():
                if actual in picks:
                    hits[opt] += 1

            if opts['per_formula']:
                for code, results in fr.items():
                    top5 = [n for n, _ in results[:5]]
                    if actual in top5:
                        formula_hits[code] = formula_hits.get(code, 0) + 1

            trials += 1

        # ----- report ---------------------------------------------------
        self.stdout.write(self.style.HTTP_INFO(
            f'=== {ltype}  (digits={ndig}, space={space}, top_n={top_n}, '
            f'history={hist}, trials={trials}) ==='))
        self.stdout.write(f'  Random baseline (pick {top_n} of {space}): {baseline:.2f}%')

        names = {'A': 'Option A  Frequency', 'B': 'Option B  Ranking',
                 'C': 'Option C  Weighted', 'D': 'Option D  Coverage'}
        for opt in ('A', 'B', 'C', 'D'):
            pct = hits[opt] / trials * 100.0
            edge = pct - baseline
            margin = self._noise_margin(baseline, trials)
            verdict = self._verdict(edge, margin)
            self.stdout.write(
                f'  {names[opt]:<22} {hits[opt]:>3}/{trials}  = {pct:5.2f}%   '
                f'edge {edge:+5.2f}%  (+/-{margin:.2f}% noise)  {verdict}')

        if opts['per_formula'] and formula_hits:
            base5 = 5 / space * 100.0
            self.stdout.write('')
            self.stdout.write(f'  Per-formula top-5 hit-rate (baseline {base5:.2f}%):')
            ranked = sorted(formula_hits.items(), key=lambda x: -x[1])
            for code, h in ranked[:15]:
                pct = h / trials * 100.0
                self.stdout.write(f'    {code}  {h:>3}/{trials} = {pct:5.2f}%  edge {pct - base5:+5.2f}%')

    # ------------------------------------------------------------------ #
    @staticmethod
    def _noise_margin(baseline_pct, trials):
        """≈95% confidence half-width of pure-chance hit-rate, in percent."""
        p = baseline_pct / 100.0
        if trials <= 0:
            return 0.0
        se = math.sqrt(max(p * (1 - p), 1e-9) / trials)
        return 1.96 * se * 100.0

    @staticmethod
    def _verdict(edge, margin):
        if edge > margin:
            return '-> beats random'
        if edge < -margin:
            return '-> worse than random'
        return '-> same as random (noise)'
