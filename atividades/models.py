from django.db import models


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

    titulo = models.CharField(max_length=150, verbose_name="Título")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="ambiental", verbose_name="Categoria")
    status = models.CharField(max_length=20, choices=STATUS, default="aguardando", verbose_name="Status")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")

    class Meta:
        ordering = ["data_criacao"]
        verbose_name = "Atividade"
        verbose_name_plural = "Atividades"

    def __str__(self):
        return f"{self.titulo} ({self.get_status_display()})"
