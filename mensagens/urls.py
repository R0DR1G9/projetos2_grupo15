from django.urls import path

from . import views

app_name = "mensagens"

urlpatterns = [
    path("", views.caixa, name="caixa"),
    path("u/<str:username>/", views.conversa, name="conversa"),
    path("u/<str:username>/novas/", views.novas, name="novas"),
    path("mensagem/<int:pk>/excluir/", views.excluir, name="excluir"),
]
