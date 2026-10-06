from django import forms
from .models import Atividade


class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ["titulo", "categoria"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex.: Reaproveitar retalhos de tecido"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
        }
        error_messages = {
            "titulo": {"required": "O título da atividade é obrigatório."},
        }
