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
        resp = self.client.get(reverse("quem_somos"))
        self.assertNotContains(resp, "img/equipe/rodrigo.jpg")
        self.assertContains(resp, "ci-user")
