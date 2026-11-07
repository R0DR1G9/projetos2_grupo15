from django.contrib import admin
from .models import Atividade


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "responsavel", "prazo", "categoria", "status")
    list_filter = ("categoria", "status")
    search_fields = ("titulo",)
