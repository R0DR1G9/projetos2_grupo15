from django.db import migrations

from biblioteca.conteudos_iniciais import CONTEUDOS


def criar(apps, schema_editor):
    Conteudo = apps.get_model('biblioteca', 'Conteudo')
    for dados in CONTEUDOS:
        Conteudo.objects.get_or_create(titulo=dados['titulo'], defaults=dados)


def remover(apps, schema_editor):
    Conteudo = apps.get_model('biblioteca', 'Conteudo')
    Conteudo.objects.filter(titulo__in=[d['titulo'] for d in CONTEUDOS]).delete()


class Migration(migrations.Migration):

    dependencies = [('biblioteca', '0001_initial')]

    operations = [migrations.RunPython(criar, remover)]
