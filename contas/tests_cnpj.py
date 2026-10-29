from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import cnpj_valido
from .models import Empresa

CNPJ_OK = '11.222.333/0001-81'


def dados(**extra):
    base = {'first_name': 'Aurora', 'cnpj': CNPJ_OK, 'username': 'aurora', 'password1': 'senha-forte-123', 'password2': 'senha-forte-123'}
    base.update(extra)
    return base


class CnpjTests(TestCase):
    def test_validador(self):
        self.assertTrue(cnpj_valido('11222333000181'))
        self.assertFalse(cnpj_valido('11222333000182'))
        self.assertFalse(cnpj_valido('11111111111111'))
        self.assertFalse(cnpj_valido('123'))

    def test_cadastro_salva_cnpj_so_com_numeros(self):
        self.client.post(reverse('cadastro'), dados())
        empresa = Empresa.objects.get()
        self.assertEqual(empresa.cnpj, '11222333000181')
        self.assertEqual(empresa.cnpj_formatado, CNPJ_OK)
        self.assertEqual(empresa.usuario.first_name, 'Aurora')

    def test_cnpj_invalido_nao_cria_conta(self):
        r = self.client.post(reverse('cadastro'), dados(cnpj='11.222.333/0001-82'))
        self.assertContains(r, 'Informe um CNPJ válido.')
        self.assertFalse(get_user_model().objects.exists())

    def test_cnpj_repetido_rejeitado(self):
        self.client.post(reverse('cadastro'), dados())
        self.client.logout()
        r = self.client.post(reverse('cadastro'), dados(username='outra'))
        self.assertContains(r, 'Já existe uma conta cadastrada com este CNPJ.')
        self.assertEqual(Empresa.objects.count(), 1)

    def test_tela_de_cadastro_tem_campo_e_mascara(self):
        r = self.client.get(reverse('cadastro'))
        self.assertContains(r, 'name="cnpj"')
        self.assertContains(r, 'js/cnpj.js')
