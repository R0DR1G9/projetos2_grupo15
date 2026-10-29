from django.urls import path
from . import views

urlpatterns = [
    path('diagnostico/', views.home, name='home'),
    path('diagnostico/novo/', views.novo_diagnostico, name='novo_diagnostico'),
    path('diagnostico/metodologia/', views.metodologia, name='metodologia_diagnostico'),
    path('diagnostico/<int:pk>/', views.resultado, name='resultado_diagnostico'),
    path('diagnostico/<int:pk>/pdf/', views.resultado_pdf, name='resultado_pdf'),
    path('diagnostico/<int:pk>/plano/', views.adicionar_ao_plano, name='adicionar_ao_plano'),
    path('deletar/<int:pk>/', views.deletar_diagnostico, name='deletar_diagnostico'),
]
