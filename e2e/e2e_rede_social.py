from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By

from rede_social.models import Post

from .base import SENHA, NavegadorTestCase


class RedeSocialE2ETests(NavegadorTestCase):
    def posts(self):
        return self.navegador.find_elements(By.CSS_SELECTOR, 'article.rs-post')

    def test_cenario_1_publicar_no_feed(self):
        self.abrir('/social/')
        campo = self.navegador.find_element(By.CSS_SELECTOR, '#rs-form-post textarea')
        campo.send_keys('Reaproveitamos 40 kg de retalhos neste mes #ESG')
        self.navegador.find_element(By.CSS_SELECTOR, '#rs-form-post button[type="submit"]').click()
        self.esperar_texto('Publicação criada com sucesso')
        self.espera.until(lambda d: 'Reaproveitamos 40 kg de retalhos' in self.posts()[0].text)
        primeiro = self.posts()[0]
        self.assertIn('Reaproveitamos 40 kg de retalhos', primeiro.text)
        self.assertIn('Aurora Confecções', primeiro.text)
        self.assertIn('atrás', primeiro.text)

    def test_cenario_2_comentar_em_publicacao_de_outra_empresa(self):
        outra = get_user_model().objects.create_user('outra', password=SENHA, first_name='Outra Malhas')
        post = Post.objects.create(autor=outra, conteudo='Como reduzir o consumo de agua?')
        self.abrir(f'/social/post/{post.pk}/')
        campo = self.navegador.find_element(By.CSS_SELECTOR, '#comentarios textarea')
        campo.send_keys('Comecamos medindo o hidrometro toda semana.')
        self.navegador.find_element(By.CSS_SELECTOR, '#comentarios button[type="submit"]').click()
        self.esperar_texto('Comentário publicado')
        self.espera.until(lambda d: 'Comecamos medindo' in d.find_element(By.CSS_SELECTOR, '#comentarios').text)
        comentarios = self.navegador.find_elements(By.CSS_SELECTOR, '.rs-comentario')
        self.assertEqual(len(comentarios), 1)
        self.assertIn('Comecamos medindo o hidrometro', comentarios[0].text)

    def test_cenario_3_publicacao_vazia_nao_e_publicada(self):
        self.abrir('/social/')
        self.navegador.find_element(By.CSS_SELECTOR, '#rs-form-post button[type="submit"]').click()
        self.espera.until(lambda d: d.find_elements(By.CSS_SELECTOR, '#rs-form-post .errorlist, #rs-form-post .rs-erro, .rs-erro-cliente:not([hidden])'))
        self.assertEqual(Post.objects.count(), 0)
