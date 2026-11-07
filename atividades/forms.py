from django import forms
from django.utils import timezone

from .models import Atividade


class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ["titulo", "categoria", "prazo", "responsavel"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex.: Reaproveitar retalhos de tecido"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "prazo": forms.DateInput(attrs={"class": "form-control", "type": "date", "aria-label": "Prazo"}),
            "responsavel": forms.TextInput(attrs={"class": "form-control", "placeholder": "Responsável (opcional)", "aria-label": "Responsável"}),
        }
        error_messages = {
            "titulo": {"required": "O título da atividade é obrigatório."},
        }

    def clean_prazo(self):
        prazo = self.cleaned_data.get("prazo")
        if prazo and prazo < timezone.localdate():
            raise forms.ValidationError("O prazo não pode ser uma data que já passou.")
        return prazo


class DetalhesAtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ["prazo", "responsavel"]
