from django.conf import settings
from django.db import models

from . import perguntas

VERSAO_ATUAL = 3
MEDALHAS = {
    'ouro':   {'chave': 'ouro',   'nome': 'Ouro',   'emoji': '🥇', 'cor': '#d4af37'},
    'prata':  {'chave': 'prata',  'nome': 'Prata',  'emoji': '🥈', 'cor': '#9aa0a6'},
    'bronze': {'chave': 'bronze', 'nome': 'Bronze', 'emoji': '🥉', 'cor': '#cd7f32'},
}

def classificar(pct):
    if pct >= 70:
        return MEDALHAS['ouro']
    if pct >= 40:
        return MEDALHAS['prata']
    return MEDALHAS['bronze']
# Create your models here.
class DiagnosticoESG(models.Model):
    nome_empresa = models.CharField(max_length=150, verbose_name="Nome da Empresa / Confecção")

    residuos_textesis = models.BooleanField(default=False, verbose_name="Realiza a gestão ou reciclagem de resíduos têxteis e sobras de corte?")
    energia_renovavel = models.BooleanField(default=False, verbose_name="Utiliza fontes de energia renovável ou eficiência energética na produção?")
    uso_agua = models.BooleanField(default=False, verbose_name="Possui processos para medição e redução do consumo de água?")
    materias_sustentaveis = models.BooleanField(default=False, verbose_name="Utiliza matérias-primas orgânicas, recicladas ou certificadas?")

    condicoes_trabalho = models.BooleanField(default=False, verbose_name="Garante condições de trabalho seguras, salários justos e apoio à comunidade local?")
    diversidade_inclusao = models.BooleanField(default=False, verbose_name="Possui políticas ativas de diversidade, inclusão e equidade de gênero?")
    saude_seguranca = models.BooleanField(default=False, verbose_name="Oferece programas formais de saúde, segurança no trabalho e ergonomia?")
    treinamento_equipe = models.BooleanField(default=False, verbose_name="Promove treinamentos e capacitação contínua para os colaboradores?")

    rastreabilidade = models.BooleanField(default=False, verbose_name="Possui rastreabilidade e controle sobre a origem dos fornecedores de matéria-prima?")
    codigo_etica = models.BooleanField(default=False, verbose_name="Possui um Código de Ética e Conduta formalizado e acessível a todos?")
    combate_corrupcao = models.BooleanField(default=False, verbose_name="Possui políticas formais de anticorrupção ou canal de denúncias?")
    transparencia_fiscal = models.BooleanField(default=False, verbose_name="Mantém transparência total em obrigações fiscais, jurídicas e relatórios?")

    # Diagnóstico v2: perfil da empresa, respostas por escala de maturidade (0 a 4) e dados opcionais
    porte = models.CharField(max_length=10, choices=perguntas.PORTES, blank=True, verbose_name="Porte")
    numero_funcionarios = models.PositiveIntegerField(null=True, blank=True, verbose_name="Número de funcionários")
    tipo_operacao = models.CharField(max_length=10, choices=perguntas.TIPOS_OPERACAO, blank=True, verbose_name="Tipo de operação")
    respostas = models.JSONField(default=dict, blank=True)
    pct_residuos_reaproveitados = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="% de sobras de tecido reaproveitadas")
    pct_mulheres_lideranca = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="% de mulheres na liderança")
    horas_treinamento_ano = models.PositiveIntegerField(null=True, blank=True, verbose_name="Horas de treinamento por pessoa ao ano")

    data_criacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.CASCADE, related_name='diagnosticos'
    )

    # 1 = formato simples (sim ou não); 3 = questionário de maturidade atual
    versao_questionario = models.PositiveSmallIntegerField(default=1)

    @property
    def formato_antigo(self):
        return self.versao_questionario != VERSAO_ATUAL

    def calcular_pontuacao(self):
        if not self.formato_antigo:
            notas = perguntas.pontuar(self.respostas)
            score_e = notas['ambiental']['pct']
            score_s = notas['social']['pct']
            score_g = notas['governanca']['pct']
        else:
            score_e, score_s, score_g = self._pontuacao_antiga()
        score_geral = (score_e + score_s + score_g) / 3
        return {
            'ambiental': round(score_e, 1),
            'social': round(score_s, 1),
            'governanca': round(score_g, 1),
            'geral': round(score_geral, 1),
            'medalha_geral': classificar(score_geral),
            'medalha_ambiental': classificar(score_e),
            'medalha_social': classificar(score_s),
            'medalha_governanca': classificar(score_g),
        }

    def _pontuacao_antiga(self):
        score_e = ((int(self.residuos_textesis) + int(self.energia_renovavel) + int(self.uso_agua) + int(self.materias_sustentaveis)) / 4) * 100
        score_s = ((int(self.condicoes_trabalho) + int(self.diversidade_inclusao) + int(self.saude_seguranca) + int(self.treinamento_equipe)) / 4) * 100
        score_g = ((int(self.rastreabilidade) + int(self.codigo_etica) + int(self.combate_corrupcao) + int(self.transparencia_fiscal)) / 4) * 100

        return score_e, score_s, score_g

    def __str__(self):
        return f"Diagnóstico ESG - {self.nome_empresa}"