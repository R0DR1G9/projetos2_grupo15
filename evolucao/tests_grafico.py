from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from diagnostico.models import DiagnosticoESG


class GraficoEvolucaoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('gestora', password='senha-forte-123')
        self.client.force_login(self.user)
        DiagnosticoESG.objects.create(usuario=self.user, nome_empresa='Aurora', residuos_textesis=True)
        DiagnosticoESG.objects.create(usuario=self.user, nome_empresa='Aurora', residuos_textesis=True, uso_agua=True)

    def test_tem_somente_duas_abas_de_grafico(self):
        html = self.client.get(reverse('evolucao')).content.decode()
        self.assertIn('data-tipo="linha"', html)
        self.assertIn('data-tipo="pilares"', html)
        self.assertNotIn('data-tipo="radar"', html)
        self.assertNotIn('Antes e depois', html)

    def test_script_nao_desenha_mais_radar_nem_barras(self):
        with open(finders.find('js/evolucao.js'), encoding='utf-8') as arquivo:
            codigo = arquivo.read()
        self.assertNotIn("'radar'", codigo)
        self.assertNotIn("type: 'bar'", codigo)
        self.assertIn('pilares', codigo)
