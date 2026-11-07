from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from selenium.webdriver.common.by import By

from atividades.models import Atividade
from notificacoes.models import Notificacao
from rede_social.models import Comentario, Post

from .base import SENHA, NavegadorTestCase


class PlanoDeAcaoE2ETests(NavegadorTestCase):
    def selos(self):
        return self.navegador.find_elements(By.CSS_SELECTOR, '[data-sino-contagem]')

    def test_cenario_1_criar_acao_com_prazo_e_responsavel(self):
        prazo = timezone.localdate() + timedelta(days=10)
        self.abrir('/atividades/')
        self.navegador.find_element(By.NAME, 'titulo').send_keys('Trocar lampadas por LED')
        self.navegador.execute_script("arguments[0].value = arguments[1];", self.navegador.find_element(By.NAME, 'prazo'), prazo.isoformat())
        self.navegador.find_element(By.NAME, 'responsavel').send_keys('Marina')
        self.navegador.find_element(By.CSS_SELECTOR, 'main form button[type="submit"]').click()
        self.esperar_texto('Atividade adicionada')
        self.espera.until(lambda d: 'Trocar lampadas por LED' in d.find_element(By.CSS_SELECTOR, '[data-atividade]').text)
        cartao = self.navegador.find_element(By.CSS_SELECTOR, '[data-atividade]')
        self.assertIn('Trocar lampadas por LED', cartao.text)
        self.assertIn('Responsável: Marina', cartao.text)
        self.assertIn(f'Prazo: {prazo:%d/%m/%Y}', cartao.text)

    def test_cenario_2_acao_atrasada_avisa_no_sino(self):
        Atividade.objects.create(usuario=self.usuario, titulo='Auditar fornecedores', categoria='governanca', prazo=timezone.localdate() - timedelta(days=2))
        self.abrir('/')
        self.espera.until(lambda d: self.selos())
        self.assertEqual(self.selos()[0].text, '1')
        self.navegador.find_element(By.CSS_SELECTOR, '.btn-sino').click()
        self.espera.until(lambda d: 'Auditar fornecedores - Atrasada há 2 dias' in d.find_element(By.CSS_SELECTOR, '[data-sino-menu]').text)
        self.navegador.find_element(By.CSS_SELECTOR, '[data-sino-menu] .sino-item').click()
        self.espera.until(lambda d: '/atividades/' in d.current_url)
        self.esperar_texto('Auditar fornecedores')
        self.assertTrue(Notificacao.objects.get(usuario=self.usuario).lida)
        self.assertEqual(self.selos(), [])

    def test_cenario_3_comentario_de_outra_empresa_avisa_e_marca_como_lido(self):
        outra = get_user_model().objects.create_user('outra', password=SENHA, first_name='Outra Malhas')
        post = Post.objects.create(autor=self.usuario, conteudo='Reaproveitamos retalhos')
        Comentario.objects.create(post=post, autor=outra, conteudo='Parabens!')
        self.abrir('/notificacoes/')
        self.esperar_texto('Outra Malhas comentou na sua publicação')
        self.navegador.find_element(By.CSS_SELECTOR, '[data-lista-notificacoes] form, main form button[type="submit"]').click()
        self.esperar_texto('Todas as notificações foram marcadas como lidas')
        self.assertEqual(self.selos(), [])
        self.assertEqual(Notificacao.objects.filter(usuario=self.usuario, lida=False).count(), 0)
