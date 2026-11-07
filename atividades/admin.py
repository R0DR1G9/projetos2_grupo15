from django.contrib import admin
from .models import Atividade


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "categoria", "status", "data_criacao")
    list_filter = ("categoria", "status")
    search_fields = ("titulo",)
