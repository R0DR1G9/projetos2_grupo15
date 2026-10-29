from django import forms

from .models import DiagnosticoESG


class DiagnosticoForm(forms.ModelForm):
    """Perfil da empresa e dados opcionais. As respostas das perguntas são lidas à parte (perguntas.ler_respostas)."""

    class Meta:
        model = DiagnosticoESG
        fields = [
            'nome_empresa', 'porte', 'tipo_operacao', 'numero_funcionarios',
            'kg_sobras_geradas', 'kg_sobras_reaproveitadas', 'pessoas_lideranca', 'mulheres_lideranca', 'horas_treinamento_ano',
        ]
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Confecções Moda Sustentável'}),
            'porte': forms.Select(attrs={'class': 'form-select'}),
            'tipo_operacao': forms.Select(attrs={'class': 'form-select'}),
            'numero_funcionarios': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Ex: 25'}),
            'kg_sobras_geradas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Ex: 120'}),
            'kg_sobras_reaproveitadas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Ex: 40'}),
            'pessoas_lideranca': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Ex: 5'}),
            'mulheres_lideranca': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Ex: 2'}),
            'horas_treinamento_ano': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Ex: 8'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['porte'].required = True
        self.fields['tipo_operacao'].required = True
        for campo in ('porte', 'tipo_operacao'):
            self.fields[campo].choices = [('', 'Selecione...')] + list(self.fields[campo].choices)[1:]

    def clean(self):
        dados = super().clean()
        pares = (
            ('kg_sobras_reaproveitadas', 'kg_sobras_geradas', 'O reaproveitado não pode ser maior que o total de sobras geradas.'),
            ('mulheres_lideranca', 'pessoas_lideranca', 'O número de mulheres não pode ser maior que o total de pessoas em liderança.'),
        )
        for parte, total, mensagem in pares:
            valor_parte, valor_total = dados.get(parte), dados.get(total)
            if valor_parte is not None and valor_total is not None and valor_parte > valor_total:
                self.add_error(parte, mensagem)
        return dados
