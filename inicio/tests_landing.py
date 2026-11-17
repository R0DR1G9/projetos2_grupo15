from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse


class LandingTests(TestCase):
    def test_visitante_ve_a_landing_na_raiz(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'inicio/landing.html')
        self.assertContains(resp, 'ESG para quem costura o dia a dia da moda.')

    def test_landing_leva_para_cadastro_e_login(self):
        resp = self.client.get('/')
        self.assertContains(resp, f'href="{reverse("cadastro")}"')
        self.assertContains(resp, f'href="{reverse("login")}"')

    def test_landing_usa_arquivos_separados_sem_estilo_inline(self):
        html = self.client.get('/').content.decode()
        self.assertIn('css/landing.css', html)
        self.assertNotIn('<style', html)
        self.assertNotIn(' style=', html)
        self.assertNotIn('<script', html)

    def test_imagens_da_landing_existem(self):
        for nome in ['diagnostico', 'plano', 'evolucao', 'social', 'biblioteca']:
            self.assertIsNotNone(finders.find(f'img/landing/{nome}.jpg'), nome)

    def test_usuario_logado_continua_vendo_o_painel(self):
        usuario = get_user_model().objects.create_user('gestora', password='senha-forte-123', first_name='Aurora')
        self.client.force_login(usuario)
        resp = self.client.get('/')
        self.assertTemplateNotUsed(resp, 'inicio/landing.html')
        self.assertContains(resp, 'Sua jornada ESG continua aqui.')
