from django.urls import path
from . import views

urlpatterns = [
    path("sobre/", views.sobre, name="sobre"),
    path("quem-somos/", views.quem_somos, name="quem_somos"),
    path("contato/", views.contato, name="contato"),
]
