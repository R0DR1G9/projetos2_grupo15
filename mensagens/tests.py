from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .context_processors import nao_lidas
from .models import Conversa, Mensagem

User = get_user_model()
SENHA = "senha-segura-123"
AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user("ana", password=SENHA)
        cls.bia = User.objects.create_user("bia", password=SENHA)
        cls.caio = User.objects.create_user("caio", password=SENHA)

    def setUp(self):
        self.client.force_login(self.ana)

    def enviar(self, de, para, texto):
        conv = Conversa.entre(de, para, criar=True)
        return Mensagem.objects.create(conversa=conv, remetente=de, texto=texto)

    def url_conversa(self, username):
        return reverse("mensagens:conversa", args=[username])


class AcessoTests(BaseTestCase):
    def test_exige_login(self):
        self.client.logout()
        for url in [
            reverse("mensagens:caixa"),
            self.url_conversa("bia"),
            reverse("mensagens:novas", args=["bia"]),
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_telas_carregam(self):
        self.enviar(self.bia, self.ana, "oi ana")
        for url in [reverse("mensagens:caixa"), self.url_conversa("bia"), reverse("mensagens:caixa") + "?q=bi"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_usuario_inexistente_ou_inativo_da_404(self):
        self.assertEqual(self.client.get(self.url_conversa("fantasma")).status_code, 404)
        User.objects.create_user("inativo", password=SENHA, is_active=False)
        self.assertEqual(self.client.get(self.url_conversa("inativo")).status_code, 404)

    def test_nao_conversa_consigo_mesmo(self):
        resp = self.client.get(self.url_conversa("ana"))
        self.assertRedirects(resp, reverse("mensagens:caixa"))
        self.client.post(self.url_conversa("ana"), {"texto": "oi"})
        self.assertEqual(Mensagem.objects.count(), 0)


class EnvioTests(BaseTestCase):
    def test_enviar_cria_conversa_e_mensagem(self):
        resp = self.client.post(self.url_conversa("bia"), {"texto": "Olá, Bia!"})
        self.assertRedirects(resp, self.url_conversa("bia") + "#ms-fim", fetch_redirect_response=False)
        msg = Mensagem.objects.get()
        self.assertEqual((msg.remetente, msg.texto), (self.ana, "Olá, Bia!"))
        self.assertEqual(Conversa.objects.count(), 1)

    def test_a_para_b_e_b_para_a_usam_a_mesma_conversa(self):
        self.client.post(self.url_conversa("bia"), {"texto": "oi"})
        self.client.force_login(self.bia)
        self.client.post(self.url_conversa("ana"), {"texto": "oi de volta"})
        self.assertEqual(Conversa.objects.count(), 1)
        self.assertEqual(Mensagem.objects.count(), 2)

    def test_abrir_conversa_nao_cria_nada(self):
        self.client.get(self.url_conversa("bia"))
        self.assertEqual(Conversa.objects.count(), 0)

    def test_mensagem_vazia_e_rejeitada(self):
        resp = self.client.post(self.url_conversa("bia"), {"texto": "   "})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Mensagem.objects.count(), 0)

    def test_mensagem_acima_do_limite_e_rejeitada(self):
        self.client.post(self.url_conversa("bia"), {"texto": "a" * 1001})
        self.assertEqual(Mensagem.objects.count(), 0)

    def test_envio_ajax_devolve_json_com_html(self):
        resp = self.client.post(self.url_conversa("bia"), {"texto": "via ajax"}, **AJAX)
        self.assertEqual(resp.status_code, 200)
        dados = resp.json()
        msg = Mensagem.objects.get()
        self.assertEqual(dados["id"], msg.pk)
        self.assertEqual(dados["status"], "Enviado")
        self.assertIn("via ajax", dados["html"])
        self.assertIn(f'data-msg-id="{msg.pk}"', dados["html"])

    def test_envio_ajax_invalido_devolve_400(self):
        resp = self.client.post(self.url_conversa("bia"), {"texto": ""}, **AJAX)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("erro", resp.json())

    def test_html_e_escapado(self):
        self.client.post(self.url_conversa("bia"), {"texto": "<script>alert(1)</script>"})
        html = self.client.get(self.url_conversa("bia")).content.decode()
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)

    def test_quebra_de_linha_e_preservada(self):
        self.client.post(self.url_conversa("bia"), {"texto": "linha 1\nlinha 2"})
        self.assertContains(self.client.get(self.url_conversa("bia")), "linha 1<br>linha 2")


class CaixaTests(BaseTestCase):
    def test_lista_conversas_com_ultima_mensagem_e_nao_lidas(self):
        self.enviar(self.bia, self.ana, "primeira")
        self.enviar(self.bia, self.ana, "segunda da bia")
        self.enviar(self.ana, self.caio, "oi caio")
        resp = self.client.get(reverse("mensagens:caixa"))
        conversas = resp.context["conversas"]
        self.assertEqual(len(conversas), 2)
        por_usuario = {c.outro.username: c for c in conversas}
        self.assertEqual(por_usuario["bia"].nao_lidas, 2)
        self.assertEqual(por_usuario["bia"].ultima_texto, "segunda da bia")
        self.assertEqual(por_usuario["caio"].nao_lidas, 0)
        self.assertContains(resp, "Você: oi caio")

    def test_ordena_pela_mensagem_mais_recente(self):
        self.enviar(self.bia, self.ana, "antiga")
        self.enviar(self.caio, self.ana, "mais nova")
        ordem = [c.outro.username for c in self.client.get(reverse("mensagens:caixa")).context["conversas"]]
        self.assertEqual(ordem, ["caio", "bia"])

    def test_conversa_sem_mensagens_nao_aparece(self):
        Conversa.entre(self.ana, self.bia, criar=True)
        self.assertEqual(self.client.get(reverse("mensagens:caixa")).context["conversas"], [])

    def test_nao_mostra_conversas_de_outras_pessoas(self):
        self.enviar(self.bia, self.caio, "segredo entre bia e caio")
        resp = self.client.get(reverse("mensagens:caixa"))
        self.assertEqual(resp.context["conversas"], [])
        self.assertNotContains(resp, "segredo entre bia e caio")

    def test_busca_de_pessoas(self):
        resp = self.client.get(reverse("mensagens:caixa") + "?q=bi")
        nomes = [u.username for u in resp.context["pessoas"]]
        self.assertEqual(nomes, ["bia"])
        resp = self.client.get(reverse("mensagens:caixa") + "?q=ana")
        self.assertEqual(list(resp.context["pessoas"]), [])  # não lista a si mesmo


class LeituraTests(BaseTestCase):
    def test_abrir_conversa_marca_recebidas_como_lidas(self):
        m = self.enviar(self.bia, self.ana, "oi")
        self.assertIsNone(m.lida_em)
        self.client.get(self.url_conversa("bia"))
        m.refresh_from_db()
        self.assertIsNotNone(m.lida_em)

    def test_minhas_mensagens_nao_sao_marcadas_ao_abrir(self):
        m = self.enviar(self.ana, self.bia, "oi bia")
        self.client.get(self.url_conversa("bia"))
        m.refresh_from_db()
        self.assertIsNone(m.lida_em)

    def test_status_enviado_e_visto(self):
        self.client.post(self.url_conversa("bia"), {"texto": "oi"})
        self.assertEqual(self.client.get(self.url_conversa("bia")).context["status"], "Enviado")
        self.client.force_login(self.bia)
        self.client.get(self.url_conversa("ana"))  # bia lê
        self.client.force_login(self.ana)
        self.assertEqual(self.client.get(self.url_conversa("bia")).context["status"], "Visto")

    def test_sem_status_quando_a_ultima_e_dela(self):
        self.enviar(self.ana, self.bia, "oi")
        self.enviar(self.bia, self.ana, "oi ana")
        self.assertEqual(self.client.get(self.url_conversa("bia")).context["status"], "")

    def test_contador_do_menu(self):
        self.enviar(self.bia, self.ana, "1")
        self.enviar(self.caio, self.ana, "2")
        self.enviar(self.ana, self.bia, "minha")  # não conta
        req = RequestFactory().get("/")
        req.user = self.ana
        self.assertEqual(nao_lidas(req), {"mensagens_nao_lidas": 2})
        self.client.get(self.url_conversa("bia"))
        self.assertEqual(nao_lidas(req), {"mensagens_nao_lidas": 1})

    def test_contador_vazio_para_visitante(self):
        from django.contrib.auth.models import AnonymousUser

        req = RequestFactory().get("/")
        req.user = AnonymousUser()
        self.assertEqual(nao_lidas(req), {})


class NovasTests(BaseTestCase):
    def test_devolve_so_o_que_veio_depois(self):
        m1 = self.enviar(self.bia, self.ana, "antiga")
        m2 = self.enviar(self.bia, self.ana, "nova")
        dados = self.client.get(reverse("mensagens:novas", args=["bia"]) + f"?depois={m1.pk}", **AJAX).json()
        self.assertIn("nova", dados["html"])
        self.assertNotIn("antiga", dados["html"])
        self.assertEqual(dados["ultima"], m2.pk)

    def test_marca_como_lidas_e_atualiza_status_do_outro_lado(self):
        mine = self.enviar(self.ana, self.bia, "oi bia")
        self.client.force_login(self.bia)
        self.client.get(reverse("mensagens:novas", args=["ana"]) + "?depois=0")
        mine.refresh_from_db()
        self.assertIsNotNone(mine.lida_em)
        self.client.force_login(self.ana)
        dados = self.client.get(reverse("mensagens:novas", args=["bia"]) + f"?depois={mine.pk}").json()
        self.assertEqual(dados["status"], "Visto")

    def test_conversa_inexistente(self):
        dados = self.client.get(reverse("mensagens:novas", args=["bia"])).json()
        self.assertEqual(dados, {"html": "", "ultima": 0, "status": ""})

    def test_parametro_invalido_nao_quebra(self):
        self.enviar(self.bia, self.ana, "oi")
        resp = self.client.get(reverse("mensagens:novas", args=["bia"]) + "?depois=abc")
        self.assertEqual(resp.status_code, 200)

    def test_nao_vaza_conversa_de_terceiros(self):
        self.enviar(self.bia, self.caio, "segredo")
        dados = self.client.get(reverse("mensagens:novas", args=["bia"]) + "?depois=0").json()
        self.assertNotIn("segredo", dados["html"])


class PaginacaoEDesfazerTests(BaseTestCase):
    def test_mostra_as_ultimas_50_e_oferece_ver_mais(self):
        for i in range(55):
            self.enviar(self.bia, self.ana, f"msg-{i:02d}")
        resp = self.client.get(self.url_conversa("bia"))
        self.assertTrue(resp.context["tem_mais"])
        self.assertEqual(len(resp.context["mensagens"]), 50)
        self.assertContains(resp, "msg-54")
        self.assertNotContains(resp, "msg-04")
        self.assertContains(resp, "Ver mensagens anteriores")
        resp = self.client.get(self.url_conversa("bia") + "?limite=100")
        self.assertFalse(resp.context["tem_mais"])
        self.assertContains(resp, "msg-00")

    def test_ordem_cronologica(self):
        for t in ["um", "dois", "tres"]:
            self.enviar(self.bia, self.ana, t)
        textos = [m.texto for m in self.client.get(self.url_conversa("bia")).context["mensagens"]]
        self.assertEqual(textos, ["um", "dois", "tres"])

    def test_desfazer_envio_so_pelo_autor(self):
        m = self.enviar(self.ana, self.bia, "oops")
        url = reverse("mensagens:excluir", args=[m.pk])
        self.client.force_login(self.bia)  # destinatária não pode apagar
        self.assertEqual(self.client.post(url).status_code, 404)
        self.client.force_login(self.caio)  # terceiro também não
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertTrue(Mensagem.objects.filter(pk=m.pk).exists())
        self.client.force_login(self.ana)
        self.assertEqual(self.client.post(url, **AJAX).json(), {"ok": True})
        self.assertFalse(Mensagem.objects.filter(pk=m.pk).exists())

    def test_desfazer_exige_post(self):
        m = self.enviar(self.ana, self.bia, "x")
        self.assertEqual(self.client.get(reverse("mensagens:excluir", args=[m.pk])).status_code, 405)

    def test_desfazer_sem_ajax_redireciona_para_a_conversa(self):
        m = self.enviar(self.ana, self.bia, "x")
        resp = self.client.post(reverse("mensagens:excluir", args=[m.pk]))
        self.assertRedirects(resp, self.url_conversa("bia"), fetch_redirect_response=False)

    def test_excluir_usuario_remove_conversas(self):
        self.enviar(self.ana, self.bia, "x")
        self.bia.delete()
        self.assertEqual(Conversa.objects.count(), 0)
        self.assertEqual(Mensagem.objects.count(), 0)


class TelaTests(BaseTestCase):
    def test_conversa_traz_hooks_do_javascript(self):
        self.enviar(self.bia, self.ana, "oi")
        resp = self.client.get(self.url_conversa("bia"))
        for trecho in ['id="ms-mensagens"', 'id="ms-form"', "data-novas-url", "mensagens.js", 'id="ms-fim"']:
            self.assertContains(resp, trecho)

    def test_botao_desfazer_so_nas_minhas(self):
        self.enviar(self.bia, self.ana, "da bia")
        self.enviar(self.ana, self.bia, "minha")
        html = self.client.get(self.url_conversa("bia")).content.decode()
        self.assertEqual(html.count('class="ms-desfazer"'), 1)

    def test_link_para_o_perfil_na_rede_social(self):
        resp = self.client.get(self.url_conversa("bia"))
        self.assertContains(resp, reverse("rede_social:perfil", args=["bia"]))
