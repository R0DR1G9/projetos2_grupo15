from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from atividades.models import Atividade
from diagnostico.models import DiagnosticoESG


class InicioTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('gestora', password='senha-forte-123', first_name='Aurora')
        self.client.force_login(self.user)

    def test_inicio_sem_dados_pede_diagnostico(self):
        resp = self.client.get(reverse('inicio'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Você ainda não fez o diagnóstico')

    def test_inicio_mostra_score_e_variacao(self):
        DiagnosticoESG.objects.create(usuario=self.user, nome_empresa='Aurora', residuos_textesis=True)
        DiagnosticoESG.objects.create(usuario=self.user, nome_empresa='Aurora', residuos_textesis=True, uso_agua=True,
                                      codigo_etica=True, saude_seguranca=True)
        resp = self.client.get(reverse('inicio'))
        self.assertContains(resp, 'Seu score ESG')
        self.assertEqual(resp.context['variacao'], 25.0)
        self.assertEqual(resp.context['score']['geral'], 33.3)

    def test_inicio_lista_somente_acoes_em_andamento(self):
        Atividade.objects.create(titulo='Coleta seletiva', status='andamento')
        Atividade.objects.create(titulo='Politica de diversidade', status='aguardando')
        resp = self.client.get(reverse('inicio'))
        self.assertContains(resp, 'Coleta seletiva')
        self.assertNotContains(resp, 'Politica de diversidade')

    def test_diagnostico_agora_fica_em_diagnostico(self):
        self.assertEqual(reverse('home'), '/diagnostico/')
        self.assertEqual(self.client.get('/diagnostico/').status_code, 200)

    def test_todas_as_paginas_abrem_com_o_novo_layout(self):
        for nome in ['inicio', 'home', 'quadro_atividades', 'evolucao', 'ranking', 'sobre', 'quem_somos', 'contato']:
            resp = self.client.get(reverse(nome))
            self.assertEqual(resp.status_code, 200, nome)
            self.assertContains(resp, 'Sua jornada ESG continua aqui.', msg_prefix=nome)
