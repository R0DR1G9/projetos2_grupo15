import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from inicio.management.commands.atualizar_versao import ler_versao, proxima_versao
from setup.versao import VERSAO


class VersaoTests(TestCase):
    def test_menu_mostra_a_versao_atual(self):
        usuario = get_user_model().objects.create_user('gestora', password='senha-forte-123', first_name='Aurora')
        self.client.force_login(usuario)
        self.assertContains(self.client.get(reverse('inicio')), f'Vastra v{VERSAO}')

    def test_calculo_da_proxima_versao(self):
        self.assertEqual(proxima_versao('1.2.3', 'patch'), '1.2.4')
        self.assertEqual(proxima_versao('1.2.3', 'minor'), '1.3.0')
        self.assertEqual(proxima_versao('1.2.3', 'major'), '2.0.0')
        self.assertEqual(proxima_versao('1.2.3', '3.0.1'), '3.0.1')
        with self.assertRaises(ValueError):
            proxima_versao('1.2.3', 'abc')

    def test_comando_atualiza_o_arquivo(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'versao.py'
            arquivo.write_text('VERSAO = "1.0.0"\n', encoding='utf-8')
            call_command('atualizar_versao', 'minor', arquivo=str(arquivo), stdout=open('/dev/null', 'w'))
            self.assertEqual(ler_versao(arquivo), '1.1.0')
            with self.assertRaises(CommandError):
                call_command('atualizar_versao', 'xyz', arquivo=str(arquivo))
