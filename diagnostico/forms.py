from django import forms
from .models import DiagnosticoESG

class DiagnosticoForm(forms.ModelForm):
    class Meta:
        model = DiagnosticoESG
        fields = [
           'nome_empresa',
            'residuos_textesis',
            'energia_renovavel',
            'uso_agua',
            'materias_sustentaveis',
            'condicoes_trabalho',
            'diversidade_inclusao',
            'saude_seguranca',
            'treinamento_equipe',
            'rastreabilidade',
            'codigo_etica',
            'combate_corrupcao',
            'transparencia_fiscal',
        ]
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Confecções Moda Sustentável'}),
        }