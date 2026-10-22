from django.contrib import admin

from .models import Comentario, Curtida, Hashtag, Perfil, Post, Seguimento


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nome_exibicao", "empresa", "cargo")
    search_fields = ("usuario__username", "nome_exibicao", "empresa")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "autor", "resumo", "tem_imagem", "pilar", "repost_de", "visivel", "criado_em")
    list_filter = ("pilar", "visivel", "criado_em")
    search_fields = ("conteudo", "autor__username")
    list_select_related = ("autor",)
    actions = ["ocultar", "mostrar"]

    @admin.display(description="conteúdo")
    def resumo(self, obj):
        return obj.conteudo[:60]

    @admin.display(boolean=True, description="imagem")
    def tem_imagem(self, obj):
        return bool(obj.imagem)

    @admin.action(description="Ocultar posts selecionados")
    def ocultar(self, request, queryset):
        queryset.update(visivel=False)

    @admin.action(description="Tornar visíveis os posts selecionados")
    def mostrar(self, request, queryset):
        queryset.update(visivel=True)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "autor", "criado_em")
    search_fields = ("conteudo", "autor__username")


admin.site.register(Hashtag)
admin.site.register(Curtida)
admin.site.register(Seguimento)
