from django.test import TestCase
from django.urls import reverse

from .models import Atividade


class QuadroAtividadesTests(TestCase):
    def test_criar_atividade_vai_para_aguardando(self):
        resp = self.client.post(reverse("quadro_atividades"), {"titulo": "Reciclar retalhos", "categoria": "ambiental"})
        self.assertRedirects(resp, reverse("quadro_atividades"))
        atividade = Atividade.objects.get()
        self.assertEqual(atividade.status, "aguardando")

    def test_titulo_obrigatorio(self):
        resp = self.client.post(reverse("quadro_atividades"), {"titulo": "", "categoria": "social"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "O título da atividade é obrigatório.")
        self.assertEqual(Atividade.objects.count(), 0)

    def test_mudar_status_atualiza_colunas(self):
        a = Atividade.objects.create(titulo="Treinar equipe", categoria="social")
        self.client.post(reverse("mudar_status_atividade", args=[a.pk]), {"status": "andamento"})
        a.refresh_from_db()
        self.assertEqual(a.status, "andamento")
        resp = self.client.get(reverse("quadro_atividades"))
        colunas = {c["chave"]: c["atividades"] for c in resp.context["colunas"]}
        self.assertEqual(len(colunas["aguardando"]), 0)
        self.assertEqual(len(colunas["andamento"]), 1)

    def test_status_invalido_ignorado(self):
        a = Atividade.objects.create(titulo="X", categoria="governanca")
        self.client.post(reverse("mudar_status_atividade", args=[a.pk]), {"status": "xyz"})
        a.refresh_from_db()
        self.assertEqual(a.status, "aguardando")

    def test_deletar(self):
        a = Atividade.objects.create(titulo="X", categoria="governanca")
        self.client.post(reverse("deletar_atividade", args=[a.pk]))
        self.assertEqual(Atividade.objects.count(), 0)
