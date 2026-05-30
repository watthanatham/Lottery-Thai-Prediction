"""
Models for Thai Government Lottery Analysis App
"""
from django.db import models
from django.utils import timezone


class LotteryDraw(models.Model):
    """
    Records a single Thai Government Lottery draw result.
    Draws happen on the 1st and 16th of each month.
    """
    draw_date = models.DateField(unique=True, verbose_name='Draw Date')
    draw_label = models.CharField(
        max_length=20, blank=True, default='',
        help_text='E.g. "1 Jan 2025"', verbose_name='Draw Label'
    )

    # First prize (6 digits) — the main number
    first_prize = models.CharField(max_length=6, verbose_name='First Prize (6-digit)')

    # Near first prize (first_prize ± 1)
    near_first_1 = models.CharField(max_length=6, blank=True, default='', verbose_name='Near 1st Prize (lower)')
    near_first_2 = models.CharField(max_length=6, blank=True, default='', verbose_name='Near 1st Prize (upper)')

    # 3-digit front prizes (first 3 digits)
    three_front_1 = models.CharField(max_length=3, blank=True, default='', verbose_name='3-Digit Front #1')
    three_front_2 = models.CharField(max_length=3, blank=True, default='', verbose_name='3-Digit Front #2')

    # 3-digit back prizes (last 3 digits)
    three_back_1 = models.CharField(max_length=3, blank=True, default='', verbose_name='3-Digit Back #1')
    three_back_2 = models.CharField(max_length=3, blank=True, default='', verbose_name='3-Digit Back #2')

    # 2-digit back prize (last 2 digits of first prize)
    two_back = models.CharField(max_length=2, blank=True, default='', verbose_name='2-Digit Back')

    notes = models.TextField(blank=True, default='', verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-draw_date']
        verbose_name = 'Lottery Draw'
        verbose_name_plural = 'Lottery Draws'

    def __str__(self):
        return f"{self.draw_date} — {self.first_prize}"

    def save(self, *args, **kwargs):
        fp = self.first_prize.strip()
        if len(fp) == 6:
            if not self.two_back:
                self.two_back = fp[-2:]
            if not self.three_back_1:
                self.three_back_1 = fp[-3:]
            if not self.three_front_1:
                self.three_front_1 = fp[:3]
            if not self.near_first_1:
                self.near_first_1 = str(int(fp) - 1).zfill(6)
            if not self.near_first_2:
                self.near_first_2 = str(int(fp) + 1).zfill(6)
        if not self.draw_label:
            self.draw_label = self.draw_date.strftime('%-d %b %Y') if self.draw_date else ''
        super().save(*args, **kwargs)

    def get_number_for_type(self, lottery_type: str) -> str | None:
        """Return the relevant prize number for a given lottery type."""
        mapping = {
            '2D': self.two_back,
            '3F': self.three_front_1,
            '3B': self.three_back_1,
        }
        return mapping.get(lottery_type)


class FormulaConfig(models.Model):
    """User-adjustable weight and active/inactive toggle for each of the 75 formulas."""
    formula_code = models.CharField(max_length=10, unique=True, verbose_name='Code')
    formula_name = models.CharField(max_length=120, verbose_name='Name')
    formula_group = models.CharField(max_length=60, verbose_name='Group')
    description = models.TextField(verbose_name='Description')
    weight = models.FloatField(default=1.0, verbose_name='Weight')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        ordering = ['formula_code']
        verbose_name = 'Formula Config'
        verbose_name_plural = 'Formula Configs'

    def __str__(self):
        return f"{self.formula_code}: {self.formula_name}"


class AnalysisSession(models.Model):
    """
    One analysis run — uses historical draws up to a reference draw
    to predict the next draw for a given lottery type.
    """
    LOTTERY_TYPE_CHOICES = [
        ('2D', '2-Digit Back (เลขท้าย 2 ตัว)'),
        ('3F', '3-Digit Front (เลขหน้า 3 ตัว)'),
        ('3B', '3-Digit Back (เลขหลัง 3 ตัว)'),
    ]

    reference_draw = models.ForeignKey(
        LotteryDraw, on_delete=models.CASCADE,
        related_name='analyses', verbose_name='Based on Draw'
    )
    lottery_type = models.CharField(
        max_length=2, choices=LOTTERY_TYPE_CHOICES, verbose_name='Lottery Type'
    )
    target_draw_date = models.DateField(
        null=True, blank=True, verbose_name='Target Draw Date'
    )
    history_limit = models.IntegerField(
        default=50, verbose_name='Draws Used in History'
    )
    formulas_run = models.IntegerField(default=0)
    formulas_active = models.IntegerField(default=0)

    # Raw results per formula: { "F01": [["45", 12.0], ["23", 10.0], ...], ... }
    formula_raw_results = models.JSONField(default=dict)

    # Option A top picks: [["45", 38], ["67", 31], ...]  (number, appearance_count)
    option_a_results = models.JSONField(default=list)

    # Option B top picks: [["45", 245.0], ...]  (number, ranking_score)
    option_b_results = models.JSONField(default=list)

    # Option C top picks: [["45", 87.5], ...]  (number, weighted consensus score)
    option_c_results = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analysis Session'
        verbose_name_plural = 'Analysis Sessions'

    def __str__(self):
        return f"[{self.get_lottery_type_display()}] Based on {self.reference_draw.draw_date} — {self.created_at:%Y-%m-%d %H:%M}"

    def get_option_a_numbers(self):
        return [item[0] for item in self.option_a_results]

    def get_option_b_numbers(self):
        return [item[0] for item in self.option_b_results]

    def get_option_c_numbers(self):
        return [item[0] for item in self.option_c_results]


class PredictionEntry(models.Model):
    """Individual predicted number tracked for a specific analysis session."""
    OPTION_CHOICES = [
        ('A', 'Option A — Frequency'),
        ('B', 'Option B — Ranking Score'),
        ('C', 'Option C — Enhanced Consensus'),
    ]

    session = models.ForeignKey(
        AnalysisSession, on_delete=models.CASCADE,
        related_name='predictions', verbose_name='Session'
    )
    option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    rank = models.IntegerField()
    number = models.CharField(max_length=6)
    frequency_count = models.IntegerField(default=0)   # Option A: how many formulas put it in top 5
    ranking_score = models.FloatField(default=0.0)      # Option B: total ranking points

    # Verification
    is_verified = models.BooleanField(default=False)
    was_correct = models.BooleanField(null=True, blank=True)
    verified_against = models.ForeignKey(
        LotteryDraw, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_predictions'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['option', 'rank']
        unique_together = [['session', 'option', 'rank']]
        verbose_name = 'Prediction Entry'
        verbose_name_plural = 'Prediction Entries'

    def __str__(self):
        return f"Option {self.option} #{self.rank}: {self.number}"

    def verify(self, actual_draw: LotteryDraw):
        actual_number = actual_draw.get_number_for_type(self.session.lottery_type)
        self.was_correct = (actual_number == self.number) if actual_number else False
        self.is_verified = True
        self.verified_against = actual_draw
        self.verified_at = timezone.now()
        self.save()
