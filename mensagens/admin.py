from django.contrib import admin

from .models import Conversa, Mensagem


@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario_a", "usuario_b", "criada_em")
    search_fields = ("usuario_a__username", "usuario_b__username")
    list_select_related = ("usuario_a", "usuario_b")


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    """Disponível para moderação (denúncias). Mensagens são privadas: acesse com critério."""

    list_display = ("id", "conversa", "remetente", "resumo", "criada_em", "lida_em")
    search_fields = ("texto", "remetente__username")
    list_select_related = ("conversa", "remetente")

    @admin.display(description="texto")
    def resumo(self, obj):
        return obj.texto[:60]
