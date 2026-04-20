from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analysis'
    verbose_name = 'Lottery Analysis'

    def ready(self):
        # Ensure FormulaConfig rows exist on startup
        from django.db.models.signals import post_migrate
        post_migrate.connect(_seed_formula_configs, sender=self)


def _seed_formula_configs(sender, **kwargs):
    try:
        from apps.analysis.models import FormulaConfig
        from apps.analysis.formulas import FormulaEngine
        for code, meta in FormulaEngine.FORMULA_REGISTRY.items():
            FormulaConfig.objects.get_or_create(
                formula_code=code,
                defaults={
                    'formula_name': meta['name'],
                    'formula_group': meta['group'],
                    'description': meta['description'],
                    'weight': 1.0,
                    'is_active': True,
                }
            )
    except Exception:
        pass  # Table may not exist yet during initial migrate
