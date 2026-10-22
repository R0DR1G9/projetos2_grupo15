import shutil
import tempfile
from io import BytesIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Comentario, Curtida, Hashtag, Post, Seguimento

User = get_user_model()
SENHA = "senha-segura-123"


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user("ana", password=SENHA)
        cls.bia = User.objects.create_user("bia", password=SENHA)
        cls.caio = User.objects.create_user("caio", password=SENHA)

    def setUp(self):
        self.client.force_login(self.ana)


class AcessoETests(BaseTestCase):
    def test_exige_login(self):
        self.client.logout()
        resp = self.client.get(reverse("rede_social:feed"))
        self.assertEqual(resp.status_code, 302)

    def test_perfil_criado_automaticamente(self):
        self.assertTrue(hasattr(self.ana, "perfil_social"))

    def test_paginas_principais_carregam(self):
        post = Post.objects.create(autor=self.bia, conteudo="Olá #esg")
        urls = [
            reverse("rede_social:feed"),
            reverse("rede_social:detalhe_post", args=[post.pk]),
            reverse("rede_social:perfil", args=["bia"]),
            reverse("rede_social:editar_perfil"),
            reverse("rede_social:hashtag", args=["esg"]),
            reverse("rede_social:buscar") + "?q=esg",
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)


class PostTests(BaseTestCase):
    def test_criar_post_extrai_hashtags(self):
        resp = self.client.post(
            reverse("rede_social:feed"),
            {"conteudo": "Meta de #Carbono e #ESG", "pilar": "ambiental"},
        )
        self.assertRedirects(resp, reverse("rede_social:feed"))
        post = Post.objects.get()
        self.assertEqual(post.autor, self.ana)
        self.assertEqual(post.pilar, "ambiental")
        self.assertEqual({h.nome for h in post.hashtags.all()}, {"carbono", "esg"})

    def test_post_vazio_e_rejeitado(self):
        resp = self.client.post(reverse("rede_social:feed"), {"conteudo": "   ", "pilar": "geral"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)

    def test_post_acima_de_500_caracteres_e_rejeitado(self):
        self.client.post(reverse("rede_social:feed"), {"conteudo": "a" * 501, "pilar": "geral"})
        self.assertEqual(Post.objects.count(), 0)

    def test_editar_conteudo_atualiza_hashtags(self):
        post = Post.objects.create(autor=self.ana, conteudo="#um")
        post.conteudo = "#dois"
        post.save()
        self.assertEqual([h.nome for h in post.hashtags.all()], ["dois"])

    def test_excluir_apenas_autor(self):
        post = Post.objects.create(autor=self.bia, conteudo="x")
        url = reverse("rede_social:excluir_post", args=[post.pk])
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())
        self.client.force_login(self.bia)
        self.client.post(url)
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_post_oculto_nao_aparece(self):
        Post.objects.create(autor=self.bia, conteudo="segredo-moderado", visivel=False)
        resp = self.client.get(reverse("rede_social:feed"))
        self.assertNotContains(resp, "segredo-moderado")


class InteracaoTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(autor=self.bia, conteudo="conteúdo da bia")

    def test_curtir_alterna(self):
        url = reverse("rede_social:curtir", args=[self.post.pk])
        self.client.post(url)
        self.assertEqual(Curtida.objects.count(), 1)
        self.client.post(url)
        self.assertEqual(Curtida.objects.count(), 0)

    def test_curtir_ajax_retorna_json_sem_redirecionar(self):
        url = reverse("rede_social:curtir", args=[self.post.pk])
        ajax = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        resp = self.client.post(url, **ajax)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"curtido": True, "total": 1})
        self.assertEqual(Curtida.objects.count(), 1)
        resp = self.client.post(url, **ajax)
        self.assertEqual(resp.json(), {"curtido": False, "total": 0})
        self.assertEqual(Curtida.objects.count(), 0)

    def test_curtir_sem_ajax_continua_redirecionando(self):
        resp = self.client.post(reverse("rede_social:curtir", args=[self.post.pk]))
        self.assertEqual(resp.status_code, 302)

    def test_ajax_conta_curtidas_de_todos_os_usuarios(self):
        Curtida.objects.create(post=self.post, usuario=self.caio)
        resp = self.client.post(
            reverse("rede_social:curtir", args=[self.post.pk]), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.json(), {"curtido": True, "total": 2})

    def test_formulario_de_curtir_e_marcado_para_ajax(self):
        resp = self.client.get(reverse("rede_social:feed"))
        self.assertContains(resp, "data-rs-curtir")
        self.assertContains(resp, 'aria-pressed="false"')

    def test_curtir_exige_post(self):
        resp = self.client.get(reverse("rede_social:curtir", args=[self.post.pk]))
        self.assertEqual(resp.status_code, 405)

    def test_next_externo_e_ignorado(self):
        resp = self.client.post(
            reverse("rede_social:curtir", args=[self.post.pk]), {"next": "https://evil.example/"}
        )
        self.assertNotIn("evil.example", resp["Location"])

    def test_repostar_alterna(self):
        url = reverse("rede_social:repostar", args=[self.post.pk])
        self.client.post(url)
        self.assertTrue(Post.objects.filter(autor=self.ana, repost_de=self.post).exists())
        self.client.post(url)
        self.assertFalse(Post.objects.filter(autor=self.ana, repost_de=self.post).exists())

    def test_nao_reposta_o_proprio_post(self):
        meu = Post.objects.create(autor=self.ana, conteudo="meu")
        self.client.post(reverse("rede_social:repostar", args=[meu.pk]))
        self.assertFalse(Post.objects.filter(repost_de=meu).exists())

    def test_repost_aparece_no_feed_com_conteudo_original(self):
        self.client.post(reverse("rede_social:repostar", args=[self.post.pk]))
        resp = self.client.get(reverse("rede_social:feed"))
        self.assertContains(resp, "repostou")
        self.assertContains(resp, "conteúdo da bia")

    def test_comentar(self):
        url = reverse("rede_social:detalhe_post", args=[self.post.pk])
        self.client.post(url, {"conteudo": "Ótima iniciativa!"})
        self.assertEqual(Comentario.objects.get().autor, self.ana)
        self.assertContains(self.client.get(url), "Ótima iniciativa!")

    def test_metricas_no_feed(self):
        Curtida.objects.create(post=self.post, usuario=self.ana)
        Curtida.objects.create(post=self.post, usuario=self.caio)
        Comentario.objects.create(post=self.post, autor=self.caio, conteudo="oi")
        resp = self.client.get(reverse("rede_social:feed"))
        self.assertContains(resp, "Curtido (2)")
        self.assertContains(resp, "Comentar (1)")


class SeguirEFeedTests(BaseTestCase):
    def test_seguir_alterna(self):
        url = reverse("rede_social:seguir", args=["bia"])
        self.client.post(url)
        self.assertTrue(Seguimento.objects.filter(seguidor=self.ana, seguido=self.bia).exists())
        self.client.post(url)
        self.assertFalse(Seguimento.objects.exists())

    def test_nao_segue_a_si_mesmo(self):
        self.client.post(reverse("rede_social:seguir", args=["ana"]))
        self.assertFalse(Seguimento.objects.exists())

    def test_aba_seguindo(self):
        Post.objects.create(autor=self.bia, conteudo="post-da-bia")
        Post.objects.create(autor=self.caio, conteudo="post-do-caio")
        Seguimento.objects.create(seguidor=self.ana, seguido=self.bia)
        resp = self.client.get(reverse("rede_social:feed") + "?aba=seguindo")
        self.assertContains(resp, "post-da-bia")
        self.assertNotContains(resp, "post-do-caio")

    def test_aba_empresa(self):
        for usuario, empresa in [(self.ana, "Acme"), (self.bia, "acme"), (self.caio, "Outra")]:
            usuario.perfil_social.empresa = empresa
            usuario.perfil_social.save()
        Post.objects.create(autor=self.bia, conteudo="post-da-bia")
        Post.objects.create(autor=self.caio, conteudo="post-do-caio")
        resp = self.client.get(reverse("rede_social:feed") + "?aba=empresa")
        self.assertContains(resp, "post-da-bia")
        self.assertNotContains(resp, "post-do-caio")

    def test_filtro_por_pilar(self):
        Post.objects.create(autor=self.bia, conteudo="post-amb", pilar="ambiental")
        Post.objects.create(autor=self.bia, conteudo="post-soc", pilar="social")
        resp = self.client.get(reverse("rede_social:feed") + "?pilar=ambiental")
        self.assertContains(resp, "post-amb")
        self.assertNotContains(resp, "post-soc")

    def test_editar_perfil(self):
        self.client.post(
            reverse("rede_social:editar_perfil"),
            {"nome_exibicao": "Ana Souza", "empresa": "Acme", "cargo": "Analista ESG", "bio": "", "site": ""},
        )
        self.ana.perfil_social.refresh_from_db()
        self.assertEqual(self.ana.perfil_social.empresa, "Acme")


class FiltroLinkificarTests(TestCase):
    def render(self, texto):
        tpl = Template("{% load rede_social_tags %}{{ t|linkificar }}")
        return tpl.render(Context({"t": texto}))

    def test_escapa_html(self):
        saida = self.render("<script>alert(1)</script> #esg")
        self.assertNotIn("<script>", saida)
        self.assertIn(reverse("rede_social:hashtag", args=["esg"]), saida)

    def test_apostrofo_nao_vira_hashtag(self):
        saida = self.render("it's fine")
        self.assertNotIn("hashtag", saida)
        self.assertFalse(Hashtag.objects.exists())

    def test_quebra_de_linha(self):
        self.assertIn("<br>", self.render("a\nb"))


class IntegracaoLayoutTests(BaseTestCase):
    def test_paginas_usam_layout_do_projeto_e_css_com_escopo(self):
        resp = self.client.get(reverse("rede_social:feed"))
        self.assertContains(resp, "rede_social.css")
        self.assertContains(resp, 'class="rs"')
        self.assertContains(resp, "rs-card")
        self.assertNotContains(resp, 'class="card ')   # sem classes genéricas que conflitem com Bootstrap


# --------------------------------------------------------------------------- imagens nos posts
MEDIA_TESTE = tempfile.mkdtemp(prefix="rs_media_")


def gerar_imagem(nome="foto.png", formato="PNG", tamanho=(20, 20)):
    buf = BytesIO()
    Image.new("RGB", tamanho, "green").save(buf, format=formato)
    return SimpleUploadedFile(nome, buf.getvalue(), content_type=f"image/{formato.lower()}")


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class ImagemPostTests(BaseTestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)

    def postar(self, **dados):
        dados = {"conteudo": "", "pilar": "geral", **dados}
        return self.client.post(reverse("rede_social:feed"), dados)

    def test_publicar_com_imagem(self):
        resp = self.postar(conteudo="Plantio de árvores #ESG", imagem=gerar_imagem())
        self.assertRedirects(resp, reverse("rede_social:feed"))
        post = Post.objects.get()
        self.assertTrue(post.imagem.name.startswith("rede_social/posts/"))
        self.assertTrue(post.imagem.name.endswith(".png"))
        self.assertNotIn("foto", post.imagem.name)  # nome original não é preservado
        self.assertTrue(default_storage.exists(post.imagem.name))
        self.assertEqual({h.nome for h in post.hashtags.all()}, {"esg"})

    def test_publicar_apenas_imagem(self):
        self.postar(imagem=gerar_imagem())
        post = Post.objects.get()
        self.assertEqual(post.conteudo, "")
        self.assertTrue(post.imagem)
        self.assertIn("[imagem]", str(post))

    def test_sem_texto_e_sem_imagem_e_rejeitado(self):
        resp = self.postar(conteudo="   ")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)

    def test_arquivo_que_nao_e_imagem_e_rejeitado(self):
        falso = SimpleUploadedFile("falso.png", b"isto nao e uma imagem", content_type="image/png")
        resp = self.postar(conteudo="oi", imagem=falso)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("imagem", resp.context["form"].errors)
        self.assertEqual(Post.objects.count(), 0)

    def test_extensao_nao_permitida_e_rejeitada(self):
        resp = self.postar(conteudo="oi", imagem=gerar_imagem("foto.bmp", "BMP"))
        self.assertIn("imagem", resp.context["form"].errors)
        self.assertEqual(Post.objects.count(), 0)

    def test_imagem_acima_do_limite_e_rejeitada(self):
        with mock.patch("rede_social.models.TAMANHO_MAXIMO_IMAGEM", 10):
            resp = self.postar(conteudo="oi", imagem=gerar_imagem(tamanho=(200, 200)))
        self.assertIn("imagem", resp.context["form"].errors)
        self.assertEqual(Post.objects.count(), 0)

    def test_excluir_post_remove_arquivo(self):
        self.postar(conteudo="com foto", imagem=gerar_imagem())
        post = Post.objects.get()
        nome = post.imagem.name
        self.assertTrue(default_storage.exists(nome))
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("rede_social:excluir_post", args=[post.pk]))
        self.assertFalse(default_storage.exists(nome))

    def test_imagem_aparece_no_feed(self):
        # Só passa depois de atualizar os templates (veja INTEGRACAO.md).
        self.postar(conteudo="com foto", imagem=gerar_imagem())
        post = Post.objects.get()
        resp = self.client.get(reverse("rede_social:feed"))
        self.assertContains(resp, post.imagem.url)

    def test_imagem_amplia_na_mesma_pagina(self):
        # O visualizador (lightbox) vem do layout; o link da foto é marcado para ampliar.
        self.postar(conteudo="com foto", imagem=gerar_imagem())
        resp = self.client.get(reverse("rede_social:feed"))
        self.assertContains(resp, 'id="rs-lightbox"')
        self.assertContains(resp, "data-rs-zoom")
