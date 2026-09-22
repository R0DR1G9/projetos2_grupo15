from django.contrib import admin
from .models import MensagemContato


@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "assunto", "data_criacao", "lida")
    list_filter = ("assunto", "lida", "data_criacao")
    search_fields = ("nome", "email", "mensagem")
    readonly_fields = ("nome", "email", "assunto", "mensagem", "data_criacao")
    list_editable = ("lida",)
    ordering = ("-data_criacao",)
