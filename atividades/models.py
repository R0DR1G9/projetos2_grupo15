from django.conf import settings
from django.db import models
from django.utils import timezone


class Atividade(models.Model):
    CATEGORIAS = [
        ("ambiental", "Ambiental"),
        ("social", "Social"),
        ("governanca", "Governança"),
    ]
    STATUS = [
        ("aguardando", "Aguardando início"),
        ("andamento", "Em andamento"),
        ("concluido", "Concluído"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="atividades")
    titulo = models.CharField(max_length=150, verbose_name="Título")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="ambiental", verbose_name="Categoria")
    status = models.CharField(max_length=20, choices=STATUS, default="aguardando", verbose_name="Status")
    descricao = models.CharField(max_length=300, blank=True, verbose_name="Detalhes")
    prazo = models.DateField(null=True, blank=True, verbose_name="Prazo")
    responsavel = models.CharField(max_length=80, blank=True, verbose_name="Responsável")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")

    class Meta:
        ordering = ["data_criacao"]
        verbose_name = "Atividade"
        verbose_name_plural = "Atividades"

    @property
    def dias_para_prazo(self):
        if self.prazo is None:
            return None
        return (self.prazo - timezone.localdate()).days

    @property
    def situacao_prazo(self):
        if self.prazo is None or self.status == "concluido":
            return ""
        dias = self.dias_para_prazo
        if dias < 0:
            return "atrasada"
        if dias <= 3:
            return "proxima"
        return "no_prazo"

    @property
    def rotulo_prazo(self):
        if self.prazo is None:
            return ""
        situacao = self.situacao_prazo
        dias = self.dias_para_prazo
        if situacao == "atrasada":
            return "Atrasada há 1 dia" if dias == -1 else f"Atrasada há {-dias} dias"
        if situacao == "proxima":
            if dias == 0:
                return "Vence hoje"
            return "Vence amanhã" if dias == 1 else f"Vence em {dias} dias"
        return f"Prazo: {self.prazo:%d/%m/%Y}"

    def __str__(self):
        return f"{self.titulo} ({self.get_status_display()})"
