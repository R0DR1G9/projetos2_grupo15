from django.db import migrations

from biblioteca.conteudos_iniciais import CONTEUDOS_PILARES


def criar(apps, schema_editor):
    Conteudo = apps.get_model('biblioteca', 'Conteudo')
    for dados in CONTEUDOS_PILARES:
        Conteudo.objects.get_or_create(titulo=dados['titulo'], defaults=dados)


def remover(apps, schema_editor):
    Conteudo = apps.get_model('biblioteca', 'Conteudo')
    Conteudo.objects.filter(titulo__in=[d['titulo'] for d in CONTEUDOS_PILARES]).delete()


class Migration(migrations.Migration):

    dependencies = [('biblioteca', '0002_conteudos_iniciais')]

    operations = [migrations.RunPython(criar, remover)]
