from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0003_atividade_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='atividade',
            name='prazo',
            field=models.DateField(blank=True, null=True, verbose_name='Prazo'),
        ),
        migrations.AddField(
            model_name='atividade',
            name='responsavel',
            field=models.CharField(blank=True, max_length=80, verbose_name='Responsável'),
        ),
    ]
