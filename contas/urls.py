from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='contas/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),

    path('senha/esqueci/', auth_views.PasswordResetView.as_view(
        template_name='contas/senha_esqueci.html',
        email_template_name='contas/email_redefinir_senha.txt',
        subject_template_name='contas/email_redefinir_senha_assunto.txt',
        success_url=reverse_lazy('senha_esqueci_enviado')), name='senha_esqueci'),
    path('senha/esqueci/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='contas/senha_enviado.html'), name='senha_esqueci_enviado'),
    path('senha/redefinir/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='contas/senha_nova.html',
        success_url=reverse_lazy('senha_redefinida')), name='password_reset_confirm'),
    path('senha/redefinida/', auth_views.PasswordResetCompleteView.as_view(
        template_name='contas/senha_redefinida.html'), name='senha_redefinida'),
]