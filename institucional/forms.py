from django import forms
from .models import MensagemContato


class ContatoForm(forms.ModelForm):
    class Meta:
        model = MensagemContato
        fields = ["nome", "email", "assunto", "mensagem"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Seu nome"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "seu@email.com"}),
            "assunto": forms.Select(attrs={"class": "form-select"}),
            "mensagem": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Conte com detalhes o bug, a sugestão ou a dúvida..."}),
        }
