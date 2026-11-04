from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Conteudo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=150, verbose_name='Título')),
                ('descricao', models.CharField(max_length=300, verbose_name='Resumo')),
                ('categoria', models.CharField(choices=[('ambiental', 'Ambiental'), ('social', 'Social'), ('governanca', 'Governança')], max_length=20, verbose_name='Categoria')),
                ('tipo', models.CharField(choices=[('video', 'Vídeo'), ('texto', 'Texto')], default='texto', max_length=10, verbose_name='Tipo')),
                ('link_video', models.URLField(blank=True, verbose_name='Link do vídeo no YouTube')),
                ('texto', models.TextField(blank=True, verbose_name='Texto do tutorial')),
                ('publicado', models.BooleanField(default=True, verbose_name='Publicado')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Conteúdo',
                'verbose_name_plural': 'Conteúdos',
                'ordering': ['categoria', 'titulo'],
            },
        ),
    ]
