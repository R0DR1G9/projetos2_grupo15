from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnostico', '0004_diagnostico_v2'),
    ]

    operations = [
        migrations.AddField(
            model_name='diagnosticoesg',
            name='versao_questionario',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
