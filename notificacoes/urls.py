from django.urls import path

from . import views

app_name = "notificacoes"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("<int:pk>/abrir/", views.abrir, name="abrir"),
    path("marcar-todas/", views.marcar_todas, name="marcar_todas"),
]
