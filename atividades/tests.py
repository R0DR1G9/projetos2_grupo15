from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Atividade


def novo_usuario(nome='gestora'):
    return get_user_model().objects.create_user(nome, password='senha-forte-123', first_name=nome.title())


class QuadroAtividadesTests(TestCase):
    def setUp(self):
        self.user = novo_usuario()
        self.client.force_login(self.user)

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
        a = Atividade.objects.create(usuario=self.user, titulo="Treinar equipe", categoria="social")
        self.client.post(reverse("mudar_status_atividade", args=[a.pk]), {"status": "andamento"})
        a.refresh_from_db()
        self.assertEqual(a.status, "andamento")
        resp = self.client.get(reverse("quadro_atividades"))
        colunas = {c["chave"]: c["atividades"] for c in resp.context["colunas"]}
        self.assertEqual(len(colunas["aguardando"]), 0)
        self.assertEqual(len(colunas["andamento"]), 1)

    def test_status_invalido_ignorado(self):
        a = Atividade.objects.create(usuario=self.user, titulo="X", categoria="governanca")
        self.client.post(reverse("mudar_status_atividade", args=[a.pk]), {"status": "xyz"})
        a.refresh_from_db()
        self.assertEqual(a.status, "aguardando")

    def test_deletar(self):
        a = Atividade.objects.create(usuario=self.user, titulo="X", categoria="governanca")
        self.client.post(reverse("deletar_atividade", args=[a.pk]))
        self.assertEqual(Atividade.objects.count(), 0)


class ArrastarCartoesTests(TestCase):
    def setUp(self):
        self.user = novo_usuario()
        self.client.force_login(self.user)

    def test_colunas_e_cartoes_tem_ganchos_para_arrastar(self):
        Atividade.objects.create(usuario=self.user, titulo="Treinar equipe", categoria="social")
        resp = self.client.get(reverse("quadro_atividades"))
        for chave in ("aguardando", "andamento", "concluido"):
            self.assertContains(resp, f'data-coluna="{chave}"')
        self.assertContains(resp, "data-atividade")
        self.assertContains(resp, "js/quadro.js")


class IsolamentoPorEmpresaTests(TestCase):
    def setUp(self):
        self.dona = novo_usuario('dona')
        self.outra = novo_usuario('outra')
        self.atividade = Atividade.objects.create(usuario=self.dona, titulo="So da dona", categoria="social")

    def test_quadro_exige_login(self):
        resp = self.client.get(reverse("quadro_atividades"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp['Location'])

    def test_conta_nova_ve_o_quadro_vazio(self):
        self.client.force_login(self.outra)
        resp = self.client.get(reverse("quadro_atividades"))
        self.assertNotContains(resp, "So da dona")
        self.assertEqual(sum(len(c["atividades"]) for c in resp.context["colunas"]), 0)

    def test_atividade_criada_fica_com_quem_criou(self):
        self.client.force_login(self.outra)
        self.client.post(reverse("quadro_atividades"), {"titulo": "Minha acao", "categoria": "ambiental"})
        self.assertEqual(Atividade.objects.get(titulo="Minha acao").usuario, self.outra)

    def test_nao_mexe_na_atividade_de_outra_empresa(self):
        self.client.force_login(self.outra)
        self.assertEqual(self.client.post(reverse("mudar_status_atividade", args=[self.atividade.pk]), {"status": "andamento"}).status_code, 404)
        self.assertEqual(self.client.post(reverse("deletar_atividade", args=[self.atividade.pk])).status_code, 404)
        self.atividade.refresh_from_db()
        self.assertEqual(self.atividade.status, "aguardando")


class PrazoEResponsavelTests(TestCase):
    def setUp(self):
        self.user = novo_usuario()
        self.client.force_login(self.user)
        self.hoje = timezone.localdate()

    def cria(self, dias=None, **extra):
        prazo = None if dias is None else self.hoje + timedelta(days=dias)
        return Atividade.objects.create(usuario=self.user, titulo="Acao", categoria="social", prazo=prazo, **extra)

    def test_criar_com_prazo_e_responsavel(self):
        data = self.hoje + timedelta(days=10)
        self.client.post(reverse("quadro_atividades"), {
            "titulo": "Trocar lampadas", "categoria": "ambiental", "prazo": data.isoformat(), "responsavel": "Marina",
        })
        a = Atividade.objects.get()
        self.assertEqual(a.prazo, data)
        self.assertEqual(a.responsavel, "Marina")
        resp = self.client.get(reverse("quadro_atividades"))
        self.assertContains(resp, "Responsável: Marina")
        self.assertContains(resp, f"Prazo: {data:%d/%m/%Y}")

    def test_prazo_e_responsavel_sao_opcionais(self):
        self.client.post(reverse("quadro_atividades"), {"titulo": "Sem prazo", "categoria": "social"})
        self.assertIsNone(Atividade.objects.get().prazo)

    def test_prazo_no_passado_e_recusado_ao_criar(self):
        ontem = self.hoje - timedelta(days=1)
        resp = self.client.post(reverse("quadro_atividades"), {"titulo": "X", "categoria": "social", "prazo": ontem.isoformat()})
        self.assertContains(resp, "O prazo não pode ser uma data que já passou.")
        self.assertEqual(Atividade.objects.count(), 0)

    def test_editar_prazo_e_responsavel_do_cartao(self):
        a = self.cria()
        data = self.hoje + timedelta(days=5)
        resp = self.client.post(reverse("editar_detalhes_atividade", args=[a.pk]), {"prazo": data.isoformat(), "responsavel": "Carlos"})
        self.assertRedirects(resp, reverse("quadro_atividades"))
        a.refresh_from_db()
        self.assertEqual((a.prazo, a.responsavel), (data, "Carlos"))

    def test_editar_com_data_invalida_nao_altera(self):
        a = self.cria(dias=4)
        self.client.post(reverse("editar_detalhes_atividade", args=[a.pk]), {"prazo": "32/13/2026", "responsavel": "Z"})
        a.refresh_from_db()
        self.assertEqual(a.prazo, self.hoje + timedelta(days=4))

    def test_nao_edita_atividade_de_outra_empresa(self):
        outra = novo_usuario('outra')
        a = Atividade.objects.create(usuario=outra, titulo="Dela", categoria="social")
        resp = self.client.post(reverse("editar_detalhes_atividade", args=[a.pk]), {"responsavel": "Invasor"})
        self.assertEqual(resp.status_code, 404)

    def test_situacao_e_rotulos_do_prazo(self):
        self.assertEqual(self.cria(dias=-2).rotulo_prazo, "Atrasada há 2 dias")
        self.assertEqual(self.cria(dias=-1).rotulo_prazo, "Atrasada há 1 dia")
        self.assertEqual(self.cria(dias=0).rotulo_prazo, "Vence hoje")
        self.assertEqual(self.cria(dias=1).rotulo_prazo, "Vence amanhã")
        self.assertEqual(self.cria(dias=3).rotulo_prazo, "Vence em 3 dias")
        self.assertEqual(self.cria(dias=3).situacao_prazo, "proxima")
        self.assertEqual(self.cria(dias=4).situacao_prazo, "no_prazo")
        self.assertEqual(self.cria().situacao_prazo, "")

    def test_concluida_nao_fica_atrasada(self):
        a = self.cria(dias=-5)
        a.status = "concluido"
        self.assertEqual(a.situacao_prazo, "")

    def test_cartoes_ordenados_por_prazo_mais_proximo(self):
        Atividade.objects.create(usuario=self.user, titulo="Sem prazo", categoria="social")
        longe = Atividade.objects.create(usuario=self.user, titulo="Longe", categoria="social", prazo=self.hoje + timedelta(days=20))
        perto = Atividade.objects.create(usuario=self.user, titulo="Perto", categoria="social", prazo=self.hoje + timedelta(days=2))
        resp = self.client.get(reverse("quadro_atividades"))
        titulos = [a.titulo for a in resp.context["colunas"][0]["atividades"]]
        self.assertEqual(titulos, ["Perto", "Longe", "Sem prazo"])
