from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from atividades.models import Atividade

from . import perguntas
from .models import VERSAO_ATUAL, DiagnosticoESG


def post_completo(nivel=4, tipo='confeccao', **extra):
    dados = {'nome_empresa': 'Confecção Teste', 'porte': 'pequena', 'tipo_operacao': tipo, 'numero_funcionarios': '20'}
    dados.update({f'q_{pid}': str(nivel) for pid in perguntas.aplicaveis(tipo)})
    dados.update(extra)
    return dados


def novo_usuario(nome='gestora', empresa='Aurora'):
    return get_user_model().objects.create_user(nome, password='senha-forte-123', first_name=empresa)


class ComLogin(TestCase):
    def setUp(self):
        self.user = novo_usuario()
        self.client.force_login(self.user)


def criar(nome='X', respostas=None, versao=VERSAO_ATUAL, usuario=None, **campos):
    return DiagnosticoESG.objects.create(
        usuario=usuario, nome_empresa=nome, respostas=respostas if respostas is not None else {pid: 4 for pid in perguntas.PERGUNTAS},
        versao_questionario=versao, **campos)


class BancoDePerguntasTests(TestCase):
    def test_estrutura(self):
        self.assertEqual(len(perguntas.PERGUNTAS), 23)
        for p in perguntas.PERGUNTAS.values():
            self.assertEqual(len(p['niveis']), 5, p['id'])
            self.assertEqual(set(p['acoes']), {0, 1, 2}, p['id'])
            self.assertIn(p['peso'], (1, 2, 3), p['id'])
            self.assertTrue(p['fontes'] and all(f in perguntas.FONTES for f in p['fontes']), p['id'])
            for acao, pronto in p['acoes'].values():
                self.assertLessEqual(len(acao), 150, p['id'])
                self.assertTrue(pronto)

    def test_todo_tipo_tem_perguntas_nos_tres_pilares(self):
        for tipo in perguntas.TODOS:
            pilares = {p['pilar'] for p in perguntas.aplicaveis(tipo).values()}
            self.assertEqual(pilares, {'ambiental', 'social', 'governanca'}, tipo)

    def test_aplicabilidade(self):
        self.assertNotIn('amb_efluentes', perguntas.aplicaveis('varejo'))
        self.assertIn('amb_efluentes', perguntas.aplicaveis('faccao'))
        self.assertNotIn('gov_terceirizados', perguntas.aplicaveis('faccao'))

    def test_notas_extremas(self):
        tudo4 = perguntas.pontuar({pid: 4 for pid in perguntas.PERGUNTAS})
        tudo0 = perguntas.pontuar({pid: 0 for pid in perguntas.PERGUNTAS})
        for chave in ('ambiental', 'social', 'governanca'):
            self.assertEqual(tudo4[chave]['pct'], 100.0)
            self.assertEqual(tudo0[chave]['pct'], 0.0)

    def test_nivel_gerenciado_vale_75(self):
        self.assertEqual(perguntas.pontuar({pid: 3 for pid in perguntas.PERGUNTAS})['social']['pct'], 75.0)

    def test_peso_influencia_a_nota(self):
        base = {pid: 0 for pid in perguntas.PERGUNTAS}
        alto = perguntas.pontuar({**base, 'amb_efluentes': 4})['ambiental']['pct']    # peso 3
        baixo = perguntas.pontuar({**base, 'amb_materiais': 4})['ambiental']['pct']   # peso 2
        self.assertGreater(alto, baixo)

    def test_nao_se_aplica_fica_fora_da_conta(self):
        todas4 = {pid: 4 for pid in perguntas.PERGUNTAS}
        com_na = {**todas4, 'amb_efluentes': None}
        self.assertEqual(perguntas.pontuar(com_na)['ambiental']['pct'], 100.0)

    def test_pilar_sem_respostas_nao_quebra(self):
        self.assertEqual(perguntas.pontuar({})['social']['pct'], 0.0)

    def test_recomendacao_e_o_proximo_passo_do_nivel_atual(self):
        respostas = {pid: 4 for pid in perguntas.PERGUNTAS}
        respostas['soc_riscos'] = 1
        rec = perguntas.recomendacoes(respostas)
        self.assertEqual([r['id'] for r in rec], ['soc_riscos'])
        self.assertEqual(rec[0]['acao'], perguntas.PERGUNTAS['soc_riscos']['acoes'][1][0])
        self.assertEqual(rec[0]['prazo'], 60)
        self.assertEqual(rec[0]['prioridade'], 'Alta')   # (3-1) * 3 = 6
        self.assertEqual((rec[0]['nivel_nome'], rec[0]['proximo_nome']), ('Básico', 'Definido'))

    def test_recomendacoes_ordenadas_por_impacto(self):
        respostas = {pid: 4 for pid in perguntas.PERGUNTAS}
        respostas.update({'soc_trabalho_digno': 0, 'soc_comunidade': 2})
        ids = [r['id'] for r in perguntas.recomendacoes(respostas)]
        self.assertEqual(ids, ['soc_trabalho_digno', 'soc_comunidade'])

    def test_ignora_nao_se_aplica_e_nivel_adequado(self):
        respostas = {pid: 3 for pid in perguntas.PERGUNTAS}
        respostas['amb_quimicos'] = None
        self.assertEqual(perguntas.recomendacoes(respostas), [])


class LeituraDasRespostasTests(TestCase):
    def test_le_so_perguntas_aplicaveis_ao_tipo(self):
        post = {f'q_{pid}': '2' for pid in perguntas.PERGUNTAS}
        respostas, faltando = perguntas.ler_respostas(post, 'varejo')
        self.assertEqual(faltando, [])
        self.assertNotIn('amb_efluentes', respostas)

    def test_na_so_vale_onde_permitido(self):
        post = {f'q_{pid}': '2' for pid in perguntas.PERGUNTAS}
        post['q_amb_quimicos'] = 'na'
        post['q_soc_riscos'] = 'na'
        respostas, faltando = perguntas.ler_respostas(post, 'confeccao')
        self.assertIsNone(respostas['amb_quimicos'])
        self.assertEqual(faltando, ['soc_riscos'])

    def test_valor_fora_da_escala(self):
        post = {f'q_{pid}': '2' for pid in perguntas.PERGUNTAS}
        post['q_amb_energia'] = '9'
        self.assertEqual(perguntas.ler_respostas(post, 'confeccao')[1], ['amb_energia'])


class DiagnosticoModelTests(TestCase):
    def test_novo_usa_respostas(self):
        d = criar()
        self.assertEqual(d.calcular_pontuacao()['geral'], 100.0)
        self.assertFalse(d.formato_antigo)

    def test_antigo_continua_funcionando(self):
        d = DiagnosticoESG.objects.create(nome_empresa='B', residuos_textesis=True, energia_renovavel=True,
                                          uso_agua=True, materias_sustentaveis=True)
        p = d.calcular_pontuacao()
        self.assertEqual((p['ambiental'], p['social'], p['geral']), (100.0, 0.0, 33.3))
        self.assertTrue(d.formato_antigo)

    def test_medalha_tem_chave_para_css(self):
        self.assertEqual(criar().calcular_pontuacao()['medalha_geral']['chave'], 'ouro')


class FluxoDoDiagnosticoTests(ComLogin):
    def test_paginas_abrem(self):
        for nome in ('home', 'novo_diagnostico', 'metodologia_diagnostico'):
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200, nome)

    def test_metodologia_lista_fontes_e_limitacoes(self):
        r = self.client.get(reverse('metodologia_diagnostico'))
        self.assertContains(r, 'Limitações')
        self.assertContains(r, perguntas.FONTES['gri']['url'])
        self.assertContains(r, perguntas.PERGUNTAS['soc_riscos']['texto'])

    def test_formulario_mostra_ancoras_dos_niveis(self):
        r = self.client.get(reverse('novo_diagnostico'))
        self.assertContains(r, perguntas.PERGUNTAS['soc_riscos']['niveis'][3])
        self.assertContains(r, 'Não se aplica')

    def test_envio_completo_salva_e_mostra_resultado(self):
        r = self.client.post(reverse('novo_diagnostico'), post_completo(4))
        d = DiagnosticoESG.objects.get()
        self.assertRedirects(r, reverse('resultado_diagnostico', args=[d.pk]))
        self.assertEqual(d.versao_questionario, VERSAO_ATUAL)
        self.assertEqual(d.calcular_pontuacao()['geral'], 100.0)
        self.assertContains(self.client.get(reverse('resultado_diagnostico', args=[d.pk])), 'Gerenciado ou acima')

    def test_varejo_envia_sem_as_perguntas_de_producao(self):
        r = self.client.post(reverse('novo_diagnostico'), post_completo(3, tipo='varejo'))
        self.assertEqual(r.status_code, 302)
        self.assertNotIn('amb_efluentes', DiagnosticoESG.objects.get().respostas)

    def test_resposta_de_pergunta_nao_aplicavel_e_descartada(self):
        r = self.client.post(reverse('novo_diagnostico'), post_completo(3, tipo='varejo', q_amb_efluentes='4'))
        self.assertEqual(r.status_code, 302)
        self.assertNotIn('amb_efluentes', DiagnosticoESG.objects.get().respostas)

    def test_na_e_salvo_como_nulo(self):
        self.client.post(reverse('novo_diagnostico'), post_completo(3, q_amb_quimicos='na'))
        self.assertIsNone(DiagnosticoESG.objects.get().respostas['amb_quimicos'])

    def test_sem_todas_as_respostas_nao_salva(self):
        dados = post_completo(3)
        del dados['q_soc_riscos']
        r = self.client.post(reverse('novo_diagnostico'), dados)
        self.assertContains(r, 'ficaram sem resposta')
        self.assertEqual(DiagnosticoESG.objects.count(), 0)

    def test_sem_nome_nao_salva_e_mantem_respostas(self):
        r = self.client.post(reverse('novo_diagnostico'), post_completo(2, nome_empresa=''))
        self.assertEqual(DiagnosticoESG.objects.count(), 0)
        self.assertContains(r, 'value="2" checked')

    def test_parte_maior_que_total_rejeitada(self):
        self.client.post(reverse('novo_diagnostico'), post_completo(3, pessoas_lideranca='4', mulheres_lideranca='5'))
        self.assertEqual(DiagnosticoESG.objects.count(), 0)
        self.client.post(reverse('novo_diagnostico'), post_completo(3, kg_sobras_geradas='10', kg_sobras_reaproveitadas='11'))
        self.assertEqual(DiagnosticoESG.objects.count(), 0)

    def test_numeros_viram_percentual_calculado(self):
        self.client.post(reverse('novo_diagnostico'), post_completo(
            3, kg_sobras_geradas='200', kg_sobras_reaproveitadas='50', pessoas_lideranca='5', mulheres_lideranca='2'))
        d = DiagnosticoESG.objects.get()
        self.assertEqual(d.pct_residuos_reaproveitados, 25)
        self.assertEqual(d.pct_mulheres_lideranca, 40)

    def test_percentual_sem_total_e_nulo(self):
        self.client.post(reverse('novo_diagnostico'), post_completo(3))
        d = DiagnosticoESG.objects.get()
        self.assertIsNone(d.pct_residuos_reaproveitados)
        self.assertIsNone(d.pct_mulheres_lideranca)

    def test_horario_exibido_no_fuso_de_recife(self):
        from django.conf import settings
        self.assertEqual(settings.TIME_ZONE, 'America/Recife')


class PlanoDeAcaoTests(ComLogin):
    def setUp(self):
        super().setUp()
        respostas = {pid: 4 for pid in perguntas.PERGUNTAS}
        respostas['soc_riscos'] = 0
        respostas['gov_etica'] = 1
        self.d = criar('C', respostas, usuario=self.user)
        self.url = reverse('adicionar_ao_plano', args=[self.d.pk])

    def test_resultado_lista_proximo_passo_e_criterio(self):
        r = self.client.get(reverse('resultado_diagnostico', args=[self.d.pk]))
        self.assertContains(r, perguntas.PERGUNTAS['soc_riscos']['acoes'][0][0])
        self.assertContains(r, perguntas.PERGUNTAS['gov_etica']['acoes'][1][0])
        self.assertContains(r, 'Pronto quando')
        self.assertContains(r, '30 dias')

    def test_adicionar_uma_cria_atividade_com_detalhes(self):
        self.client.post(self.url, {'pergunta': 'gov_etica'})
        a = Atividade.objects.get()
        self.assertEqual(a.titulo, perguntas.PERGUNTAS['gov_etica']['acoes'][1][0])
        self.assertEqual((a.categoria, a.status), ('governanca', 'aguardando'))
        self.assertIn('Pronto quando', a.descricao)
        self.assertIn('60 dias', a.descricao)

    def test_nao_duplica(self):
        self.client.post(self.url, {'pergunta': 'gov_etica'})
        self.client.post(self.url, {'pergunta': 'gov_etica'})
        self.assertEqual(Atividade.objects.count(), 1)
        self.assertContains(self.client.get(reverse('resultado_diagnostico', args=[self.d.pk])), 'No plano')

    def test_adicionar_todas(self):
        self.client.post(self.url, {'todas': '1'})
        self.assertEqual(Atividade.objects.count(), 2)

    def test_ignora_pergunta_invalida_ou_adequada(self):
        self.client.post(self.url, {'pergunta': 'nao_existe'})
        self.client.post(self.url, {'pergunta': 'amb_energia'})
        self.assertEqual(Atividade.objects.count(), 0)

    def test_so_aceita_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_diagnostico_antigo_nao_gera_recomendacoes(self):
        antigo = DiagnosticoESG.objects.create(usuario=self.user, nome_empresa='Velho', codigo_etica=True)
        r = self.client.get(reverse('resultado_diagnostico', args=[antigo.pk]))
        self.assertContains(r, 'formato antigo')
        self.assertNotContains(r, 'O que fazer primeiro')
        self.client.post(reverse('adicionar_ao_plano', args=[antigo.pk]), {'todas': '1'})
        self.assertEqual(Atividade.objects.count(), 0)

    def test_excluir_diagnostico(self):
        self.assertEqual(self.client.post(reverse('deletar_diagnostico', args=[self.d.pk])).status_code, 200)
        self.assertEqual(DiagnosticoESG.objects.count(), 0)


class ArquivosSeparadosTests(TestCase):
    """Preferência do projeto: nada de CSS ou JavaScript dentro do HTML."""

    def test_nenhum_template_tem_css_ou_js_embutido(self):
        import pathlib, re
        raiz = pathlib.Path(__file__).resolve().parent.parent
        proibido = re.compile(r'<style|style="|<script(?![^>]*\bsrc=)|\son[a-z]+="', re.I)
        problemas = []
        for arq in raiz.rglob('*.html'):
            if 'venv' in arq.parts or 'staticfiles' in arq.parts:
                continue
            for n, linha in enumerate(arq.read_text(encoding='utf-8').splitlines(), 1):
                if proibido.search(linha):
                    problemas.append(f'{arq.relative_to(raiz)}:{n}')
        self.assertEqual(problemas, [])


class ArquivosEstaticosTests(ComLogin):
    def test_css_e_js_sao_servidos_sem_collectstatic(self):
        for caminho in ('css/base.css', 'css/diagnostico.css', 'js/base.js', 'js/diagnostico_form.js', 'js/evolucao.js'):
            r = self.client.get('/static/' + caminho)
            self.assertEqual(r.status_code, 200, caminho)

    def test_paginas_referenciam_os_arquivos(self):
        self.assertContains(self.client.get(reverse('novo_diagnostico')), '/static/js/diagnostico_form.js')
        self.assertContains(self.client.get(reverse('inicio')), '/static/css/base.css')


class AcessoPorUsuarioTests(TestCase):
    def setUp(self):
        self.dona = novo_usuario('dona', 'Dona')
        self.outra = novo_usuario('outra', 'Outra')
        self.d = criar('Da dona', usuario=self.dona)

    def test_visitante_vai_para_o_login(self):
        for nome, args in (('home', []), ('novo_diagnostico', []), ('resultado_diagnostico', [self.d.pk])):
            r = self.client.get(reverse(nome, args=args))
            self.assertEqual(r.status_code, 302, nome)
            self.assertIn('/login/', r['Location'])

    def test_metodologia_e_publica(self):
        self.assertEqual(self.client.get(reverse('metodologia_diagnostico')).status_code, 200)

    def test_outra_usuaria_nao_ve_nem_altera(self):
        self.client.force_login(self.outra)
        self.assertEqual(self.client.get(reverse('resultado_diagnostico', args=[self.d.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('adicionar_ao_plano', args=[self.d.pk]), {'todas': '1'}).status_code, 404)
        self.assertEqual(self.client.post(reverse('deletar_diagnostico', args=[self.d.pk])).status_code, 404)
        self.assertEqual(DiagnosticoESG.objects.count(), 1)

    def test_lista_mostra_so_os_proprios(self):
        criar('Da outra', usuario=self.outra)
        self.client.force_login(self.dona)
        r = self.client.get(reverse('home'))
        self.assertContains(r, 'Da dona')
        self.assertNotContains(r, 'Da outra')

    def test_novo_diagnostico_fica_ligado_ao_usuario(self):
        self.client.force_login(self.dona)
        self.client.post(reverse('novo_diagnostico'), post_completo(3))
        self.assertEqual(DiagnosticoESG.objects.filter(usuario=self.dona).count(), 2)


class MelhoriasVisuaisTests(ComLogin):
    def test_form_tem_barra_de_perguntas_respondidas(self):
        r = self.client.get(reverse('novo_diagnostico'))
        self.assertContains(r, 'id="barraRespondidas"')
        self.assertContains(r, 'Respondeu')

    def test_form_pede_numeros_e_nao_percentuais(self):
        r = self.client.get(reverse('novo_diagnostico'))
        self.assertContains(r, 'name="kg_sobras_geradas"')
        self.assertContains(r, 'name="pessoas_lideranca"')
        self.assertNotContains(r, 'name="pct_')

    def test_resultado_mostra_hora_selo_e_proximo_nivel(self):
        self.client.post(reverse('novo_diagnostico'), post_completo(2))
        d = DiagnosticoESG.objects.get()
        r = self.client.get(reverse('resultado_diagnostico', args=[d.pk]))
        self.assertContains(r, ' às ')
        self.assertContains(r, 'selo-nivel')
        self.assertContains(r, 'pontos para o nível')

    def test_sem_travessao_longo_nos_templates(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent
        for arquivo in base.rglob('*.html'):
            self.assertNotIn('—', arquivo.read_text(encoding='utf-8'), str(arquivo))


class ExportarPdfTests(ComLogin):
    def test_pdf_do_diagnostico(self):
        self.client.post(reverse('novo_diagnostico'), post_completo(2, kg_sobras_geradas='100', kg_sobras_reaproveitadas='20'))
        d = DiagnosticoESG.objects.get()
        r = self.client.get(reverse('resultado_pdf', args=[d.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/pdf')
        self.assertTrue(r.content.startswith(b'%PDF'))
        self.assertIn('attachment', r['Content-Disposition'])

    def test_pdf_de_outra_empresa_negado(self):
        self.client.post(reverse('novo_diagnostico'), post_completo(2))
        d = DiagnosticoESG.objects.get()
        self.client.logout()
        self.client.force_login(novo_usuario('outra', 'Outra'))
        self.assertEqual(self.client.get(reverse('resultado_pdf', args=[d.pk])).status_code, 404)

    def test_botao_de_exportar_no_resultado(self):
        self.client.post(reverse('novo_diagnostico'), post_completo(2))
        d = DiagnosticoESG.objects.get()
        self.assertContains(self.client.get(reverse('resultado_diagnostico', args=[d.pk])), 'Exportar em PDF')

    def test_pdf_de_diagnostico_com_cnpj_e_formato_antigo(self):
        from contas.models import Empresa
        Empresa.objects.create(usuario=self.user, cnpj='11222333000181')
        d = DiagnosticoESG.objects.create(usuario=self.user, nome_empresa='Antiga', residuos_textesis=True)
        r = self.client.get(reverse('resultado_pdf', args=[d.pk]))
        self.assertTrue(r.content.startswith(b'%PDF'))

    def test_pdf_da_evolucao(self):
        self.client.post(reverse('novo_diagnostico'), post_completo(1))
        self.client.post(reverse('novo_diagnostico'), post_completo(3))
        r = self.client.get(reverse('evolucao_pdf'))
        self.assertTrue(r.content.startswith(b'%PDF'))
        self.assertContains(self.client.get(reverse('evolucao')), 'Exportar em PDF')

    def test_pdf_da_evolucao_sem_dados_redireciona(self):
        self.assertRedirects(self.client.get(reverse('evolucao_pdf')), reverse('evolucao'))
