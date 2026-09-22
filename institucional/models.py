from django.db import models


class MensagemContato(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail")
    assunto = models.CharField(
        max_length=20,
        choices=[
            ("bug", "Reportar um bug"),
            ("sugestao", "Sugestão"),
            ("duvida", "Dúvida"),
            ("outro", "Outro"),
        ],
        default="outro",
        verbose_name="Assunto",
    )
    mensagem = models.TextField(verbose_name="Mensagem")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Recebida em")
    lida = models.BooleanField(default=False, verbose_name="Lida")

    class Meta:
        ordering = ["-data_criacao"]
        verbose_name = "Mensagem de contato"
        verbose_name_plural = "Mensagens de contato"

    def __str__(self):
        return f"{self.get_assunto_display()} — {self.nome} ({self.data_criacao:%d/%m/%Y})"
