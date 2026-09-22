from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/salvar-diagnostico/', views.salvar_diagnostico, name='salvar_diagnostico'),
    path('deletar/<int:pk>/', views.deletar_diagnostico, name='deletar_diagnostico'),
]