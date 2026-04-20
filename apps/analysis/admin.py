from django.contrib import admin
from .models import LotteryDraw, FormulaConfig, AnalysisSession, PredictionEntry


@admin.register(LotteryDraw)
class LotteryDrawAdmin(admin.ModelAdmin):
    list_display = ['draw_date', 'draw_label', 'first_prize', 'two_back',
                    'three_front_1', 'three_back_1', 'created_at']
    list_filter = ['draw_date']
    search_fields = ['first_prize', 'two_back']
    ordering = ['-draw_date']
    date_hierarchy = 'draw_date'


@admin.register(FormulaConfig)
class FormulaConfigAdmin(admin.ModelAdmin):
    list_display = ['formula_code', 'formula_name', 'formula_group', 'weight', 'is_active']
    list_filter = ['formula_group', 'is_active']
    list_editable = ['weight', 'is_active']
    ordering = ['formula_code']
    search_fields = ['formula_name', 'formula_code']


@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference_draw', 'lottery_type', 'formulas_run',
                    'history_limit', 'created_at']
    list_filter = ['lottery_type']
    readonly_fields = ['formula_raw_results', 'option_a_results', 'option_b_results',
                       'created_at', 'formulas_run', 'formulas_active']
    ordering = ['-created_at']


@admin.register(PredictionEntry)
class PredictionEntryAdmin(admin.ModelAdmin):
    list_display = ['session', 'option', 'rank', 'number', 'frequency_count',
                    'ranking_score', 'is_verified', 'was_correct']
    list_filter = ['option', 'is_verified', 'was_correct']
    ordering = ['session', 'option', 'rank']
