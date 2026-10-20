from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CadastroForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label='Nome da empresa')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'username')
        labels = {'username': 'Usuário'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'form-control'