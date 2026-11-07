from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atividades', '0002_atividade_descricao'),
    ]

    operations = [
        migrations.AddField(
            model_name='atividade',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='atividades', to=settings.AUTH_USER_MODEL),
        ),
    ]
