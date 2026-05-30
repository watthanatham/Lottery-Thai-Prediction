from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysissession',
            name='option_c_results',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='predictionentry',
            name='option',
            field=models.CharField(
                choices=[
                    ('A', 'Option A — Frequency'),
                    ('B', 'Option B — Ranking Score'),
                    ('C', 'Option C — Enhanced Consensus'),
                ],
                max_length=1,
            ),
        ),
    ]
