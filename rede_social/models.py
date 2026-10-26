import os
import re
import uuid

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

# "#" não pode vir colado em letra/número nem em "&" (evita casar "&#39;" já escapado)
HASHTAG_RE = re.compile(r"(?<![\w&])#(\w+)", re.UNICODE)

# Upload de imagens nos posts
TAMANHO_MAXIMO_IMAGEM = 4 * 1024 * 1024
EXTENSOES_IMAGEM = ["jpg", "jpeg", "png", "gif", "webp"]


def caminho_imagem_post(instance, filename):
    """Nome aleatório: evita colisões e não expõe o nome original do arquivo."""
    extensao = os.path.splitext(filename)[1].lower()
    return f"rede_social/posts/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{extensao}"


def validar_tamanho_imagem(arquivo):
    if arquivo.size > TAMANHO_MAXIMO_IMAGEM:
        limite = TAMANHO_MAXIMO_IMAGEM / (1024 * 1024)
        raise ValidationError(f"A imagem é muito grande (máximo de {limite:g} MB).")


class Pilar(models.TextChoices):
    GERAL = "geral", "Geral"
    AMBIENTAL = "ambiental", "Ambiental (E)"
    SOCIAL = "social", "Social (S)"
    GOVERNANCA = "governanca", "Governança (G)"


class Perfil(models.Model):
    """Perfil público do usuário na rede social (estilo LinkedIn)."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil_social"
    )
    nome_exibicao = models.CharField("nome de exibição", max_length=80, blank=True)
    empresa = models.CharField(max_length=120, blank=True)
    cargo = models.CharField(max_length=80, blank=True)
    bio = models.CharField(max_length=280, blank=True)
    site = models.URLField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfis"

    def __str__(self):
        return f"Perfil de {self.usuario.get_username()}"

    @property
    def nome(self):
        return (
            self.nome_exibicao
            or self.usuario.get_full_name()
            or self.usuario.get_username()
        )

    def get_absolute_url(self):
        return reverse("rede_social:perfil", args=[self.usuario.get_username()])


def nome_do_usuario(usuario):
    """Nome para exibição; funciona mesmo se o usuário ainda não tiver Perfil."""
    try:
        perfil = usuario.perfil_social
    except ObjectDoesNotExist:
        perfil = None
    if perfil is not None and perfil.nome_exibicao:
        return perfil.nome_exibicao
    return usuario.get_full_name() or usuario.get_username()


class Hashtag(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"#{self.nome}"


class Post(models.Model):
    """Publicação (estilo tweet/post). Um repost é um Post sem texto apontando para o original."""

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts_sociais"
    )
    conteudo = models.TextField(blank=True, validators=[MaxLengthValidator(500)])
    pilar = models.CharField(
        "pilar ESG", max_length=12, choices=Pilar.choices, default=Pilar.GERAL, db_index=True
    )
    imagem = models.ImageField(
        "imagem",
        upload_to=caminho_imagem_post,
        blank=True,
        validators=[FileExtensionValidator(EXTENSOES_IMAGEM), validar_tamanho_imagem],
    )
    repost_de = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="reposts"
    )
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name="posts")
    visivel = models.BooleanField(
        default=True, help_text="Desmarque para ocultar (moderação)."
    )
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-criado_em", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["autor", "repost_de"],
                condition=models.Q(repost_de__isnull=False),
                name="rs_um_repost_por_autor",
            )
        ]

    def __str__(self):
        if self.repost_de_id:
            return f"{self.autor.get_username()} repostou #{self.repost_de_id}"
        return f"{self.autor.get_username()}: {self.conteudo[:40] or '[imagem]'}"

    def get_absolute_url(self):
        return reverse("rede_social:detalhe_post", args=[self.repost_de_id or self.pk])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.repost_de_id:
            self.sincronizar_hashtags()

    def sincronizar_hashtags(self):
        nomes = {n.lower()[:50] for n in HASHTAG_RE.findall(self.conteudo)}
        self.hashtags.set([Hashtag.objects.get_or_create(nome=n)[0] for n in nomes])


class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comentarios")
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comentarios_sociais"
    )
    conteudo = models.CharField(max_length=280)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em", "pk"]

    def __str__(self):
        return f"{self.autor.get_username()} em #{self.post_id}"


class Curtida(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="curtidas")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="curtidas_sociais"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "usuario"], name="rs_uma_curtida_por_usuario")
        ]

    def __str__(self):
        return f"{self.usuario.get_username()} curtiu #{self.post_id}"


class Seguimento(models.Model):
    seguidor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seguindo_social"
    )
    seguido = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seguidores_social"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "seguimento"
        constraints = [
            models.UniqueConstraint(fields=["seguidor", "seguido"], name="rs_seguimento_unico")
        ]

    def __str__(self):
        return f"{self.seguidor.get_username()} → {self.seguido.get_username()}"
