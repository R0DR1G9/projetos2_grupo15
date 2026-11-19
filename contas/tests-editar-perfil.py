from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Empresa

CNPJ_A = '11222333000181'
CNPJ_B = '11444777000161'


class EditarPerfilTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'aurora', email='aurora@teste.com', password='senha-forte-123', first_name='Aurora')
        Empresa.objects.create(usuario=self.user, cnpj=CNPJ_A)
        self.outro = User.objects.create_user(
            'bruno', email='bruno@teste.com', password='senha-forte-123', first_name='Bruno')
        Empresa.objects.create(usuario=self.outro, cnpj=CNPJ_B)
        self.client.login(username='aurora', password='senha-forte-123')
        self.url = reverse('editar_perfil')

    def dados(self, **extra):
        base = {'first_name': 'Aurora Verde', 'email': 'Novo@Teste.com', 'cnpj': '11.222.333/0001-81'}
        base.update(extra)
        return base

    def test_exige_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_formulario_vem_preenchido(self):
        html = self.client.get(self.url).content.decode()
        self.assertIn('Aurora', html)
        self.assertIn('aurora@teste.com', html)
        self.assertIn('11.222.333/0001-81', html)

    def test_salva_nome_e_email_e_mantem_usuario(self):
        r = self.client.post(self.url, self.dados())
        self.assertRedirects(r, reverse('perfil'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Aurora Verde')
        self.assertEqual(self.user.email, 'novo@teste.com')
        self.assertEqual(self.user.username, 'aurora')

    def test_recusa_email_de_outra_conta(self):
        r = self.client.post(self.url, self.dados(email='BRUNO@teste.com'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Já existe uma conta com este e-mail.')

    def test_recusa_cnpj_de_outra_conta_e_invalido(self):
        r = self.client.post(self.url, self.dados(cnpj='11.444.777/0001-61'))
        self.assertContains(r, 'Já existe uma conta cadastrada com este CNPJ.')
        r = self.client.post(self.url, self.dados(cnpj='12.345.678/0001-90'))
        self.assertContains(r, 'Informe um CNPJ válido.')

    def test_pode_manter_o_proprio_email_e_cnpj(self):
        r = self.client.post(self.url, self.dados(email='aurora@teste.com'))
        self.assertRedirects(r, reverse('perfil'))

    def test_conta_sem_empresa_nao_exige_cnpj(self):
        Empresa.objects.filter(usuario=self.user).delete()
        r = self.client.post(self.url, self.dados(cnpj=''))
        self.assertRedirects(r, reverse('perfil'))
        self.client.post(self.url, self.dados(cnpj='11.222.333/0001-81'))
        self.assertTrue(Empresa.objects.filter(usuario=self.user, cnpj=CNPJ_A).exists())

    def test_perfil_tem_botao_editar(self):
        self.assertContains(self.client.get(reverse('perfil')), self.url)