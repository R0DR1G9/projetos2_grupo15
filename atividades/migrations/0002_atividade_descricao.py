from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='atividade',
            name='descricao',
            field=models.CharField(blank=True, max_length=300, verbose_name='Detalhes'),
        ),
    ]
