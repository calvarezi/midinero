from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(
                choices=[
                    ('HIGH_EXPENSE', 'Gasto alto'), 
                    ('GOAL_COMPLETED', 'Meta cumplida'), 
                    ('BUDGET_EXCEEDED', 'Presupuesto superado'), 
                    ('BUDGET_WARNING', 'Advertencia de presupuesto'),
                    ('REMINDER', 'Recordatorio'), 
                    ('SYSTEM', 'Sistema')
                ], 
                default='SYSTEM', 
                max_length=32
            ),
        ),
    ]