from django.contrib import admin

from .models import Notificacao


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo", "texto", "lida", "criada_em")
    list_filter = ("tipo", "lida")
