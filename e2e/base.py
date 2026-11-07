import os
import shutil

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SENHA = 'senha-forte-123'


class NavegadorTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opcoes = Options()
        opcoes.add_argument('--headless=new')
        opcoes.add_argument('--no-sandbox')
        opcoes.add_argument('--disable-dev-shm-usage')
        opcoes.add_argument('--window-size=1400,1000')
        if os.environ.get('CHROME_BIN'):
            opcoes.binary_location = os.environ['CHROME_BIN']
        caminho = os.environ.get('CHROMEDRIVER_PATH') or shutil.which('chromedriver')
        servico = Service(executable_path=caminho) if caminho else Service()
        cls.navegador = webdriver.Chrome(service=servico, options=opcoes)
        cls.navegador.implicitly_wait(3)
        cls.espera = WebDriverWait(cls.navegador, 10)

    @classmethod
    def tearDownClass(cls):
        cls.navegador.quit()
        super().tearDownClass()

    def setUp(self):
        self.usuario = get_user_model().objects.create_user('gestora', password=SENHA, first_name='Aurora Confecções')
        self.entrar('gestora')

    def abrir(self, caminho):
        self.navegador.get(self.live_server_url + caminho)

    def entrar(self, usuario, senha=SENHA):
        self.navegador.delete_all_cookies()
        self.abrir('/login/')
        self.navegador.find_element(By.NAME, 'username').send_keys(usuario)
        self.navegador.find_element(By.NAME, 'password').send_keys(senha)
        self.navegador.find_element(By.CSS_SELECTOR, 'form button[type="submit"]').click()
        self.espera.until(lambda d: '/login/' not in d.current_url)

    def esperar_texto(self, texto):
        self.espera.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), texto))

    def texto_da_pagina(self):
        return self.navegador.find_element(By.TAG_NAME, 'body').text
