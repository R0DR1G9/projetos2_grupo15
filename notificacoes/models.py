from django.conf import settings
from django.db import models
from django.db.models import Q


class Notificacao(models.Model):
    TIPOS = [
        ("comentario", "Comentário"),
        ("mensagem", "Mensagem"),
        ("prazo", "Prazo"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notificacoes")
    tipo = models.CharField(max_length=20, choices=TIPOS)
    texto = models.CharField(max_length=200)
    link = models.CharField(max_length=200, blank=True)
    chave = models.CharField(max_length=120, blank=True)
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em", "-pk"]
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        constraints = [
            models.UniqueConstraint(fields=["usuario", "chave"], condition=~Q(chave=""), name="notificacao_chave_unica"),
        ]

    def __str__(self):
        return f"{self.usuario.get_username()}: {self.texto}"
