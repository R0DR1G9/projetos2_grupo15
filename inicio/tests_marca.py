from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse


class MarcaTests(TestCase):
    def test_arquivo_da_logo_existe(self):
        self.assertIsNotNone(finders.find('img/logo.svg'))

    def test_menu_mostra_nome_e_logo_do_vastra(self):
        usuario = get_user_model().objects.create_user('gestora', password='senha-forte-123', first_name='Aurora')
        self.client.force_login(usuario)
        resp = self.client.get(reverse('inicio'))
        self.assertContains(resp, '<strong>Vastra</strong>', html=True)
        self.assertContains(resp, 'class="marca-logo"')
        self.assertContains(resp, 'rel="icon"')
        self.assertContains(resp, 'img/logo.svg')

    def test_paginas_de_login_tem_o_icone_da_aba(self):
        resp = self.client.get(reverse('login'))
        self.assertContains(resp, 'rel="icon"')
