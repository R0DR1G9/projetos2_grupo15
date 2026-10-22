from django import forms
from django.core.exceptions import ValidationError

from .models import TAMANHO_MAXIMO_MENSAGEM


class MensagemForm(forms.Form):
    texto = forms.CharField(
        max_length=TAMANHO_MAXIMO_MENSAGEM,
        error_messages={"required": "Escreva uma mensagem."},
        widget=forms.Textarea(
            attrs={
                "rows": 1,
                "maxlength": TAMANHO_MAXIMO_MENSAGEM,
                "placeholder": "Mensagem…",
                "aria-label": "Escreva sua mensagem",
                "autocomplete": "off",
            }
        ),
    )

    def clean_texto(self):
        texto = self.cleaned_data["texto"].strip()
        if not texto:
            raise ValidationError("Escreva uma mensagem.")
        return texto
