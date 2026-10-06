from django.urls import path
from . import views

urlpatterns = [
    path("atividades/", views.quadro, name="quadro_atividades"),
    path("atividades/<int:pk>/status/", views.mudar_status, name="mudar_status_atividade"),
    path("atividades/<int:pk>/deletar/", views.deletar, name="deletar_atividade"),
]
