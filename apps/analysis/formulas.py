"""
75 Lottery Analysis Formulas for Thai Government Lottery
=========================================================
Each formula takes historical draw data and returns a ranked list of
(number_string, score) tuples — highest score = most likely prediction.

Groups:
  F01–F10  Frequency Analysis
  F11–F20  Hot / Cold / Due
  F21–F30  Gap Analysis
  F31–F40  Digit Position Analysis
  F41–F50  Statistical Methods
  F51–F60  Pattern Recognition
  F61–F70  Time-Based Analysis
  F71–F75  Composite & Advanced

Aggregation:
  Option A — Top 5 by frequency: count how many formulas place a number
             in their top 5, pick the 5 with the highest count.
  Option B — Ranking Score: 1st=5 pts, 2nd=4 pts, 3rd=3 pts, 4th=2 pts,
             5th=1 pt across all formulas, pick top 5 by total score.
"""
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Tuple, Dict, Optional


Result = List[Tuple[str, float]]  # [(number_str, score), ...]


class FormulaEngine:
    # ------------------------------------------------------------------ #
    # Registry: code → {method_suffix, group, name, description}          #
    # ------------------------------------------------------------------ #
    FORMULA_REGISTRY: Dict[str, dict] = {
        'F01': {'suffix': 'raw_frequency',            'group': 'Frequency',   'name': 'Raw Frequency',               'description': 'Count how often each number appeared across all history'},
        'F02': {'suffix': 'recent_freq_10',           'group': 'Frequency',   'name': 'Recent Freq (10 draws)',       'description': 'Frequency count in the last 10 draws'},
        'F03': {'suffix': 'recent_freq_5',            'group': 'Frequency',   'name': 'Recent Freq (5 draws)',        'description': 'Frequency count in the last 5 draws'},
        'F04': {'suffix': 'recent_freq_3',            'group': 'Frequency',   'name': 'Recent Freq (3 draws)',        'description': 'Frequency count in the last 3 draws'},
        'F05': {'suffix': 'linear_weighted',          'group': 'Frequency',   'name': 'Linear Weighted Freq',         'description': 'Linear decay — recent draws weighted more'},
        'F06': {'suffix': 'exp_weighted',             'group': 'Frequency',   'name': 'Exponential Weighted Freq',    'description': 'Exponential decay weighting favouring recent draws'},
        'F07': {'suffix': 'odd_even_freq',            'group': 'Frequency',   'name': 'Odd/Even Frequency',           'description': 'Frequency within the favoured odd/even group by recent trend'},
        'F08': {'suffix': 'high_low_freq',            'group': 'Frequency',   'name': 'High/Low Frequency',           'description': 'Frequency within the favoured high/low group by recent trend'},
        'F09': {'suffix': 'digit_pair_freq',          'group': 'Frequency',   'name': 'Digit Pair Frequency',         'description': 'Frequency of digit-pair substrings in historical numbers'},
        'F10': {'suffix': 'digit_sum_freq',           'group': 'Frequency',   'name': 'Digit Sum Frequency',          'description': 'Numbers sharing the most common recent digit sum'},
        'F11': {'suffix': 'hot_numbers',              'group': 'Hot/Cold',    'name': 'Hot Numbers',                  'description': 'Numbers that appeared in the last 3 draws'},
        'F12': {'suffix': 'warm_numbers',             'group': 'Hot/Cold',    'name': 'Warm Numbers',                 'description': 'Numbers that appeared in the last 5 draws'},
        'F13': {'suffix': 'cold_numbers',             'group': 'Hot/Cold',    'name': 'Cold Numbers',                 'description': 'Numbers not seen in 10+ draws — overdue'},
        'F14': {'suffix': 'due_numbers',              'group': 'Hot/Cold',    'name': 'Due Numbers',                  'description': 'Ranked by longest gap since last appearance'},
        'F15': {'suffix': 'overdue_avg_gap',          'group': 'Hot/Cold',    'name': 'Overdue by Avg Gap',           'description': 'Current gap exceeds individual historical average gap'},
        'F16': {'suffix': 'hot_streak',               'group': 'Hot/Cold',    'name': 'Hot Streak',                   'description': 'Numbers with consecutive recent appearances'},
        'F17': {'suffix': 'cold_recovery',            'group': 'Hot/Cold',    'name': 'Cold Recovery',                'description': 'Cold numbers beginning to reappear after drought'},
        'F18': {'suffix': 'hot_cold_balance',         'group': 'Hot/Cold',    'name': 'Hot/Cold Balance',             'description': 'Balanced blend of hot frequency and cold due-ness'},
        'F19': {'suffix': 'thermal_score',            'group': 'Hot/Cold',    'name': 'Thermal Score',                'description': 'Composite temperature: recency × frequency'},
        'F20': {'suffix': 'thermal_regression',       'group': 'Hot/Cold',    'name': 'Thermal Regression',           'description': 'Numbers regressing toward their thermal equilibrium'},
        'F21': {'suffix': 'avg_gap_closeness',        'group': 'Gap',         'name': 'Avg Gap Closeness',            'description': 'Current gap vs average historical gap — near-due numbers'},
        'F22': {'suffix': 'min_gap',                  'group': 'Gap',         'name': 'Minimum Gap',                  'description': 'Numbers with smallest minimum gap (most frequent)'},
        'F23': {'suffix': 'max_gap_overdue',          'group': 'Gap',         'name': 'Max Gap Overdue',              'description': 'Current gap approaching the number\'s maximum historical gap'},
        'F24': {'suffix': 'gap_ratio',                'group': 'Gap',         'name': 'Gap Ratio',                    'description': 'Ratio of current gap to average gap — overdue indicator'},
        'F25': {'suffix': 'gap_consistency',          'group': 'Gap',         'name': 'Gap Consistency',              'description': 'Predictable appearance intervals (low std dev in gaps)'},
        'F26': {'suffix': 'gap_trend',                'group': 'Gap',         'name': 'Decreasing Gap Trend',         'description': 'Numbers appearing with increasing frequency over time'},
        'F27': {'suffix': 'overdue_prob',             'group': 'Gap',         'name': 'Overdue Probability',          'description': 'Geometric distribution probability based on current gap'},
        'F28': {'suffix': 'gap_percentile',           'group': 'Gap',         'name': 'Gap Percentile',               'description': 'Numbers in top percentile for overdue status'},
        'F29': {'suffix': 'gap_zscore',               'group': 'Gap',         'name': 'Gap Z-Score',                  'description': 'Z-score of current gap vs historical gap distribution'},
        'F30': {'suffix': 'multi_period_gap',         'group': 'Gap',         'name': 'Multi-Period Gap',             'description': 'Frequency trend comparison across multiple time windows'},
        'F31': {'suffix': 'units_digit_freq',         'group': 'Position',    'name': 'Units Digit Frequency',        'description': 'Rank by how hot the units (ones) digit has been'},
        'F32': {'suffix': 'tens_digit_freq',          'group': 'Position',    'name': 'Tens Digit Frequency',         'description': 'Rank by how hot the tens digit has been'},
        'F33': {'suffix': 'hundreds_digit_freq',      'group': 'Position',    'name': 'Hundreds Digit Frequency',     'description': 'Rank by how hot the hundreds digit has been (3-digit only)'},
        'F34': {'suffix': 'position_correlation',     'group': 'Position',    'name': 'Position Correlation',         'description': 'Numbers where all digit positions are simultaneously hot'},
        'F35': {'suffix': 'leading_digit',            'group': 'Position',    'name': 'Leading Digit Dominance',      'description': 'Numbers whose leading digit has been dominant'},
        'F36': {'suffix': 'trailing_digit',           'group': 'Position',    'name': 'Trailing Digit Pattern',       'description': 'Numbers whose trailing digit fits recent trailing patterns'},
        'F37': {'suffix': 'middle_digit',             'group': 'Position',    'name': 'Middle Digit Analysis',        'description': 'Middle digit frequency analysis (meaningful for 3-digit)'},
        'F38': {'suffix': 'position_weighted',        'group': 'Position',    'name': 'Position Weighted Score',      'description': 'Weighted combination of all digit-position frequencies'},
        'F39': {'suffix': 'position_hot_cold',        'group': 'Position',    'name': 'Position Hot/Cold',            'description': 'Hot/cold status evaluated per digit position'},
        'F40': {'suffix': 'cross_position_corr',      'group': 'Position',    'name': 'Cross-Position Correlation',   'description': 'Numbers whose digit-pair combinations co-occur frequently'},
        'F41': {'suffix': 'mean_deviation',           'group': 'Statistical', 'name': 'Mean Deviation',               'description': 'Numbers close to statistical mean expected frequency'},
        'F42': {'suffix': 'std_dev_scoring',          'group': 'Statistical', 'name': 'Std Dev Scoring',              'description': 'Numbers within 1σ of expected frequency'},
        'F43': {'suffix': 'zscore_ranking',           'group': 'Statistical', 'name': 'Z-Score Ranking',              'description': 'Frequency Z-score ranking — statistically over-performers'},
        'F44': {'suffix': 'percentile_score',         'group': 'Statistical', 'name': 'Percentile Score',             'description': 'Frequency percentile ranking across all possible numbers'},
        'F45': {'suffix': 'kde_estimate',             'group': 'Statistical', 'name': 'KDE Probability',              'description': 'Kernel density estimate of draw probability'},
        'F46': {'suffix': 'chi_square',               'group': 'Statistical', 'name': 'Chi-Square Residual',          'description': 'Numbers with significant chi-square residuals vs expected'},
        'F47': {'suffix': 'expected_vs_actual',       'group': 'Statistical', 'name': 'Expected vs Actual',           'description': 'Numbers underperforming expected frequency — due to correct'},
        'F48': {'suffix': 'confidence_interval',      'group': 'Statistical', 'name': 'Confidence Interval',          'description': 'Numbers inside the 95% CI for expected frequency'},
        'F49': {'suffix': 'regression_to_mean',       'group': 'Statistical', 'name': 'Regression to Mean',           'description': 'Numbers expected to regress toward mean frequency'},
        'F50': {'suffix': 'variance_stability',       'group': 'Statistical', 'name': 'Variance Stability',           'description': 'Consistently performing numbers across sub-periods'},
        'F51': {'suffix': 'mirror_numbers',           'group': 'Pattern',     'name': 'Mirror Numbers',               'description': 'Mirror pairs (12↔21): predict mirror after partner appears'},
        'F52': {'suffix': 'reverse_digit',            'group': 'Pattern',     'name': 'Reverse Digit Pattern',        'description': 'Numbers whose reverse appears in recent draws'},
        'F53': {'suffix': 'consecutive_seq',          'group': 'Pattern',     'name': 'Consecutive Sequence',         'description': 'Numbers in arithmetic step with recent results'},
        'F54': {'suffix': 'same_digit_pairs',         'group': 'Pattern',     'name': 'Same-Digit Pairs / Triples',   'description': 'Double / triple digit numbers (11, 22, 111…)'},
        'F55': {'suffix': 'adjacent_digits',          'group': 'Pattern',     'name': 'Adjacent Digit Numbers',       'description': 'Numbers whose digits are adjacent in value (12, 23, 89…)'},
        'F56': {'suffix': 'sum_cluster',              'group': 'Pattern',     'name': 'Digit Sum Cluster',            'description': 'Numbers sharing the digit-sum cluster of recent winners'},
        'F57': {'suffix': 'digit_diff_pattern',       'group': 'Pattern',     'name': 'Digit Difference Pattern',     'description': 'Numbers whose delta from last draw matches historical avg delta'},
        'F58': {'suffix': 'odd_even_ratio',           'group': 'Pattern',     'name': 'Odd/Even Ratio Match',         'description': 'Score reflects the odd/even ratio trend of recent draws'},
        'F59': {'suffix': 'high_low_ratio',           'group': 'Pattern',     'name': 'High/Low Ratio Match',         'description': 'Score reflects the high/low ratio trend of recent draws'},
        'F60': {'suffix': 'pattern_recurrence',       'group': 'Pattern',     'name': 'Pattern Recurrence',           'description': 'Numbers frequently following recently drawn numbers'},
        'F61': {'suffix': 'same_period',              'group': 'Time',        'name': 'Same Draw Period',             'description': 'Numbers that perform well on same-period draws (1st/16th)'},
        'F62': {'suffix': 'seasonal_freq',            'group': 'Time',        'name': 'Seasonal Frequency',           'description': 'Numbers performing well in the current quarter / season'},
        'F63': {'suffix': 'year_freq',                'group': 'Time',        'name': 'Year-Based Frequency',         'description': 'Numbers performing well in the current calendar year'},
        'F64': {'suffix': 'month_cluster',            'group': 'Time',        'name': 'Month Clustering',             'description': 'Numbers that cluster by calendar month'},
        'F65': {'suffix': 'draw_periodicity',         'group': 'Time',        'name': 'Draw Periodicity',             'description': 'Numbers appearing at regular periodic intervals'},
        'F66': {'suffix': 'cyclic_pattern',           'group': 'Time',        'name': 'Cyclic Pattern',               'description': 'Cyclic appearance detection via autocorrelation'},
        'F67': {'suffix': 'long_term_trend',          'group': 'Time',        'name': 'Long-Term Trend',              'description': 'Numbers with a rising long-term appearance trend'},
        'F68': {'suffix': 'short_term_momentum',      'group': 'Time',        'name': 'Short-Term Momentum',          'description': 'Numbers accelerating in frequency over the short term'},
        'F69': {'suffix': 'recency_bias_corr',        'group': 'Time',        'name': 'Recency Bias Correction',      'description': 'Corrects for recency bias — surfaces neglected frequent numbers'},
        'F70': {'suffix': 'time_decay_weighted',      'group': 'Time',        'name': 'Time-Decay Weighted',          'description': 'Exponential time-decay score across full history'},
        'F71': {'suffix': 'fibonacci_resonance',      'group': 'Composite',   'name': 'Fibonacci Resonance',          'description': 'Numbers near Fibonacci sequence values'},
        'F72': {'suffix': 'prime_weighting',          'group': 'Composite',   'name': 'Prime Number Weighting',       'description': 'Applies extra weight to prime numbers based on recent prime trend'},
        'F73': {'suffix': 'golden_ratio',             'group': 'Composite',   'name': 'Golden Ratio Proximity',       'description': 'Numbers near golden-ratio-derived predictions from recent draws'},
        'F74': {'suffix': 'ensemble_consensus',       'group': 'Composite',   'name': 'Ensemble Consensus',           'description': 'Voting consensus across a diverse sub-set of formulas'},
        'F75': {'suffix': 'adaptive_composite',       'group': 'Composite',   'name': 'Adaptive Composite',           'description': 'Adaptive weighted blend: frequency + gap + position + statistics'},
    }

    # ------------------------------------------------------------------ #
    # Constructor                                                          #
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        numbers: List[int],
        dates: Optional[List[datetime]] = None,
        num_digits: int = 2,
    ):
        self.numbers = numbers                        # historical draws as ints
        self.dates = dates or []
        self.num_digits = num_digits
        self.max_val = 99 if num_digits == 2 else 999
        self.all_nums = list(range(self.max_val + 1))
        self.counter = Counter(numbers)
        self.n = len(numbers)
        self.expected_freq = self.n / (self.max_val + 1)

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #
    def _fmt(self, n: int) -> str:
        return str(n).zfill(self.num_digits)

    def _rank(self, scores: Dict[int, float]) -> Result:
        return [(self._fmt(k), v)
                for k, v in sorted(scores.items(), key=lambda x: -x[1])]

    def _last_n(self, n: int) -> List[int]:
        return self.numbers[-n:] if self.n >= n else self.numbers[:]

    def _current_gap(self, num: int) -> int:
        for i, x in enumerate(reversed(self.numbers)):
            if x == num:
                return i
        return self.n + 1

    def _gaps(self, num: int) -> List[int]:
        pos = [i for i, x in enumerate(self.numbers) if x == num]
        return [pos[i + 1] - pos[i] for i in range(len(pos) - 1)]

    def _safe_std(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        avg = sum(values) / len(values)
        return math.sqrt(sum((v - avg) ** 2 for v in values) / len(values))

    def _linear_slope(self, values: List[float]) -> float:
        n = len(values)
        if n < 2:
            return 0.0
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        den = sum((i - x_mean) ** 2 for i in range(n))
        return num / den if den else 0.0

    # ================================================================== #
    # GROUP 1 — FREQUENCY ANALYSIS (F01–F10)                             #
    # ================================================================== #
    def F01_raw_frequency(self) -> Result:
        return self._rank({n: self.counter.get(n, 0) for n in self.all_nums})

    def F02_recent_freq_10(self) -> Result:
        c = Counter(self._last_n(10))
        return self._rank({n: c.get(n, 0) for n in self.all_nums})

    def F03_recent_freq_5(self) -> Result:
        c = Counter(self._last_n(5))
        return self._rank({n: c.get(n, 0) for n in self.all_nums})

    def F04_recent_freq_3(self) -> Result:
        c = Counter(self._last_n(3))
        return self._rank({n: c.get(n, 0) for n in self.all_nums})

    def F05_linear_weighted(self) -> Result:
        scores: Dict[int, float] = defaultdict(float)
        for i, num in enumerate(self.numbers):
            scores[num] += (i + 1) / max(self.n, 1)
        return self._rank({n: scores.get(n, 0.0) for n in self.all_nums})

    def F06_exp_weighted(self) -> Result:
        scores: Dict[int, float] = defaultdict(float)
        decay = 0.95
        for i, num in enumerate(self.numbers):
            scores[num] += decay ** (self.n - i - 1)
        return self._rank({n: scores.get(n, 0.0) for n in self.all_nums})

    def F07_odd_even_freq(self) -> Result:
        recent = self._last_n(10)
        odd_c = sum(1 for x in recent if x % 2 == 1)
        favor_odd = odd_c < len(recent) / 2   # favour the less-frequent parity
        scores = {}
        for n in self.all_nums:
            base = self.counter.get(n, 0)
            bonus = 1.5 if (n % 2 == 1) == favor_odd else 1.0
            scores[n] = base * bonus
        return self._rank(scores)

    def F08_high_low_freq(self) -> Result:
        mid = self.max_val // 2
        recent = self._last_n(10)
        high_c = sum(1 for x in recent if x > mid)
        favor_high = high_c < len(recent) / 2
        scores = {}
        for n in self.all_nums:
            base = self.counter.get(n, 0)
            bonus = 1.5 if (n > mid) == favor_high else 1.0
            scores[n] = base * bonus
        return self._rank(scores)

    def F09_digit_pair_freq(self) -> Result:
        # Build pair frequency table from history
        pair_cnt: Counter = Counter()
        for x in self.numbers:
            s = str(x).zfill(self.num_digits)
            for j in range(len(s) - 1):
                pair_cnt[s[j:j + 2]] += 1
        scores = {}
        for n in self.all_nums:
            s = str(n).zfill(self.num_digits)
            scores[n] = sum(pair_cnt[s[j:j + 2]] for j in range(len(s) - 1))
        return self._rank(scores)

    def F10_digit_sum_freq(self) -> Result:
        recent = self._last_n(10)
        digit_sum = lambda x: sum(int(d) for d in str(x).zfill(self.num_digits))
        if not recent:
            return self._rank({n: 0 for n in self.all_nums})
        target = Counter(digit_sum(x) for x in recent).most_common(1)[0][0]
        scores = {}
        for n in self.all_nums:
            diff = abs(digit_sum(n) - target)
            scores[n] = max(0, 5 - diff) + self.counter.get(n, 0) * 0.1
        return self._rank(scores)

    # ================================================================== #
    # GROUP 2 — HOT / COLD / DUE (F11–F20)                              #
    # ================================================================== #
    def F11_hot_numbers(self) -> Result:
        hot = set(self._last_n(3))
        return self._rank({n: self.counter.get(n, 0) * (3.0 if n in hot else 1.0)
                           for n in self.all_nums})

    def F12_warm_numbers(self) -> Result:
        warm = set(self._last_n(5))
        return self._rank({n: self.counter.get(n, 0) * (2.0 if n in warm else 1.0)
                           for n in self.all_nums})

    def F13_cold_numbers(self) -> Result:
        recent_10 = set(self._last_n(10))
        scores = {}
        for n in self.all_nums:
            gap = self._current_gap(n)
            cold_bonus = gap / 10.0 if n not in recent_10 else 0
            scores[n] = self.counter.get(n, 0) + cold_bonus
        return self._rank(scores)

    def F14_due_numbers(self) -> Result:
        return self._rank({n: self._current_gap(n) for n in self.all_nums})

    def F15_overdue_avg_gap(self) -> Result:
        scores = {}
        for n in self.all_nums:
            gaps = self._gaps(n)
            current = self._current_gap(n)
            if gaps:
                avg = sum(gaps) / len(gaps)
                scores[n] = max(0.0, current - avg)
            else:
                scores[n] = current * 0.5
        return self._rank(scores)

    def F16_hot_streak(self) -> Result:
        scores = {}
        for n in self.all_nums:
            streak = 0
            for x in reversed(self.numbers):
                if x == n:
                    streak += 1
                else:
                    break
            scores[n] = streak * 3 + self.counter.get(n, 0)
        return self._rank(scores)

    def F17_cold_recovery(self) -> Result:
        scores = {}
        recent_5 = self._last_n(5)
        recent_20 = self._last_n(20)
        for n in self.all_nums:
            f5 = recent_5.count(n)
            f20 = recent_20.count(n) / max(len(recent_20), 1) * 5
            scores[n] = f5 * 2 if f5 > 0 and f20 < f5 else 0
            scores[n] += self.counter.get(n, 0) * 0.1
        return self._rank(scores)

    def F18_hot_cold_balance(self) -> Result:
        hot = dict(self.F11_hot_numbers())
        due = dict(self.F14_due_numbers())
        max_h = max((float(v) for v in hot.values()), default=1) or 1
        max_d = max((float(v) for v in due.values()), default=1) or 1
        scores = {}
        for n in self.all_nums:
            s = self._fmt(n)
            scores[n] = (float(hot.get(s, 0)) / max_h) * 0.5 + (float(due.get(s, 0)) / max_d) * 0.5
        return self._rank(scores)

    def F19_thermal_score(self) -> Result:
        scores = {}
        for n in self.all_nums:
            gap = self._current_gap(n)
            recency = max(0, 20 - gap) / 20.0
            freq_ratio = self.counter.get(n, 0) / max(self.expected_freq, 0.001)
            scores[n] = recency * 0.4 + freq_ratio * 0.6
        return self._rank(scores)

    def F20_thermal_regression(self) -> Result:
        scores = {}
        for n in self.all_nums:
            freq = self.counter.get(n, 0)
            gap = self._current_gap(n)
            deviation = abs(freq - self.expected_freq)
            recency_penalty = gap / max(self.n, 1)
            scores[n] = deviation * (1 - recency_penalty) + freq * 0.1
        return self._rank(scores)

    # ================================================================== #
    # GROUP 3 — GAP ANALYSIS (F21–F30)                                   #
    # ================================================================== #
    def F21_avg_gap_closeness(self) -> Result:
        scores = {}
        for n in self.all_nums:
            gaps = self._gaps(n)
            current = self._current_gap(n)
            if gaps:
                avg = sum(gaps) / len(gaps)
                scores[n] = max(0, 10 - abs(current - avg))
            else:
                scores[n] = 0
        return self._rank(scores)

    def F22_min_gap(self) -> Result:
        scores = {}
        for n in self.all_nums:
            gaps = self._gaps(n)
            scores[n] = 1.0 / (min(gaps) + 1) if gaps else 0
        return self._rank(scores)

    def F23_max_gap_overdue(self) -> Result:
        scores = {}
        for n in self.all_nums:
            gaps = self._gaps(n)
            current = self._current_gap(n)
            if gaps:
                scores[n] = current / max(max(gaps), 1)
            else:
                scores[n] = 0
        return self._rank(scores)

    def F24_gap_ratio(self) -> Result:
        scores = {}
        for n in self.all_nums:
            gaps = self._gaps(n)
            current = self._current_gap(n)
            if gaps:
                avg = sum(gaps) / len(gaps)
                scores[n] = current / max(avg, 1)
            else:
                scores[n] = current / max(self.n, 1)
        return self._rank(scores)

    def F25_gap_consistency(self) -> Result:
        scores = {}
        for n in self.all_nums:
            gaps = self._gaps(n)
            if len(gaps) >= 2:
                avg = sum(gaps) / len(gaps)
                std = self._safe_std([float(g) for g in gaps])
                current = self._current_gap(n)
                consistency = max(0, 10 - std)
                closeness = max(0, 5 - abs(current - avg))
                scores[n] = consistency * closeness
            else:
                scores[n] = 0
        return self._rank(scores)

    def F26_gap_trend(self) -> Result:
        scores = {}
        for n in self.all_nums:
            gaps = self._gaps(n)
            if len(gaps) >= 3:
                slope = self._linear_slope([float(g) for g in gaps])
                scores[n] = max(0, -slope)   # negative slope = gap shrinking = good
            else:
                scores[n] = 0
        return self._rank(scores)

    def F27_overdue_prob(self) -> Result:
        # P(appears at least once in `gap` draws) = 1 - (1-p)^gap, increases with gap
        p = 1.0 / (self.max_val + 1)
        scores = {n: (1 - (1 - p) ** max(self._current_gap(n), 1)) * 100
                  for n in self.all_nums}
        return self._rank(scores)

    def F28_gap_percentile(self) -> Result:
        all_gaps = {n: self._current_gap(n) for n in self.all_nums}
        max_gap = max(all_gaps.values()) or 1
        return self._rank({n: g / max_gap for n, g in all_gaps.items()})

    def F29_gap_zscore(self) -> Result:
        scores = {}
        for n in self.all_nums:
            gaps = self._gaps(n)
            current = self._current_gap(n)
            if len(gaps) >= 2:
                avg = sum(gaps) / len(gaps)
                std = self._safe_std([float(g) for g in gaps])
                scores[n] = max(0, (current - avg) / max(std, 1))
            else:
                scores[n] = 0
        return self._rank(scores)

    def F30_multi_period_gap(self) -> Result:
        periods = [5, 10, 20, 50]
        scores = {}
        for n in self.all_nums:
            period_rates = [self._last_n(p).count(n) / p for p in periods if self.n >= p]
            if len(period_rates) >= 2:
                trend = sum(period_rates[-2:]) / 2 - sum(period_rates[:2]) / 2
                scores[n] = max(0, trend) * 100 + self.counter.get(n, 0)
            else:
                scores[n] = self.counter.get(n, 0)
        return self._rank(scores)

    # ================================================================== #
    # GROUP 4 — DIGIT POSITION ANALYSIS (F31–F40)                        #
    # ================================================================== #
    def F31_units_digit_freq(self) -> Result:
        uf = Counter(x % 10 for x in self.numbers)
        return self._rank({n: uf.get(n % 10, 0) for n in self.all_nums})

    def F32_tens_digit_freq(self) -> Result:
        tf = Counter((x // 10) % 10 for x in self.numbers)
        return self._rank({n: tf.get((n // 10) % 10, 0) for n in self.all_nums})

    def F33_hundreds_digit_freq(self) -> Result:
        if self.num_digits < 3:
            return self._rank({n: self.counter.get(n, 0) for n in self.all_nums})
        hf = Counter(x // 100 for x in self.numbers)
        return self._rank({n: hf.get(n // 100, 0) for n in self.all_nums})

    def F34_position_correlation(self) -> Result:
        uf = Counter(x % 10 for x in self.numbers)
        tf = Counter((x // 10) % 10 for x in self.numbers)
        hf = Counter(x // 100 for x in self.numbers) if self.num_digits == 3 else Counter()
        scores = {}
        for n in self.all_nums:
            u = uf.get(n % 10, 0)
            t = tf.get((n // 10) % 10, 0)
            h = hf.get(n // 100, 0) if self.num_digits == 3 else 0
            scores[n] = (u + t + h) / self.num_digits
        return self._rank(scores)

    def F35_leading_digit(self) -> Result:
        lf = Counter(int(str(x).zfill(self.num_digits)[0]) for x in self.numbers)
        return self._rank({n: lf.get(int(str(n).zfill(self.num_digits)[0]), 0) for n in self.all_nums})

    def F36_trailing_digit(self) -> Result:
        tf = Counter(x % 10 for x in self._last_n(10))
        scores = {}
        for n in self.all_nums:
            base = tf.get(n % 10, 0)
            if self.numbers:
                dist = abs((n % 10) - (self.numbers[-1] % 10))
                base += max(0, 5 - dist) * 0.5
            scores[n] = base
        return self._rank(scores)

    def F37_middle_digit(self) -> Result:
        if self.num_digits == 3:
            mf = Counter((x // 10) % 10 for x in self.numbers)
            return self._rank({n: mf.get((n // 10) % 10, 0) for n in self.all_nums})
        # For 2-digit, rank by sum of both digits
        sf = Counter((x // 10 + x % 10) for x in self.numbers)
        return self._rank({n: sf.get(n // 10 + n % 10, 0) for n in self.all_nums})

    def F38_position_weighted(self) -> Result:
        uf = Counter(x % 10 for x in self.numbers)
        tf = Counter((x // 10) % 10 for x in self.numbers)
        hf = Counter(x // 100 for x in self.numbers) if self.num_digits == 3 else Counter()
        scores = {}
        for n in self.all_nums:
            if self.num_digits == 3:
                scores[n] = (uf.get(n % 10, 0) * 0.4
                             + tf.get((n // 10) % 10, 0) * 0.3
                             + hf.get(n // 100, 0) * 0.3)
            else:
                scores[n] = uf.get(n % 10, 0) * 0.5 + tf.get((n // 10) % 10, 0) * 0.5
        return self._rank(scores)

    def F39_position_hot_cold(self) -> Result:
        recent = self._last_n(10)
        uf = Counter(x % 10 for x in recent)
        tf = Counter((x // 10) % 10 for x in recent)
        return self._rank({n: uf.get(n % 10, 0) + tf.get((n // 10) % 10, 0)
                           for n in self.all_nums})

    def F40_cross_position_corr(self) -> Result:
        pair_cnt: Counter = Counter()
        for x in self.numbers:
            s = str(x).zfill(self.num_digits)
            for i in range(len(s)):
                for j in range(i + 1, len(s)):
                    pair_cnt[(i, int(s[i]), j, int(s[j]))] += 1
        scores = {}
        for n in self.all_nums:
            s = str(n).zfill(self.num_digits)
            score = 0
            for i in range(len(s)):
                for j in range(i + 1, len(s)):
                    score += pair_cnt.get((i, int(s[i]), j, int(s[j])), 0)
            scores[n] = score
        return self._rank(scores)

    # ================================================================== #
    # GROUP 5 — STATISTICAL METHODS (F41–F50)                            #
    # ================================================================== #
    def F41_mean_deviation(self) -> Result:
        scores = {}
        for n in self.all_nums:
            freq = self.counter.get(n, 0)
            scores[n] = max(0, 10 - abs(freq - self.expected_freq)) + freq * 0.1
        return self._rank(scores)

    def F42_std_dev_scoring(self) -> Result:
        freqs = [self.counter.get(n, 0) for n in self.all_nums]
        mean = sum(freqs) / len(freqs)
        std = self._safe_std([float(f) for f in freqs]) or 1
        scores = {}
        for n in self.all_nums:
            freq = self.counter.get(n, 0)
            z = abs(freq - mean) / std
            scores[n] = max(0, 3 - z) * freq
        return self._rank(scores)

    def F43_zscore_ranking(self) -> Result:
        freqs = [self.counter.get(n, 0) for n in self.all_nums]
        mean = sum(freqs) / len(freqs)
        std = self._safe_std([float(f) for f in freqs]) or 1
        return self._rank({n: (self.counter.get(n, 0) - mean) / std for n in self.all_nums})

    def F44_percentile_score(self) -> Result:
        sorted_freqs = sorted(self.counter.get(n, 0) for n in self.all_nums)
        total = len(sorted_freqs)
        scores = {}
        for n in self.all_nums:
            freq = self.counter.get(n, 0)
            pct = sum(1 for f in sorted_freqs if f <= freq) / total
            scores[n] = pct * 100
        return self._rank(scores)

    def F45_kde_estimate(self) -> Result:
        if not self.numbers:
            return self._rank({n: 0 for n in self.all_nums})
        bw = max(1.0, (self.max_val + 1) / 20.0)
        scores = {n: sum(math.exp(-0.5 * ((n - x) / bw) ** 2) for x in self.numbers)
                  for n in self.all_nums}
        return self._rank(scores)

    def F46_chi_square(self) -> Result:
        scores = {}
        for n in self.all_nums:
            obs = self.counter.get(n, 0)
            exp = max(self.expected_freq, 0.001)
            scores[n] = (obs - exp) ** 2 / exp + obs * 0.1
        return self._rank(scores)

    def F47_expected_vs_actual(self) -> Result:
        scores = {}
        for n in self.all_nums:
            deficit = max(0.0, self.expected_freq - self.counter.get(n, 0))
            scores[n] = deficit + self.counter.get(n, 0) * 0.05
        return self._rank(scores)

    def F48_confidence_interval(self) -> Result:
        freqs = [self.counter.get(n, 0) for n in self.all_nums]
        mean = sum(freqs) / len(freqs)
        std = self._safe_std([float(f) for f in freqs])
        lo, hi = mean - 1.96 * std, mean + 1.96 * std
        scores = {}
        for n in self.all_nums:
            freq = self.counter.get(n, 0)
            scores[n] = freq * (2.0 if lo <= freq <= hi else 0.5)
        return self._rank(scores)

    def F49_regression_to_mean(self) -> Result:
        freqs = [self.counter.get(n, 0) for n in self.all_nums]
        mean = sum(freqs) / len(freqs)
        scores = {}
        for n in self.all_nums:
            deficit = max(0.0, mean - self.counter.get(n, 0))
            scores[n] = deficit + self.counter.get(n, 0) * 0.2
        return self._rank(scores)

    def F50_variance_stability(self) -> Result:
        period = max(10, self.n // 5)
        scores = {}
        for n in self.all_nums:
            pf = [self.numbers[i:i + period].count(n) / period
                  for i in range(0, self.n, period)]
            if len(pf) >= 2:
                avg = sum(pf) / len(pf)
                var = self._safe_std(pf) ** 2
                scores[n] = avg * max(0, 10 - var * 100)
            else:
                scores[n] = self.counter.get(n, 0)
        return self._rank(scores)

    # ================================================================== #
    # GROUP 6 — PATTERN RECOGNITION (F51–F60)                            #
    # ================================================================== #
    def F51_mirror_numbers(self) -> Result:
        recent_10 = set(self._last_n(10))
        scores = {}
        for n in self.all_nums:
            mirror = int(str(n).zfill(self.num_digits)[::-1])
            scores[n] = self.counter.get(n, 0) + (5 if mirror in recent_10 and mirror != n else 0)
        return self._rank(scores)

    def F52_reverse_digit(self) -> Result:
        if not self.numbers:
            return self._rank({n: 0 for n in self.all_nums})
        last_rev = int(str(self.numbers[-1]).zfill(self.num_digits)[::-1])
        scores = {}
        for n in self.all_nums:
            scores[n] = max(0, 20 - abs(n - last_rev)) + self.counter.get(n, 0)
        return self._rank(scores)

    def F53_consecutive_seq(self) -> Result:
        recent = self._last_n(5)
        scores = {}
        for n in self.all_nums:
            seq_score = sum(max(0, 10 - abs(n - p)) for p in recent if abs(n - p) in [1, 2, 5, 10, 11])
            scores[n] = seq_score + self.counter.get(n, 0) * 0.5
        return self._rank(scores)

    def F54_same_digit_pairs(self) -> Result:
        repeat_trend = sum(1 for x in self._last_n(10) if len(set(str(x).zfill(self.num_digits))) <= 2)
        scores = {}
        for n in self.all_nums:
            s = str(n).zfill(self.num_digits)
            base = self.counter.get(n, 0)
            if len(set(s)) == 1:
                scores[n] = base * 2 + repeat_trend * 2
            elif len(set(s)) == 2:
                scores[n] = base * 1.5 + repeat_trend
            else:
                scores[n] = base
        return self._rank(scores)

    def F55_adjacent_digits(self) -> Result:
        scores = {}
        for n in self.all_nums:
            s = str(n).zfill(self.num_digits)
            max_diff = max(abs(int(s[i]) - int(s[i + 1])) for i in range(len(s) - 1))
            base = self.counter.get(n, 0)
            scores[n] = base * (1.8 if max_diff <= 1 else 1.3 if max_diff <= 2 else 1.0)
        return self._rank(scores)

    def F56_sum_cluster(self) -> Result:
        recent = self._last_n(5)
        if not recent:
            return self._rank({n: 0 for n in self.all_nums})
        digit_sum = lambda x: sum(int(d) for d in str(x).zfill(self.num_digits))
        target_sums = {digit_sum(x) for x in recent}
        scores = {}
        for n in self.all_nums:
            ds = digit_sum(n)
            base = self.counter.get(n, 0)
            if ds in target_sums:
                scores[n] = base * 2 + 5
            elif any(abs(ds - s) <= 1 for s in target_sums):
                scores[n] = base * 1.5 + 2
            else:
                scores[n] = base
        return self._rank(scores)

    def F57_digit_diff_pattern(self) -> Result:
        if len(self.numbers) < 2:
            return self._rank({n: self.counter.get(n, 0) for n in self.all_nums})
        diffs = [abs(self.numbers[i + 1] - self.numbers[i]) for i in range(len(self.numbers) - 1)]
        avg_diff = sum(diffs[-5:]) / max(len(diffs[-5:]), 1)
        last = self.numbers[-1]
        scores = {}
        for n in self.all_nums:
            closeness = max(0, 10 - abs(abs(n - last) - avg_diff))
            scores[n] = closeness + self.counter.get(n, 0) * 0.3
        return self._rank(scores)

    def F58_odd_even_ratio(self) -> Result:
        recent = self._last_n(10)
        odd_ratio = sum(1 for x in recent if x % 2 == 1) / max(len(recent), 1)
        scores = {}
        for n in self.all_nums:
            base = self.counter.get(n, 0)
            scores[n] = base * (1 + odd_ratio if n % 2 == 1 else 1 + (1 - odd_ratio))
        return self._rank(scores)

    def F59_high_low_ratio(self) -> Result:
        mid = self.max_val // 2
        recent = self._last_n(10)
        high_ratio = sum(1 for x in recent if x > mid) / max(len(recent), 1)
        scores = {}
        for n in self.all_nums:
            base = self.counter.get(n, 0)
            scores[n] = base * (1 + high_ratio if n > mid else 1 + (1 - high_ratio))
        return self._rank(scores)

    def F60_pattern_recurrence(self) -> Result:
        if len(self.numbers) < 10:
            return self._rank({n: self.counter.get(n, 0) for n in self.all_nums})
        recent = set(self._last_n(5))
        trans: Counter = Counter()
        for i in range(len(self.numbers) - 1):
            trans[self.numbers[i + 1]] += 1
            if self.numbers[i] in recent:
                trans[self.numbers[i + 1]] += 2
        return self._rank({n: trans.get(n, 0) + self.counter.get(n, 0) * 0.1
                           for n in self.all_nums})

    # ================================================================== #
    # GROUP 7 — TIME-BASED ANALYSIS (F61–F70)                            #
    # ================================================================== #
    def F61_same_period(self) -> Result:
        if not self.dates:
            return self.F01_raw_frequency()
        latest_day = self.dates[-1].day if self.dates else 1
        next_is_first = latest_day > 15
        period_nums = [x for x, d in zip(self.numbers, self.dates) if (d.day <= 15) == next_is_first]
        c = Counter(period_nums)
        return self._rank({n: c.get(n, 0) for n in self.all_nums})

    def F62_seasonal_freq(self) -> Result:
        if not self.dates:
            return self.F01_raw_frequency()
        cur_q = (datetime.now().month - 1) // 3
        seasonal = [x for x, d in zip(self.numbers, self.dates) if (d.month - 1) // 3 == cur_q]
        c = Counter(seasonal)
        return self._rank({n: c.get(n, 0) * 2 + self.counter.get(n, 0) for n in self.all_nums})

    def F63_year_freq(self) -> Result:
        if not self.dates:
            return self.F01_raw_frequency()
        cur_y = datetime.now().year
        year_nums = [x for x, d in zip(self.numbers, self.dates) if d.year == cur_y]
        c = Counter(year_nums)
        return self._rank({n: c.get(n, 0) * 3 + self.counter.get(n, 0) for n in self.all_nums})

    def F64_month_cluster(self) -> Result:
        if not self.dates:
            return self.F01_raw_frequency()
        cur_m = datetime.now().month
        month_nums = [x for x, d in zip(self.numbers, self.dates) if d.month == cur_m]
        c = Counter(month_nums)
        return self._rank({n: c.get(n, 0) * 2 + self.counter.get(n, 0) for n in self.all_nums})

    def F65_draw_periodicity(self) -> Result:
        scores = {}
        for n in self.all_nums:
            positions = [i for i, x in enumerate(self.numbers) if x == n]
            if len(positions) >= 3:
                diffs = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
                avg_p = sum(diffs) / len(diffs)
                std_p = self._safe_std([float(d) for d in diffs])
                consistency = max(0, 10 - std_p)
                current = self._current_gap(n)
                remainder = current % max(avg_p, 1)
                closeness = max(0, 5 - abs(remainder - avg_p / 2))
                scores[n] = consistency * closeness
            else:
                scores[n] = 0
        return self._rank(scores)

    def F66_cyclic_pattern(self) -> Result:
        scores = {}
        for n in self.all_nums:
            binary = [1 if x == n else 0 for x in self.numbers]
            if sum(binary) < 3:
                scores[n] = 0
                continue
            cycle_score = 0
            for cl in [5, 10, 15, 20, 24]:
                if len(binary) < cl * 2:
                    continue
                cycle_score += sum(binary[i] * binary[i + cl]
                                   for i in range(len(binary) - cl))
            scores[n] = cycle_score + self.counter.get(n, 0)
        return self._rank(scores)

    def F67_long_term_trend(self) -> Result:
        period = max(10, self.n // 5)
        scores = {}
        for n in self.all_nums:
            pf = [self.numbers[i:i + period].count(n) / max(period, 1)
                  for i in range(0, self.n, period)]
            scores[n] = max(0, self._linear_slope(pf)) * 100 if len(pf) >= 3 else 0
        return self._rank(scores)

    def F68_short_term_momentum(self) -> Result:
        c5 = Counter(self._last_n(5))
        c10 = Counter(self._last_n(10))
        scores = {}
        for n in self.all_nums:
            momentum = c5.get(n, 0) / 5.0 - c10.get(n, 0) / 10.0
            scores[n] = max(0, momentum) * 100 + self.counter.get(n, 0)
        return self._rank(scores)

    def F69_recency_bias_corr(self) -> Result:
        c5 = Counter(self._last_n(5))
        scores = {}
        for n in self.all_nums:
            all_f = self.counter.get(n, 0)
            corr = all_f - c5.get(n, 0) * (self.n / 5.0)
            scores[n] = max(0, corr) + all_f * 0.1
        return self._rank(scores)

    def F70_time_decay_weighted(self) -> Result:
        scores: Dict[int, float] = defaultdict(float)
        for i, num in enumerate(self.numbers):
            scores[num] += math.exp(-0.05 * (self.n - i - 1))
        return self._rank({n: scores.get(n, 0.0) for n in self.all_nums})

    # ================================================================== #
    # GROUP 8 — COMPOSITE & ADVANCED (F71–F75)                           #
    # ================================================================== #
    def F71_fibonacci_resonance(self) -> Result:
        fib = [0, 1]
        while fib[-1] < self.max_val:
            fib.append(fib[-1] + fib[-2])
        fib_set = {f for f in fib if f <= self.max_val}
        scores = {}
        for n in self.all_nums:
            min_dist = min(abs(n - f) for f in fib_set) if fib_set else self.max_val
            scores[n] = self.counter.get(n, 0) + max(0, 10 - min_dist)
        return self._rank(scores)

    def F72_prime_weighting(self) -> Result:
        def is_prime(k: int) -> bool:
            if k < 2:
                return False
            return all(k % i != 0 for i in range(2, int(k ** 0.5) + 1))
        prime_trend = sum(1 for x in self._last_n(10) if is_prime(x)) / 10.0
        scores = {}
        for n in self.all_nums:
            base = self.counter.get(n, 0)
            scores[n] = base * (1 + prime_trend) if is_prime(n) else base
        return self._rank(scores)

    def F73_golden_ratio(self) -> Result:
        phi = (1 + math.sqrt(5)) / 2
        if not self.numbers:
            return self._rank({n: 0 for n in self.all_nums})
        phi_targets = set()
        for x in self._last_n(5):
            phi_targets.add(int(x * phi) % (self.max_val + 1))
            phi_targets.add(int(x / phi) % (self.max_val + 1))
        scores = {}
        for n in self.all_nums:
            min_d = min(abs(n - t) for t in phi_targets) if phi_targets else self.max_val
            scores[n] = self.counter.get(n, 0) + max(0, 10 - min_d)
        return self._rank(scores)

    def F74_ensemble_consensus(self) -> Result:
        sub = [self.F01_raw_frequency, self.F02_recent_freq_10,
               self.F05_linear_weighted, self.F11_hot_numbers,
               self.F14_due_numbers, self.F24_gap_ratio, self.F43_zscore_ranking]
        votes: Counter = Counter()
        for fn in sub:
            for rank, (num_str, _) in enumerate(fn()[:10]):
                votes[num_str] += max(0, 10 - rank)
        return self._rank({n: float(votes.get(self._fmt(n), 0)) for n in self.all_nums})

    def F75_adaptive_composite(self) -> Result:
        sources = {
            'freq':  dict(self.F06_exp_weighted()),
            'gap':   dict(self.F15_overdue_avg_gap()),
            'pos':   dict(self.F38_position_weighted()),
            'stat':  dict(self.F43_zscore_ranking()),
        }
        maxes = {k: max((float(v) for v in d.values()), default=1) or 1 for k, d in sources.items()}
        weights = {'freq': 0.35, 'gap': 0.25, 'pos': 0.20, 'stat': 0.20}
        scores = {}
        for n in self.all_nums:
            s = self._fmt(n)
            scores[n] = sum(weights[k] * float(sources[k].get(s, 0)) / maxes[k]
                            for k in sources)
        return self._rank(scores)

    # ================================================================== #
    # RUN ENGINE                                                          #
    # ================================================================== #
    def run_all(
        self,
        active_codes: Optional[set] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Result]:
        """
        Run all active formulas.
        Returns {formula_code: [(number_str, score), ...]}
        """
        if active_codes is None:
            active_codes = set(self.FORMULA_REGISTRY.keys())
        if weights is None:
            weights = {}

        results: Dict[str, Result] = {}
        for code, meta in self.FORMULA_REGISTRY.items():
            if code not in active_codes:
                continue
            method_name = f"{code}_{meta['suffix']}"
            method = getattr(self, method_name, None)
            if method is None:
                continue
            try:
                raw: Result = method()
                w = weights.get(code, 1.0)
                results[code] = [(num, score * w) for num, score in raw]
            except Exception:
                results[code] = []
        return results

    # ================================================================== #
    # AGGREGATION                                                         #
    # ================================================================== #
    @staticmethod
    def aggregate_option_a(formula_results: Dict[str, Result], top_n: int = 10) -> list:
        """
        Option A — Highest Frequency.
        Count which numbers appear in the Top-5 of the most formulas.
        Returns [(number_str, appearance_count), ...]
        """
        counts: Counter = Counter()
        for results in formula_results.values():
            for num_str, _ in results[:5]:
                counts[num_str] += 1
        return counts.most_common(top_n)

    @staticmethod
    def aggregate_option_b(formula_results: Dict[str, Result], top_n: int = 10) -> list:
        """
        Option B — Ranking Score.
        1st=5 pts, 2nd=4 pts, 3rd=3 pts, 4th=2 pts, 5th=1 pt per formula.
        Returns [(number_str, total_score), ...]
        """
        point_map = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1}
        totals: Dict[str, float] = defaultdict(float)
        for results in formula_results.values():
            for rank_idx, (num_str, _) in enumerate(results[:5]):
                totals[num_str] += point_map.get(rank_idx, 0)
        return sorted(totals.items(), key=lambda x: -x[1])[:top_n]

    @staticmethod
    def aggregate_option_c_enhanced(formula_results: Dict[str, Result], top_n: int = 10) -> list:
        """
        Option C — Enhanced Consensus (NEW OPTIMIZED METHOD).
        Combines both frequency consensus AND weighted score for better accuracy.
        Heavily weights Gap Analysis formulas (F21-F30) which are most reliable.
        Returns [(number_str, consensus_score), ...]
        """
        # Group formulas by category for weighted voting
        gap_formulas = {'F21', 'F23', 'F24', 'F27', 'F29', 'F25', 'F26', 'F28', 'F30'}
        hot_cold_formulas = {'F13', 'F14', 'F15', 'F18', 'F20'}
        stat_formulas = {'F41', 'F42', 'F43', 'F44', 'F47', 'F50'}

        scores: Dict[str, float] = defaultdict(float)
        formula_votes: Dict[str, int] = defaultdict(int)

        for code, results in formula_results.items():
            category_weight = 1.0
            if code in gap_formulas:
                category_weight = 3.0  # Gap analysis: 3x weight
            elif code in hot_cold_formulas:
                category_weight = 2.0  # Hot/Cold: 2x weight
            elif code in stat_formulas:
                category_weight = 1.5  # Statistical: 1.5x weight

            for rank_idx, (num_str, score) in enumerate(results[:5]):
                # Points decrease by rank, multiplied by category weight
                point_map = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1}
                points = point_map.get(rank_idx, 0)
                scores[num_str] += (points * category_weight)
                formula_votes[num_str] += 1

        # Sort by: score (weighted), then by number of formulas supporting it
        results = [
            (num_str, scores[num_str])
            for num_str in sorted(scores.keys(),
                                 key=lambda x: (-scores[x], -formula_votes[x]))
        ]
        return results[:top_n]

    @staticmethod
    def aggregate_coverage(formula_results: Dict[str, Result],
                           top_n: int = 10,
                           num_digits: int = 2) -> list:
        """
        Option D — Coverage.

        Honest strategy for a fair (random) draw: instead of pretending one number
        is "the answer", spread the budget across `top_n` DISTINCT numbers so the
        chance that one of them hits is maximised. Expected hit-rate is exactly
        top_n / 10**num_digits — and the backtest confirms the formulas cannot beat
        that, so the only real lever is how many numbers you choose to cover.

        Numbers are ranked by cross-formula consensus (so the set is not arbitrary),
        then the list is PADDED with the next unused numbers to guarantee the set
        always contains exactly `top_n` distinct picks — never wasting a slot on a
        duplicate the way a naive vote count can.

        Returns [(number_str, consensus_score), ...] of length `top_n`.
        """
        space = 10 ** num_digits
        top_n = max(1, min(top_n, space))

        scores: Dict[str, float] = defaultdict(float)
        votes: Dict[str, int] = defaultdict(int)
        for results in formula_results.values():
            for rank_idx, (num_str, _) in enumerate(results[:10]):
                scores[num_str] += max(0, 10 - rank_idx)
                votes[num_str] += 1

        ranked = sorted(scores.keys(), key=lambda x: (-scores[x], -votes[x]))
        picks = ranked[:top_n]

        # Pad to exactly top_n distinct numbers so coverage is guaranteed.
        if len(picks) < top_n:
            chosen = set(picks)
            for i in range(space):
                s = str(i).zfill(num_digits)
                if s not in chosen:
                    picks.append(s)
                    chosen.add(s)
                    if len(picks) >= top_n:
                        break

        return [(p, scores.get(p, 0.0)) for p in picks[:top_n]]

    @staticmethod
    def coverage_expectation(top_n: int, num_digits: int) -> float:
        """Honest expected hit-rate (%) for covering `top_n` of 10**num_digits numbers."""
        space = 10 ** num_digits
        return min(top_n, space) / space * 100.0
