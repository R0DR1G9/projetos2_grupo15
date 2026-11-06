from django.db import migrations

from biblioteca.conteudos_iniciais import CONTEUDOS


def atualizar(apps, schema_editor):
    Conteudo = apps.get_model('biblioteca', 'Conteudo')
    for dados in CONTEUDOS:
        Conteudo.objects.filter(titulo=dados['titulo']).update(texto=dados['texto'])


class Migration(migrations.Migration):

    dependencies = [('biblioteca', '0003_conteudos_dos_pilares')]

    operations = [migrations.RunPython(atualizar, migrations.RunPython.noop)]
