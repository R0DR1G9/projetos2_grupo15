import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile

from rede_social.imagens import reduzir_imagem
from rede_social.models import Perfil

from .models import Empresa


def cnpj_valido(numeros):
    if len(numeros) != 14 or numeros == numeros[0] * 14:
        return False
    for tamanho in (12, 13):
        pesos = ([5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2] if tamanho == 12 else [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        soma = sum(int(n) * p for n, p in zip(numeros[:tamanho], pesos))
        digito = 0 if soma % 11 < 2 else 11 - soma % 11
        if int(numeros[tamanho]) != digito:
            return False
    return True


class CadastroForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label='Nome da empresa')
    cnpj = forms.CharField(max_length=18, label='CNPJ', widget=forms.TextInput(attrs={'placeholder': '00.000.000/0000-00', 'inputmode': 'numeric', 'autocomplete': 'off'}))
    email = forms.EmailField(label='E-mail')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'cnpj', 'email', 'username')
        labels = {'username': 'Usuário'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['first_name', 'cnpj', 'email', 'username', 'password1', 'password2'])
        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'form-control'

    def clean_cnpj(self):
        numeros = re.sub(r'\D', '', self.cleaned_data['cnpj'])
        if not cnpj_valido(numeros):
            raise forms.ValidationError('Informe um CNPJ válido.')
        if Empresa.objects.filter(cnpj=numeros).exists():
            raise forms.ValidationError('Já existe uma conta cadastrada com este CNPJ.')
        return numeros

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Empresa.objects.create(usuario=user, cnpj=self.cleaned_data['cnpj'])
        return user
class FotoPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto']
        widgets = {'foto': forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/png,image/jpeg,image/webp,image/gif',
        })}

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if isinstance(foto, UploadedFile):
            return reduzir_imagem(foto, lado_maximo=600)
        return foto