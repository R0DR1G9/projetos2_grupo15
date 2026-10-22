from django.urls import path

from . import views

app_name = "rede_social"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("post/<int:pk>/", views.detalhe_post, name="detalhe_post"),
    path("post/<int:pk>/curtir/", views.curtir, name="curtir"),
    path("post/<int:pk>/repostar/", views.repostar, name="repostar"),
    path("post/<int:pk>/excluir/", views.excluir_post, name="excluir_post"),
    path("hashtag/<str:tag>/", views.hashtag, name="hashtag"),
    path("buscar/", views.buscar, name="buscar"),
    path("meu-perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("perfil/<str:username>/", views.perfil, name="perfil"),
    path("perfil/<str:username>/seguir/", views.seguir, name="seguir"),
]
