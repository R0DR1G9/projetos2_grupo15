from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Q

TAMANHO_MAXIMO_MENSAGEM = 1000


class Conversa(models.Model):
    """Conversa privada entre duas pessoas.

    O par é guardado em ordem (menor id em `usuario_a`), então A→B e B→A caem
    sempre na mesma conversa. Use `Conversa.entre(...)` para buscar/criar.
    """

    usuario_a = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversas_a"
    )
    usuario_b = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversas_b"
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario_a", "usuario_b"], name="ms_uma_conversa_por_par")
        ]

    def __str__(self):
        return f"{self.usuario_a.get_username()} ↔ {self.usuario_b.get_username()}"

    @classmethod
    def entre(cls, u1, u2, criar=False):
        a, b = sorted([u1, u2], key=lambda u: u.pk)
        if criar:
            return cls.objects.get_or_create(usuario_a=a, usuario_b=b)[0]
        return cls.objects.filter(usuario_a=a, usuario_b=b).first()

    @classmethod
    def do_usuario(cls, usuario):
        return cls.objects.filter(Q(usuario_a=usuario) | Q(usuario_b=usuario))

    def outro_de(self, usuario):
        return self.usuario_b if usuario.pk == self.usuario_a_id else self.usuario_a


class Mensagem(models.Model):
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name="mensagens")
    remetente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mensagens_enviadas"
    )
    texto = models.TextField(validators=[MaxLengthValidator(TAMANHO_MAXIMO_MENSAGEM)])
    criada_em = models.DateTimeField(auto_now_add=True)
    lida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["criada_em", "pk"]
        indexes = [
            models.Index(fields=["conversa", "criada_em"]),
            models.Index(fields=["conversa", "lida_em"]),
        ]

    def __str__(self):
        return f"{self.remetente.get_username()}: {self.texto[:40]}"
