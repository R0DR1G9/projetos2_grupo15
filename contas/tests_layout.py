from django.test import TestCase
from django.urls import reverse


class PaginasDeAcessoSemMenuTests(TestCase):
    def test_login_e_cadastro_nao_mostram_o_menu_lateral(self):
        for nome in ("login", "cadastro"):
            resposta = self.client.get(reverse(nome))
            self.assertEqual(resposta.status_code, 200)
            self.assertContains(resposta, "auth-marca")
            self.assertNotContains(resposta, 'id="menuLateral"')
            self.assertNotContains(resposta, 'id="alternarMenu"')

    def test_demais_paginas_continuam_com_menu_recolhivel(self):
        resposta = self.client.get(reverse("sobre"))
        self.assertContains(resposta, 'id="menuLateral"')
        self.assertContains(resposta, 'id="alternarMenu"')
