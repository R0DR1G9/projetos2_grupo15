from selenium.webdriver.common.by import By

from biblioteca.models import Conteudo

from .base import NavegadorTestCase


class BibliotecaE2ETests(NavegadorTestCase):
    def setUp(self):
        super().setUp()
        Conteudo.objects.all().delete()
        Conteudo.objects.create(titulo='Reaproveitar retalhos', descricao='Passos para as sobras', categoria='ambiental',
                                tipo='video', link_video='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        Conteudo.objects.create(titulo='Equipe segura', descricao='Boas praticas', categoria='social', tipo='texto',
                                texto='Mantenha as saidas livres.')

    def cartoes(self):
        return self.navegador.find_elements(By.CSS_SELECTOR, '.bib-cartao')

    def test_cenario_1_listar_conteudos(self):
        self.abrir('/biblioteca/')
        self.esperar_texto('Reaproveitar retalhos')
        self.assertEqual(len(self.cartoes()), 2)
        pagina = self.texto_da_pagina()
        for esperado in ('Reaproveitar retalhos', 'Ambiental', 'Vídeo', 'Equipe segura', 'Social', 'Texto'):
            self.assertIn(esperado, pagina)

    def test_cenario_2_filtrar_por_categoria(self):
        self.abrir('/biblioteca/')
        self.navegador.find_element(By.LINK_TEXT, 'Ambiental').click()
        self.espera.until(lambda d: len(self.cartoes()) == 1)
        self.esperar_texto('Reaproveitar retalhos')
        pagina = self.texto_da_pagina()
        self.assertIn('Reaproveitar retalhos', pagina)
        self.assertNotIn('Equipe segura', pagina)

    def test_cenario_3_assistir_a_um_video(self):
        self.abrir('/biblioteca/')
        self.navegador.find_element(By.PARTIAL_LINK_TEXT, 'Reaproveitar retalhos').click()
        self.espera.until(lambda d: '/biblioteca/' in d.current_url and d.current_url.rstrip('/').split('/')[-1].isdigit())
        quadro = self.navegador.find_element(By.CSS_SELECTOR, '.bib-video iframe')
        self.assertIn('youtube-nocookie.com/embed/dQw4w9WgXcQ', quadro.get_attribute('src'))
        self.assertIn('Passos para as sobras', self.texto_da_pagina())
