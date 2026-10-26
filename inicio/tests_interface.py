import re

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from diagnostico import perguntas
from diagnostico.models import VERSAO_ATUAL, DiagnosticoESG


def rodape_da_barra_lateral(html):
    inicio = html.index('class="sidebar-rodape"')
    return html[inicio:html.index('</aside>', inicio)]


class InterfaceSemIconesTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('gestora', password='senha-forte-123', first_name='Aurora')
        self.client.force_login(self.user)
        self.diagnostico = DiagnosticoESG.objects.create(
            usuario=self.user,
            nome_empresa='Aurora',
            tipo_operacao='confeccao',
            respostas={pid: 3 for pid in perguntas.aplicaveis('confeccao')},
            versao_questionario=VERSAO_ATUAL,
        )

    def titulo(self, nome_url):
        html = self.client.get(reverse(nome_url)).content.decode()
        return re.search(r'<h1 class="display-5[^>]*>(.*?)</h1>', html, re.S).group(1)

    def test_titulo_do_diagnostico_sem_icone(self):
        h1 = self.titulo('home')
        self.assertIn('Diagnóstico de Maturidade ESG', h1)
        self.assertNotIn('<i', h1)

    def test_titulo_da_evolucao_sem_icone(self):
        h1 = self.titulo('evolucao')
        self.assertIn('Evolução ESG', h1)
        self.assertNotIn('<i', h1)

    def test_titulo_do_quadro_de_atividades_sem_icone(self):
        h1 = self.titulo('quadro_atividades')
        self.assertIn('Quadro de atividades', h1)
        self.assertNotIn('<i', h1)

    def test_pilares_do_formulario_sem_icone(self):
        html = self.client.get(reverse('novo_diagnostico')).content.decode()
        titulos = [
            t for t in re.findall(r'<h2 class="h5 fw-bold mb-1">(.*?)</h2>', html, re.S)
            if 'Pilar' in t
        ]
        self.assertEqual(len(titulos), 3)
        for titulo in titulos:
            self.assertTrue(titulo.startswith('Pilar '), titulo)
            self.assertNotIn('<i', titulo)

    def test_pilares_do_resultado_sem_icone_nem_medalha(self):
        html = self.client.get(reverse('resultado_diagnostico', args=[self.diagnostico.pk])).content.decode()
        cartoes = re.findall(r'<div class="pilar-card .*?<div class="valor mt-1">', html, re.S)
        self.assertEqual(len(cartoes), 3)
        for cartao in cartoes:
            self.assertNotIn('<i', cartao)
            for medalha in ('🥇', '🥈', '🥉'):
                self.assertNotIn(medalha, cartao)

    def test_porcentagens_dos_pilares_no_inicio_sem_icone(self):
        html = self.client.get(reverse('inicio')).content.decode()
        cartoes = re.findall(r'<div class="mini-pilar .*?</div></div></div>', html, re.S)
        self.assertEqual(len(cartoes), 3)
        for cartao in cartoes:
            self.assertNotIn('<i', cartao)
        for icone in ('bi-tree', 'bi-bank'):
            self.assertNotIn(icone, html)


class SairDoSiteTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('gestora', password='senha-forte-123', first_name='Aurora')

    def test_barra_lateral_nao_tem_entrar_nem_sair_logado(self):
        self.client.force_login(self.user)
        rodape = rodape_da_barra_lateral(self.client.get(reverse('inicio')).content.decode())
        for texto in ('Sair', 'Entrar', 'Criar conta', 'logout'):
            self.assertNotIn(texto, rodape)
        self.assertIn('github.com', rodape)

    def test_barra_lateral_nao_tem_entrar_nem_sair_deslogado(self):
        rodape = rodape_da_barra_lateral(self.client.get(reverse('sobre')).content.decode())
        for texto in ('Sair', 'Entrar', 'Criar conta', 'login'):
            self.assertNotIn(texto, rodape)

    def test_sair_pede_confirmacao_antes_de_enviar(self):
        self.client.force_login(self.user)
        html = self.client.get(reverse('inicio')).content.decode()
        formularios = re.findall(r'<form[^>]*action="/logout/"[^>]*>', html)
        self.assertEqual(len(formularios), 1)
        self.assertIn('data-confirmar="Deseja realmente sair da sua conta?"', formularios[0])

    def test_topo_continua_com_entrar_e_criar_conta_deslogado(self):
        html = self.client.get(reverse('sobre')).content.decode()
        self.assertIn(reverse('login'), html)
        self.assertIn(reverse('cadastro'), html)

    def test_sair_encerra_a_sessao(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse('logout'))
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
