from django.urls import path
from . import views

urlpatterns = [
    path('evolucao/', views.evolucao, name='evolucao'),
    path('evolucao/pdf/', views.evolucao_pdf, name='evolucao_pdf'),
]