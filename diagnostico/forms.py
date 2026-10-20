from django import forms

from .models import DiagnosticoESG


class DiagnosticoForm(forms.ModelForm):
    """Perfil da empresa e dados opcionais. As respostas das perguntas são lidas à parte (perguntas.ler_respostas)."""

    class Meta:
        model = DiagnosticoESG
        fields = [
            'nome_empresa', 'porte', 'tipo_operacao', 'numero_funcionarios',
            'pct_residuos_reaproveitados', 'pct_mulheres_lideranca', 'horas_treinamento_ano',
        ]
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Confecções Moda Sustentável'}),
            'porte': forms.Select(attrs={'class': 'form-select'}),
            'tipo_operacao': forms.Select(attrs={'class': 'form-select'}),
            'numero_funcionarios': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Ex: 25'}),
            'pct_residuos_reaproveitados': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'placeholder': 'Ex: 30'}),
            'pct_mulheres_lideranca': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'placeholder': 'Ex: 40'}),
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
        for campo in ('pct_residuos_reaproveitados', 'pct_mulheres_lideranca'):
            valor = dados.get(campo)
            if valor is not None and valor > 100:
                self.add_error(campo, 'Informe um valor entre 0 e 100.')
        return dados
