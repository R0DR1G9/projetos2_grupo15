from django.db import models

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

    data_criacao = models.DateTimeField(auto_now_add=True)

    def calcular_pontuacao(self):
        score_e = ((int(self.residuos_textesis) + int(self.energia_renovavel) + int(self.uso_agua) + int(self.materias_sustentaveis)) / 4) * 100
        score_s = ((int(self.condicoes_trabalho) + int(self.diversidade_inclusao) + int(self.saude_seguranca) + int(self.treinamento_equipe)) / 4) * 100
        score_g = ((int(self.rastreabilidade) + int(self.codigo_etica) + int(self.combate_corrupcao) + int(self.transparencia_fiscal)) / 4) * 100

        score_geral = (score_e + score_s + score_g) / 3

        return {
            'ambiental': round(score_e, 1),
            'social': round(score_s, 1),
            'governanca': round(score_g, 1),
            'geral': round(score_geral, 1)
        }
    def __str__(self):
        return f"Diagnóstico ESG - {self.nome_empresa}"