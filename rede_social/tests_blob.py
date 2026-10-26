import io
import os
from types import SimpleNamespace
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from PIL import Image
from vercel.blob import sync as blob_real
from vercel.blob.errors import BlobError

from .forms import PostForm
from .imagens import LADO_MAXIMO, reduzir_imagem
from .storage import VercelBlobStorage

TOKEN = "vercel_blob_rw_AbC123xyz_segredo456"


def imagem_em_bytes(tamanho, formato="JPEG", modo="RGB"):
    saida = io.BytesIO()
    Image.new(modo, tamanho, (200, 30, 30)).save(saida, format=formato)
    return saida.getvalue()


def arquivo_enviado(nome, conteudo, tipo):
    return SimpleUploadedFile(nome, conteudo, content_type=tipo)


class VercelBlobStorageTests(SimpleTestCase):
    def setUp(self):
        self.armazenamento = VercelBlobStorage()

    def test_salvar_envia_bytes_como_publico_e_devolve_o_caminho(self):
        with mock.patch.object(
            blob_real,
            "put_blob",
            autospec=True,
            return_value=SimpleNamespace(pathname="rede_social/posts/2026/10/a.png"),
        ) as put:
            with mock.patch("rede_social.storage.blob", blob_real):
                nome = self.armazenamento.save(
                    "rede_social/posts/2026/10/a.png", ContentFile(b"dados", name="a.png")
                )
        self.assertEqual(nome, "rede_social/posts/2026/10/a.png")
        args, kwargs = put.call_args
        self.assertEqual(args, ("rede_social/posts/2026/10/a.png", b"dados"))
        self.assertEqual(kwargs["access"], "public")
        self.assertEqual(kwargs["content_type"], "image/png")
        self.assertGreater(kwargs["cache_control_max_age"], 0)

    def test_url_usa_a_loja_do_token(self):
        with mock.patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": TOKEN}):
            url = self.armazenamento.url("rede_social/posts/2026/10/a b.png")
        self.assertEqual(
            url,
            "https://abc123xyz.public.blob.vercel-storage.com/rede_social/posts/2026/10/a%20b.png",
        )

    def test_url_sem_token_levanta_erro_de_configuracao(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ImproperlyConfigured):
                self.armazenamento.url("a.png")

    def test_apagar_chama_o_blob(self):
        with mock.patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": TOKEN}):
            with mock.patch("rede_social.storage.blob") as blob:
                self.armazenamento.delete("rede_social/posts/a.png")
        blob.delete_blob.assert_called_once_with(
            "https://abc123xyz.public.blob.vercel-storage.com/rede_social/posts/a.png"
        )

    def test_apagar_nome_vazio_nao_chama_o_blob(self):
        with mock.patch("rede_social.storage.blob") as blob:
            self.armazenamento.delete("")
        blob.delete_blob.assert_not_called()

    def test_apagar_com_falha_do_blob_nao_derruba_a_requisicao(self):
        with mock.patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": TOKEN}):
            with mock.patch("rede_social.storage.blob") as blob:
                blob.delete_blob.side_effect = BlobError("falhou")
                with self.assertLogs("rede_social.storage", level="WARNING"):
                    self.armazenamento.delete("rede_social/posts/a.png")

    def test_nome_nunca_existe_previamente(self):
        self.assertFalse(self.armazenamento.exists("qualquer.png"))


class ReduzirImagemTests(SimpleTestCase):
    def test_imagem_grande_e_reduzida_para_o_lado_maximo(self):
        original = arquivo_enviado("g.jpg", imagem_em_bytes((3200, 2000)), "image/jpeg")
        reduzida = reduzir_imagem(original)
        imagem = Image.open(reduzida)
        self.assertEqual(imagem.format, "JPEG")
        self.assertEqual(max(imagem.size), LADO_MAXIMO)
        self.assertEqual(imagem.size, (1600, 1000))
        self.assertEqual(reduzida.name, "g.jpg")

    def test_png_grande_continua_png(self):
        original = arquivo_enviado("g.png", imagem_em_bytes((2400, 1800), "PNG"), "image/png")
        imagem = Image.open(reduzir_imagem(original))
        self.assertEqual(imagem.format, "PNG")
        self.assertEqual(max(imagem.size), LADO_MAXIMO)

    def test_webp_grande_e_reduzido(self):
        original = arquivo_enviado("g.webp", imagem_em_bytes((2000, 2000), "WEBP"), "image/webp")
        imagem = Image.open(reduzir_imagem(original))
        self.assertEqual(imagem.format, "WEBP")
        self.assertEqual(imagem.size, (1600, 1600))

    def test_imagem_pequena_nao_e_alterada(self):
        conteudo = imagem_em_bytes((800, 600))
        original = arquivo_enviado("p.jpg", conteudo, "image/jpeg")
        resultado = reduzir_imagem(original)
        self.assertIs(resultado, original)
        self.assertEqual(resultado.read(), conteudo)

    def test_gif_nao_e_alterado_mesmo_grande(self):
        conteudo = imagem_em_bytes((2500, 2500), "GIF", "P")
        original = arquivo_enviado("a.gif", conteudo, "image/gif")
        resultado = reduzir_imagem(original)
        self.assertIs(resultado, original)
        self.assertEqual(resultado.read(), conteudo)

    def test_jpeg_cmyk_e_convertido_para_rgb(self):
        original = arquivo_enviado(
            "c.jpg", imagem_em_bytes((2000, 1000), "JPEG", "CMYK"), "image/jpeg"
        )
        self.assertEqual(Image.open(reduzir_imagem(original)).mode, "RGB")

    def test_orientacao_exif_e_respeitada(self):
        imagem = Image.new("RGB", (2000, 1000), (10, 10, 200))
        exif = Image.Exif()
        exif[0x0112] = 6
        saida = io.BytesIO()
        imagem.save(saida, format="JPEG", exif=exif)
        original = arquivo_enviado("o.jpg", saida.getvalue(), "image/jpeg")
        self.assertEqual(Image.open(reduzir_imagem(original)).size, (800, 1600))


class PostFormImagemTests(TestCase):
    def test_formulario_entrega_a_imagem_ja_reduzida(self):
        enviado = arquivo_enviado("g.jpg", imagem_em_bytes((3000, 3000)), "image/jpeg")
        form = PostForm({"conteudo": "oi", "pilar": "geral"}, {"imagem": enviado})
        self.assertTrue(form.is_valid(), form.errors)
        imagem = Image.open(form.cleaned_data["imagem"])
        self.assertEqual(imagem.size, (1600, 1600))

    def test_formulario_sem_imagem_continua_valido(self):
        form = PostForm({"conteudo": "só texto", "pilar": "geral"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertFalse(form.cleaned_data["imagem"])
