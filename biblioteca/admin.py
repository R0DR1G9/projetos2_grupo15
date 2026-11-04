from django.contrib import admin

from .models import Conteudo


@admin.register(Conteudo)
class ConteudoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'tipo', 'publicado')
    list_filter = ('categoria', 'tipo', 'publicado')
    search_fields = ('titulo', 'descricao')
