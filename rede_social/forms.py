from django import forms

from .models import Comentario, Perfil, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["conteudo", "pilar", "imagem"]
        widgets = {
            "imagem": forms.FileInput(
                attrs={"accept": "image/jpeg,image/png,image/gif,image/webp"}
            ),
            "conteudo": forms.Textarea(
                attrs={
                    "rows": 3,
                    "maxlength": 500,
                    "placeholder": "Compartilhe uma ação ou conquista ESG da sua empresa… use #hashtags",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O texto passa a ser opcional quando há imagem (regra em clean()).
        self.fields["conteudo"].required = False

    def clean_conteudo(self):
        return self.cleaned_data["conteudo"].strip()

    def clean(self):
        cleaned = super().clean()
        if (
            not cleaned.get("conteudo")
            and not cleaned.get("imagem")
            and not self.has_error("imagem")
        ):
            self.add_error("conteudo", "Escreva algo ou anexe uma imagem para publicar.")
        return cleaned


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["conteudo"]
        widgets = {
            "conteudo": forms.Textarea(
                attrs={"rows": 2, "maxlength": 280, "placeholder": "Escreva sua resposta…"}
            )
        }

    def clean_conteudo(self):
        conteudo = self.cleaned_data["conteudo"].strip()
        if not conteudo:
            raise forms.ValidationError("Escreva algo para comentar.")
        return conteudo


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["nome_exibicao", "empresa", "cargo", "bio", "site"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 3, "maxlength": 280})}
