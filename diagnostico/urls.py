from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/salvar-diagnostico/', views.salvar_diagnostico, name='salvar_diagnostico'),
]