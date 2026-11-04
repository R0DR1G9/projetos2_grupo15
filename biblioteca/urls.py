from django.urls import path

from . import views

urlpatterns = [
    path('biblioteca/', views.lista, name='biblioteca'),
    path('biblioteca/<int:pk>/', views.detalhe, name='biblioteca_detalhe'),
]
