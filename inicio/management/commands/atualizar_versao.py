import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

PADRAO = re.compile(r'^\d+\.\d+\.\d+$')
ARQUIVO_PADRAO = Path(settings.BASE_DIR) / 'setup' / 'versao.py'


def proxima_versao(atual, tipo):
    maior, menor, correcao = (int(p) for p in atual.split('.'))
    if tipo == 'major':
        return f'{maior + 1}.0.0'
    if tipo == 'minor':
        return f'{maior}.{menor + 1}.0'
    if tipo == 'patch':
        return f'{maior}.{menor}.{correcao + 1}'
    if PADRAO.match(tipo):
        return tipo
    raise ValueError(tipo)


def ler_versao(arquivo):
    achado = re.search(r'VERSAO\s*=\s*"(\d+\.\d+\.\d+)"', Path(arquivo).read_text(encoding='utf-8'))
    if not achado:
        raise CommandError(f'Não achei a versão em {arquivo}.')
    return achado.group(1)


class Command(BaseCommand):
    help = 'Atualiza a versão do Vastra mostrada no menu lateral. Use patch, minor, major ou um número como 1.2.0.'

    def add_arguments(self, parser):
        parser.add_argument('tipo', help='patch, minor, major ou o número da versão (ex.: 1.2.0)')
        parser.add_argument('--arquivo', default=str(ARQUIVO_PADRAO), help='Arquivo da versão (só para testes).')

    def handle(self, *args, **opcoes):
        atual = ler_versao(opcoes['arquivo'])
        try:
            nova = proxima_versao(atual, opcoes['tipo'])
        except ValueError:
            raise CommandError('Use patch, minor, major ou um número no formato 1.2.0.')
        Path(opcoes['arquivo']).write_text(f'VERSAO = "{nova}"\n', encoding='utf-8')
        self.stdout.write(self.style.SUCCESS(f'Versão atualizada: {atual} -> {nova}'))
