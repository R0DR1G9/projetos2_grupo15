from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .views import EQUIPE


class QuemSomosTests(TestCase):
    def test_lista_todos_os_integrantes(self):
        resp = self.client.get(reverse("quem_somos"))
        self.assertEqual(resp.status_code, 200)
        for nome, _ in EQUIPE:
            self.assertContains(resp, nome)

    def test_integrante_com_foto_usa_imagem(self):
        resp = self.client.get(reverse("quem_somos"))
        self.assertContains(resp, "img/equipe/ana-beatriz.jpg")
        self.assertContains(resp, 'alt="Foto de Ana Beatriz Pedrosa"')

    def test_integrante_sem_foto_usa_icone(self):
        with patch("institucional.views.finders.find", return_value=None):
            resp = self.client.get(reverse("quem_somos"))
        self.assertNotContains(resp, "img/equipe/")
        self.assertContains(resp, "ci-user")

    def test_todos_os_integrantes_tem_foto(self):
        resp = self.client.get(reverse("quem_somos"))
        for _, slug in EQUIPE:
            self.assertContains(resp, f"img/equipe/{slug}.jpg")

    def test_nao_mostra_texto_introdutorio(self):
        resp = self.client.get(reverse("quem_somos"))
        self.assertNotContains(resp, "Somos um grupo de estudantes")
