from django.urls import path
from . import views

urlpatterns = [
    path('evolucao/', views.evolucao, name='evolucao'),
]