"""Banco de perguntas do diagnóstico ESG (questionário versão 3).

Como foi construído (detalhes na página /diagnostico/metodologia/):
- Temas: derivados do padrão setorial GRI para Têxteis e Vestuário (minuta em consulta pública),
  do Higg FEM (gestão ambiental), das áreas de risco do Guia OCDE para cadeias de vestuário,
  dos 7 temas centrais da ISO 26000, das áreas do B Impact Assessment e das NRs do setor (FIEMG).
- Escala: 5 níveis inspirados nos modelos de maturidade ESG da CrossCountry (Mindful, Defined,
  Managed, Integrated), da Oren (Compliant, Efficient, Strategic, Leader) e no escalonamento do
  Higg FEM (conformidade básica, metas e melhoria, ações avançadas).
- Cada pergunta tem uma descrição concreta para cada nível (âncoras), para reduzir respostas "no chute".
- Os PESOS e a nota de corte são decisão metodológica da equipe, explicada na metodologia.
"""

FONTES = {
    "gri": {
        "sigla": "GRI",
        "nome": "GRI — Padrão Setorial para Têxteis e Vestuário (minuta em consulta pública, 18 tópicos prováveis)",
        "url": "https://globalreporting.org/media/snzig5ft/gri-textiles-apparel-faq.pdf",
    },
    "higg": {
        "sigla": "Higg FEM",
        "nome": "Higg Facility Environmental Module (7 áreas ambientais e 3 níveis), conforme descrito pela HQTS",
        "url": "https://www.hqts.com/higg-fem-verification-audits/",
    },
    "oecd": {
        "sigla": "OCDE",
        "nome": "Guia OCDE de Devida Diligência para Cadeias de Vestuário e Calçados (áreas de risco e etapas), conforme resumido pela TexSpace Today",
        "url": "https://www.texspacetoday.com/oecd-issues-due-diligence-guidelines-for-responsible-fashion-supply-chain/",
    },
    "iso26000": {
        "sigla": "ISO 26000",
        "nome": "ISO 26000 — 7 temas centrais de responsabilidade social",
        "url": "https://www.fm2s.com.br/blog/iso-26000",
    },
    "bcorp": {
        "sigla": "B Impact",
        "nome": "B Impact Assessment (B Lab) — áreas: trabalhadores, comunidade, meio ambiente, clientes e governança",
        "url": "https://www.bcorporation.net/en-us/faq/what-topics-are-covered-b-impact-assessment/",
    },
    "orrick": {
        "sigla": "Orrick",
        "nome": "Orrick — ESG Maturity Model (8 componentes, 3 a 4 níveis cada)",
        "url": "https://media.orrick.com/Media%20Library/public/files/misc/2023/esg-maturity-model.pdf",
    },
    "crosscountry": {
        "sigla": "CrossCountry",
        "nome": "CrossCountry Consulting — ESG Maturity Model (Mindful, Defined, Managed, Integrated)",
        "url": "https://www.crosscountry-consulting.com/insights/blog/esg-maturity-model/",
    },
    "oren": {
        "sigla": "Oren",
        "nome": "Oren — níveis de maturidade ESG (Compliant, Efficient, Strategic, Leader)",
        "url": "https://www.orennow.com/blog/esg-maturity-guide-to-evaluating-your-companys-esg-progress",
    },
    "fiemg": {
        "sigla": "FIEMG/NRs",
        "nome": "FIEMG — E-book do Setor Vestuário (NR-1, NR-5, NR-6, NR-7, NR-12, NR-17, NR-26 aplicadas à confecção)",
        "url": "https://www.fiemg.com.br/wp-content/uploads/2024/09/EBOOK-DO-SETOR-VESTUARIO.pdf",
    },
    "abvtex": {
        "sigla": "ABVTEX",
        "nome": "Programa ABVTEX (185 requisitos: conformidade legal, direitos dos trabalhadores, gestão da cadeia e impactos ambientais)",
        "url": "https://abvtex.org.br/wp-content/uploads/2024/06/24mar07c-Curso-EAD-Programa-ABVTEX.pdf",
    },
}

# Escala de maturidade (0 a 4)
ESCALA = [
    (0, "Inexistente", "Ainda não fazemos"),
    (1, "Básico", "Fazemos o mínimo, de forma informal"),
    (2, "Definido", "Há regra, responsável e registro"),
    (3, "Gerenciado", "Medimos, acompanhamos e corrigimos"),
    (4, "Integrado", "Faz parte da estratégia e melhora todo ano"),
]
NOMES_NIVEL = {n: nome for n, nome, _ in ESCALA}

NIVEL_MAXIMO = 4
NIVEL_ALVO = 3          # "Gerenciado": abaixo disso a pergunta gera recomendação
PRAZO_POR_NIVEL = {0: 30, 1: 60, 2: 90}   # dias sugeridos para subir um nível

PORTES = [
    ("micro", "Microempresa (até 9 pessoas)"),
    ("pequena", "Pequena empresa (10 a 49 pessoas)"),
    ("media", "Média empresa (50 pessoas ou mais)"),
]

TIPOS_OPERACAO = [
    ("confeccao", "Confecção própria (produz as peças)"),
    ("faccao", "Facção / oficina de costura"),
    ("marca", "Marca que terceiriza a produção"),
    ("varejo", "Varejo / loja de moda"),
]
TODOS = ["confeccao", "faccao", "marca", "varejo"]
PRODUCAO = ["confeccao", "faccao"]


def _p(id, texto, peso, niveis, fontes, acoes, aplica=TODOS, permite_na=False):
    return {"id": id, "texto": texto, "peso": peso, "niveis": niveis, "fontes": fontes,
            "acoes": acoes, "aplica": aplica, "permite_na": permite_na}


PILARES = [
    {
        "chave": "ambiental", "nome": "Ambiental", "sigla": "E", "icone": "bi-tree",
        "subtemas": [
            {"chave": "gestao_ambiental", "nome": "Gestão ambiental", "perguntas": [
                _p("amb_gestao",
                   "A empresa mantém em dia as licenças e alvarás ambientais e tem alguém responsável pela gestão ambiental?", 2,
                   ["Não sabemos ao certo quais licenças ambientais se aplicam a nós",
                    "Temos as licenças exigidas, mas ninguém acompanha os prazos",
                    "Há responsável definido e um controle simples de licenças e prazos",
                    "Os impactos ambientais estão mapeados, com plano de ação acompanhado",
                    "Sistema de gestão ambiental com metas, revisão anual e melhoria contínua"],
                   ["higg", "iso26000"],
                   {0: ("Levantar com o órgão ambiental quais licenças e alvarás a empresa precisa e regularizar as pendentes",
                        "Lista das licenças exigidas, com a situação de cada uma"),
                    1: ("Nomear um responsável ambiental e criar planilha com licenças, validades e alertas de renovação",
                        "Responsável nomeado e planilha com datas de vencimento"),
                    2: ("Mapear os principais impactos ambientais (energia, água, resíduos, químicos) e montar plano de ação com prazos",
                        "Documento com impactos priorizados e ações com responsável e prazo")}),
            ]},
            {"chave": "energia", "nome": "Energia", "perguntas": [
                _p("amb_energia",
                   "O consumo de energia é medido e há ações para reduzi-lo ou usar fontes renováveis?", 2,
                   ["Não acompanhamos o consumo de energia",
                    "Olhamos a conta de luz, mas sem comparar meses nem agir",
                    "Registramos o consumo todo mês e já fizemos melhorias (ex.: lâmpadas LED)",
                    "Temos meta de redução e acompanhamos o resultado das ações",
                    "Meta de redução, fonte renovável e emissões calculadas, revisadas todo ano"],
                   ["gri", "higg"],
                   {0: ("Registrar em planilha o consumo (kWh) e o valor da conta de energia, mês a mês, por 3 meses",
                        "Planilha com 3 meses de consumo preenchidos"),
                    1: ("Trocar lâmpadas por LED, desligar equipamentos ociosos e avaliar energia solar ou contrato de energia renovável",
                        "Lista de melhorias feitas e consumo comparado antes e depois"),
                    2: ("Definir meta anual de redução de kWh (ex.: -10%) com responsável e revisar o resultado todo mês",
                        "Meta escrita com responsável e painel mensal atualizado")}),
            ]},
            {"chave": "agua", "nome": "Água e efluentes", "perguntas": [
                _p("amb_agua",
                   "O consumo de água é medido e há ações para reduzir o desperdício?", 2,
                   ["Não medimos o consumo de água",
                    "Acompanhamos só a conta, sem ações",
                    "Medimos o consumo e corrigimos vazamentos e desperdícios evidentes",
                    "Temos indicador (ex.: litros por peça) e meta de redução",
                    "Reutilizamos água, revisamos a meta todo ano e comparamos com referências do setor"],
                   ["higg", "gri"],
                   {0: ("Registrar o consumo de água (m³) todo mês, pela conta ou por hidrômetro, durante 3 meses",
                        "Planilha com 3 meses de consumo de água"),
                    1: ("Fazer vistoria de vazamentos e torneiras e orientar a equipe sobre o uso consciente da água",
                        "Checklist de vistoria preenchido e correções registradas"),
                    2: ("Definir indicador (litros por peça ou por pessoa) e meta de redução, com revisão a cada trimestre",
                        "Indicador calculado e meta registrada")},
                   aplica=PRODUCAO),
                _p("amb_efluentes",
                   "Os efluentes (água de lavagem, tingimento, lavanderia) são tratados e descartados conforme a lei?", 3,
                   ["Descartamos sem tratamento ou não sabemos o destino",
                    "Descartamos na rede comum sem verificar as exigências legais",
                    "Conhecemos a exigência legal e cumprimos o básico do descarte",
                    "Efluentes tratados e monitorados, com licença e laudos em dia",
                    "Tratamento além do exigido, metas de qualidade, reúso e laudos periódicos"],
                   ["higg", "gri", "oecd"],
                   {0: ("Identificar quais etapas geram efluente (lavagem, tingimento) e para onde ele vai, e consultar o órgão ambiental sobre a exigência",
                        "Mapa das etapas que geram efluente e do destino de cada uma"),
                    1: ("Regularizar o descarte conforme a orientação do órgão ambiental ou contratar empresa licenciada",
                        "Comprovante de regularização ou contrato com empresa licenciada"),
                    2: ("Fazer análise periódica do efluente e arquivar os laudos junto com a licença",
                        "Laudos recentes arquivados e calendário das próximas análises")},
                   aplica=PRODUCAO, permite_na=True),
            ]},
            {"chave": "quimicos", "nome": "Produtos químicos", "perguntas": [
                _p("amb_quimicos",
                   "Os produtos químicos (corantes, amaciantes, solventes, colas) são identificados, armazenados e usados com controle?", 3,
                   ["Não temos lista nem controle dos produtos químicos usados",
                    "Sabemos o que usamos, mas sem rótulo, ficha de segurança ou armazenamento adequado",
                    "Temos lista, rótulos preventivos, fichas de segurança e armazenamento adequado",
                    "Substituímos os produtos mais perigosos e treinamos quem os manuseia",
                    "Política de químicos com lista de substâncias restritas, exigida também dos fornecedores"],
                   ["higg", "gri", "fiemg"],
                   {0: ("Listar todos os produtos químicos usados, com quantidade e local de armazenamento",
                        "Planilha de inventário com todos os produtos"),
                    1: ("Rotular os produtos conforme a NR-26, reunir as fichas de segurança e organizar o armazenamento separado",
                        "Produtos rotulados e fichas de segurança acessíveis perto do local de uso"),
                    2: ("Identificar os produtos mais perigosos, testar substitutos e treinar quem os manuseia",
                        "Lista de substituições avaliadas e lista de presença do treinamento")},
                   aplica=PRODUCAO, permite_na=True),
            ]},
            {"chave": "residuos_materiais", "nome": "Resíduos e materiais", "perguntas": [
                _p("amb_residuos",
                   "Como a empresa trata sobras de tecido, peças descartadas e embalagens?", 2,
                   ["Tudo vai para o lixo comum",
                    "Aproveitamos algumas sobras quando dá, sem registro",
                    "Separamos os resíduos e damos destino regular (venda, doação, reciclagem)",
                    "Medimos quantidade e destino e temos meta de redução do desperdício",
                    "Encaixe de moldes otimizado, parcerias de reciclagem e relatório do que foi reaproveitado"],
                   ["gri", "higg"],
                   {0: ("Separar sobras de tecido, peças descartadas e embalagens em recipientes próprios e pesar o total gerado por 1 mês",
                        "Registro do peso mensal por tipo de resíduo"),
                    1: ("Fechar parceria com recicladora, artesãos ou cooperativa para destinar as sobras e registrar cada retirada",
                        "Parceria combinada e registro das retiradas"),
                    2: ("Calcular o % de resíduo reaproveitado e definir meta de redução de sobras, com revisão trimestral",
                        "Indicador calculado todo mês e meta escrita")}),
                _p("amb_materiais",
                   "Qual parte das matérias-primas e produtos comprados tem origem mais sustentável (orgânica, reciclada ou certificada)?", 2,
                   ["Escolhemos só por preço e disponibilidade",
                    "Usamos opções sustentáveis de forma ocasional",
                    "Temos itens regulares com matéria-prima orgânica, reciclada ou certificada",
                    "Há critério de escolha e meta de % de materiais de menor impacto",
                    "Meta crescente, certificações verificadas e comunicação transparente ao cliente"],
                   ["gri", "iso26000"],
                   {0: ("Escolher 1 matéria-prima ou produto para trocar por opção orgânica, reciclada ou certificada e pedir cotação",
                        "Cotação recebida e decisão registrada"),
                    1: ("Tornar a opção sustentável um item fixo da coleção e guardar os certificados do fornecedor",
                        "Item no catálogo e certificados arquivados"),
                    2: ("Definir critério de escolha de materiais e meta de % de itens de menor impacto para a próxima coleção",
                        "Critério por escrito e meta com prazo")},
                   aplica=["confeccao", "marca", "varejo"]),
            ]},
        ],
    },
    {
        "chave": "social", "nome": "Social", "sigla": "S", "icone": "bi-people",
        "subtemas": [
            {"chave": "direitos", "nome": "Direitos e condições de trabalho", "perguntas": [
                _p("soc_trabalho_digno",
                   "A empresa garante que não há trabalho infantil, trabalho forçado nem condições análogas à escravidão, nela e em seus terceirizados?", 3,
                   ["Nunca verificamos esse tema",
                    "Confiamos na boa-fé: sabemos que não ocorre, mas não verificamos",
                    "Conferimos idade e documentos na contratação e proibimos por política escrita",
                    "Verificamos também terceirizados e facções e temos canal para denúncias",
                    "Verificação periódica documentada, auditorias na cadeia e plano de correção"],
                   ["gri", "oecd", "abvtex"],
                   {0: ("Registrar por escrito o compromisso de não admitir trabalho infantil, forçado ou análogo ao escravo e conferir os documentos de todos os trabalhadores",
                        "Compromisso assinado pela direção e conferência de documentos concluída"),
                    1: ("Padronizar a conferência de idade e documentos na contratação e incluir a proibição nos contratos com terceiros",
                        "Checklist de admissão em uso e cláusula incluída nos contratos"),
                    2: ("Visitar facções e fornecedores com checklist (idade, jornada, alojamento, liberdade de saída) e abrir canal de denúncia",
                        "Relatório das visitas e canal de denúncia divulgado")}),
                _p("soc_remuneracao",
                   "Salários, jornada, horas extras e benefícios cumprem a lei e o piso da categoria, com registro formal?", 3,
                   ["Há pendências e não temos controle de jornada nem de horas extras",
                    "Cumprimos o essencial, mas com controle informal de jornada",
                    "Pagamos conforme a lei e o piso, com registro de jornada e contratos formais",
                    "Revisamos salários e horas extras periodicamente e reduzimos jornadas excessivas",
                    "Política de remuneração justa, comparada com o mercado, com indicadores e revisão anual"],
                   ["gri", "oecd"],
                   {0: ("Conferir o piso da categoria e a situação formal (carteira, FGTS, jornada) de todos os colaboradores e listar as pendências",
                        "Lista de pendências com responsável"),
                    1: ("Implantar registro de ponto e controle de horas extras e regularizar os contratos",
                        "Registro de ponto em uso e contratos regularizados"),
                    2: ("Revisar salários e horas extras todo semestre e traçar plano para reduzir jornadas excessivas",
                        "Relatório semestral de horas extras com plano de redução")}),
            ]},
            {"chave": "saude_seguranca", "nome": "Saúde e segurança", "perguntas": [
                _p("soc_riscos",
                   "A empresa identifica e controla os riscos de saúde e segurança do trabalho (PGR, CIPA ou designado, EPIs, exames)?", 3,
                   ["Não temos PGR nem programa de segurança",
                    "Fornecemos EPIs e fazemos exames, mas sem inventário de riscos",
                    "Temos PGR e exames ocupacionais em dia, com CIPA ou responsável designado",
                    "Acidentes e quase-acidentes são registrados e analisados, com plano de ação acompanhado",
                    "Indicadores de acidentes, metas de redução, treinamentos regulares e melhoria contínua"],
                   ["fiemg", "gri", "oecd"],
                   {0: ("Contratar ou designar profissional de segurança do trabalho para elaborar o PGR (inventário de riscos e plano de ação) da NR-1",
                        "PGR elaborado e assinado"),
                    1: ("Colocar em dia o PCMSO e os exames ocupacionais, entregar EPIs com ficha de controle e constituir CIPA ou designado",
                        "Exames em dia, fichas de EPI assinadas e CIPA ou designado nomeado"),
                    2: ("Criar registro de acidentes e quase-acidentes e analisar as causas a cada trimestre",
                        "Registro em uso e ata da primeira análise")}),
                _p("soc_ergonomia",
                   "Os postos de trabalho (costura, corte, estoque, loja) têm ergonomia adequada e máquinas com proteções?", 2,
                   ["Nunca avaliamos postos, mobiliário nem proteções das máquinas",
                    "Corrigimos problemas quando alguém reclama ou se machuca",
                    "Avaliamos postos e máquinas e corrigimos os riscos graves (cadeiras, iluminação, proteções)",
                    "Temos análise ergonômica (AET), pausas e manutenção registrada das máquinas",
                    "Revisão periódica com participação dos trabalhadores e indicadores de afastamento"],
                   ["fiemg", "gri"],
                   {0: ("Fazer ronda nos postos com checklist de cadeira, bancada, iluminação e proteções das máquinas",
                        "Checklist preenchido para todos os postos"),
                    1: ("Corrigir os itens críticos do checklist (cadeiras ajustáveis, proteção de agulha e correias, parada de emergência)",
                        "Itens críticos corrigidos e fotografados"),
                    2: ("Contratar a Análise Ergonômica do Trabalho (AET), definir pausas e registrar a manutenção das máquinas",
                        "Laudo de AET e planilha de manutenção em uso")}),
            ]},
            {"chave": "equidade_dialogo", "nome": "Equidade e diálogo", "perguntas": [
                _p("soc_equidade",
                   "A empresa promove igualdade de oportunidades e previne discriminação e assédio, incluindo equidade de gênero?", 2,
                   ["Não temos regras nem tratamos o tema",
                    "Não toleramos discriminação, mas sem regra escrita nem canal",
                    "Política escrita contra discriminação e assédio, divulgada à equipe",
                    "Canal de denúncia, critérios iguais de contratação e promoção e dados acompanhados (gênero, raça, PcD)",
                    "Metas de equidade, indicadores por cargo, ações de inclusão e revisão anual"],
                   ["gri", "oecd", "iso26000"],
                   {0: ("Escrever política curta contra discriminação e assédio e apresentá-la em reunião com toda a equipe",
                        "Política publicada e ata da reunião"),
                    1: ("Criar canal confidencial de denúncia de assédio e discriminação e definir como elas serão tratadas",
                        "Canal ativo e procedimento por escrito"),
                    2: ("Levantar a composição da equipe e da liderança por gênero e definir critérios iguais de contratação e promoção",
                        "Levantamento feito e critérios escritos")}),
                _p("soc_dialogo",
                   "Os trabalhadores têm voz: reuniões, pesquisa de clima ou diálogo com o sindicato?", 2,
                   ["Não há espaço formal de escuta",
                    "A conversa acontece, mas só informalmente com a chefia",
                    "Reuniões periódicas e canal de sugestões",
                    "Pesquisa de clima anual, respeito às negociações coletivas e retorno aos colaboradores",
                    "Representantes da equipe participam de decisões e as melhorias são acompanhadas"],
                   ["gri", "oecd"],
                   {0: ("Marcar reunião mensal curta com a equipe para ouvir problemas e sugestões e registrar os pontos",
                        "Primeira ata e lista de pendências"),
                    1: ("Criar canal de sugestões (caixa ou formulário) e divulgar à equipe as respostas e decisões",
                        "Canal ativo e primeiro retorno divulgado"),
                    2: ("Aplicar pesquisa de clima anônima, divulgar os resultados e definir 3 melhorias",
                        "Resultados divulgados e 3 melhorias com prazo")}),
            ]},
            {"chave": "pessoas_comunidade", "nome": "Pessoas e comunidade", "perguntas": [
                _p("soc_capacitacao",
                   "A equipe recebe treinamentos e tem possibilidade de crescer dentro da empresa?", 1,
                   ["Não há treinamento",
                    "Treinamos só quando surge uma necessidade",
                    "Há integração de novos colaboradores e treinamento de segurança para todos",
                    "Plano anual de capacitação com registro de horas por pessoa",
                    "Plano de carreira, mentorias, avaliação dos resultados e meta de horas"],
                   ["iso26000", "bcorp"],
                   {0: ("Treinar a equipe nas regras de segurança e no uso das máquinas e registrar a presença",
                        "Lista de presença do primeiro treinamento"),
                    1: ("Criar um treinamento de integração padrão para novos colaboradores",
                        "Roteiro aprovado e aplicado a 1 novo colaborador"),
                    2: ("Montar o calendário anual de treinamentos e registrar as horas por pessoa",
                        "Calendário aprovado e planilha de horas")}),
                _p("soc_comunidade",
                   "A empresa se envolve com a comunidade local (compras locais, projetos sociais, geração de renda)?", 1,
                   ["Não temos relação com a comunidade",
                    "Ajudamos em ações esporádicas",
                    "Mantemos uma ação regular (doação de sobras, compra local, vagas locais)",
                    "Ações planejadas, com parceiros e resultado acompanhado",
                    "Programa estruturado, com metas, escuta da comunidade e divulgação de resultados"],
                   ["iso26000", "bcorp"],
                   {0: ("Escolher uma ação viável de apoio à comunidade (doar sobras a artesãos, priorizar fornecedor local) e realizá-la uma vez",
                        "Ação realizada e registrada"),
                    1: ("Transformar a ação em rotina, por exemplo doação mensal de retalhos a uma associação",
                        "Parceria combinada e calendário de repetição"),
                    2: ("Definir objetivo e indicador da ação (famílias atendidas, kg doados) e revisar os resultados a cada semestre",
                        "Indicador registrado e relatório semestral")}),
            ]},
        ],
    },
    {
        "chave": "governanca", "nome": "Governança", "sigla": "G", "icone": "bi-building",
        "subtemas": [
            {"chave": "etica", "nome": "Ética e integridade", "perguntas": [
                _p("gov_etica",
                   "Existe Código de Ética e Conduta formalizado, conhecido por todos e com consequências definidas?", 2,
                   ["Não existe código nem regras de conduta",
                    "Há regras de conduta, mas não escritas",
                    "Código escrito e entregue a todos",
                    "Código treinado, assinado e aplicado, com medidas para quebras de conduta",
                    "Código revisado todo ano, estendido a fornecedores e acompanhado pela direção"],
                   ["iso26000", "bcorp"],
                   {0: ("Redigir um Código de Ética e Conduta de 1 a 2 páginas com princípios e comportamentos esperados",
                        "Código aprovado pela direção"),
                    1: ("Apresentar o código em reunião, entregar cópia a cada colaborador e colher assinatura de ciência",
                        "Assinaturas de ciência arquivadas"),
                    2: ("Definir as medidas para quebras de conduta e incluir o código no treinamento de integração",
                        "Procedimento disciplinar escrito e código no treinamento de integração")}),
                _p("gov_anticorrupcao",
                   "Há política anticorrupção e canal para denúncias e reclamações, de empregados e de terceiros?", 3,
                   ["Não temos política nem canal",
                    "Informalmente, é possível falar com a direção",
                    "Política anticorrupção escrita e canal de denúncia divulgado",
                    "Canal confidencial com protocolo de apuração e retorno a quem denunciou",
                    "Canal independente, análise periódica das denúncias, treinamentos e avaliação de risco de corrupção"],
                   ["gri", "oecd"],
                   {0: ("Definir uma pessoa e um e-mail ou formulário para receber denúncias e dúvidas e avisar a equipe",
                        "Canal criado e comunicado"),
                    1: ("Escrever política anticorrupção (brindes, propina, relação com fiscalização) e divulgar a equipe e fornecedores",
                        "Política publicada e comunicada"),
                    2: ("Estabelecer protocolo de apuração e resposta às denúncias, com sigilo e proteção contra retaliação",
                        "Protocolo escrito e registro dos casos")}),
            ]},
            {"chave": "cadeia", "nome": "Cadeia de fornecimento", "perguntas": [
                _p("gov_rastreio",
                   "A empresa sabe a origem (fornecedor, país, tipo de fibra) dos materiais e produtos que usa?", 2,
                   ["Só conhecemos o fornecedor direto",
                    "Temos cadastro dos fornecedores diretos",
                    "Sabemos a origem dos principais materiais",
                    "Rastreamos origem e etapas até o produto final nos itens principais",
                    "Rastreabilidade completa, com documentos e verificação periódica"],
                   ["gri", "oecd"],
                   {0: ("Montar cadastro com dados e documentos de todos os fornecedores diretos",
                        "Planilha de fornecedores completa"),
                    1: ("Perguntar aos 5 principais fornecedores a origem das matérias-primas e registrar as respostas",
                        "Respostas dos 5 principais fornecedores registradas"),
                    2: ("Mapear as etapas (fibra, fiação, tecelagem, beneficiamento, confecção) dos itens mais vendidos",
                        "Mapa da cadeia dos itens principais")},
                   aplica=["confeccao", "marca", "varejo"]),
                _p("gov_compras",
                   "A escolha e a avaliação de fornecedores consideram critérios sociais e ambientais, e não só o preço?", 2,
                   ["Escolhemos só por preço e prazo",
                    "Consideramos reputação e qualidade, sem critério socioambiental formal",
                    "Exigimos documentos básicos (CNPJ, regularidade, licenças) e um compromisso de conduta",
                    "Avaliamos riscos sociais e ambientais dos fornecedores e priorizamos os melhores",
                    "Auditorias periódicas, plano de melhoria com fornecedores e critério socioambiental na decisão de compra"],
                   ["gri", "oecd"],
                   {0: ("Definir 3 critérios mínimos para escolher fornecedores (regularidade legal, trabalho decente, licença ambiental)",
                        "Critérios escritos e aprovados"),
                    1: ("Criar formulário de homologação e exigir documentos e compromisso de conduta de cada fornecedor novo",
                        "Formulário em uso e fornecedores novos homologados"),
                    2: ("Classificar fornecedores por risco social e ambiental e priorizar visitas aos de maior risco",
                        "Matriz de risco e cronograma de visitas")}),
                _p("gov_terceirizados",
                   "A empresa conhece e verifica as oficinas e facções que produzem para ela?", 3,
                   ["Contratamos sem lista nem contrato formal",
                    "Temos lista de facções e contrato informal",
                    "Contrato formal e verificação documental (CNPJ, regularidade trabalhista)",
                    "Visitas periódicas com checklist de condições de trabalho e plano de correção",
                    "Programa de desenvolvimento das facções, auditorias e participação em programa de certificação (ex.: ABVTEX)"],
                   ["oecd", "abvtex", "gri"],
                   {0: ("Listar todas as oficinas e facções com endereço, responsável e volume produzido",
                        "Lista completa e atualizada"),
                    1: ("Formalizar contrato com cláusulas de trabalho decente e pedir a documentação trabalhista de cada facção",
                        "Contratos assinados e documentos arquivados"),
                    2: ("Visitar cada facção com checklist de condições de trabalho e registrar plano de correção",
                        "Relatório das visitas e plano de correção por facção")},
                   aplica=["confeccao", "marca"], permite_na=True),
            ]},
            {"chave": "gestao_esg", "nome": "Gestão ESG", "perguntas": [
                _p("gov_metas",
                   "A direção definiu prioridades, metas e responsáveis para os temas ESG?", 2,
                   ["Não há prioridades nem metas ESG",
                    "Há intenção, mas sem prioridades escritas",
                    "Temos prioridades escritas e responsável definido",
                    "Metas mensuráveis com prazo, acompanhadas pela direção",
                    "Metas ligadas à estratégia e à remuneração, revisadas todo ano"],
                   ["orrick", "crosscountry"],
                   {0: ("Reunir a direção e listar os 5 temas ESG mais importantes para o negócio, ouvindo equipe e clientes",
                        "Lista de prioridades aprovada"),
                    1: ("Nomear um responsável ESG e transformar as prioridades em um plano de ação escrito",
                        "Responsável nomeado e plano escrito"),
                    2: ("Transformar cada prioridade em meta mensurável com prazo (ex.: reduzir 10% das sobras em 12 meses) e revisar a cada trimestre",
                        "Metas registradas e primeira revisão feita")}),
                _p("gov_dados",
                   "Os indicadores ESG são coletados, conferidos e acompanhados de forma organizada?", 1,
                   ["Não coletamos indicadores",
                    "Temos alguns números soltos",
                    "Planilha com indicadores principais e responsável por atualizá-la",
                    "Indicadores conferidos, atualizados todo mês e usados em decisões",
                    "Sistema centralizado, com controle de qualidade dos dados e revisão independente"],
                   ["orrick", "crosscountry"],
                   {0: ("Escolher 5 indicadores ESG simples (kWh, água, resíduo, acidentes, horas de treinamento) e começar a registrá-los",
                        "Planilha com o primeiro mês preenchido"),
                    1: ("Definir responsável e um dia fixo do mês para atualizar a planilha de indicadores",
                        "Responsável nomeado e 3 meses seguidos atualizados"),
                    2: ("Criar rotina de conferência dos dados e apresentar os indicadores à direção a cada trimestre",
                        "Ata da reunião trimestral com os indicadores")}),
            ]},
            {"chave": "transparencia", "nome": "Transparência", "perguntas": [
                _p("gov_transparencia",
                   "A empresa comunica seus resultados e práticas de forma transparente e verdadeira (relatório, rótulos, redes, clientes)?", 1,
                   ["Não comunicamos",
                    "Comunicamos de forma pontual, sem verificar as afirmações",
                    "Divulgamos práticas e certificações reais no site, nas redes e nos rótulos",
                    "Relatório anual simples com indicadores e metas, com afirmações apoiadas em evidências",
                    "Relatório em padrão reconhecido (ex.: GRI), com verificação externa"],
                   ["gri", "oecd", "orrick"],
                   {0: ("Listar o que a empresa já faz de ESG, com evidências, e revisar as afirmações de marketing para evitar exageros",
                        "Lista com evidências e afirmações revisadas"),
                    1: ("Publicar no site ou nas redes uma página com as práticas e certificações reais e conferir os rótulos das peças",
                        "Página publicada e rótulos conferidos"),
                    2: ("Publicar um relatório anual de 2 a 4 páginas com indicadores, metas e resultados",
                        "Relatório publicado")}),
            ]},
        ],
    },
]

PERGUNTAS = {
    p["id"]: {**p, "pilar": pilar["chave"], "subtema": sub["nome"]}
    for pilar in PILARES for sub in pilar["subtemas"] for p in sub["perguntas"]
}

NA = None  # resposta "não se aplica" (só em perguntas com permite_na)


def aplicaveis(tipo_operacao):
    """Perguntas que valem para o tipo de operação (todas, se o tipo for desconhecido)."""
    if tipo_operacao not in TODOS:
        return dict(PERGUNTAS)
    return {pid: p for pid, p in PERGUNTAS.items() if tipo_operacao in p["aplica"]}


def _percentual(perguntas, respostas):
    """Média ponderada só das perguntas respondidas (ignora 'não se aplica')."""
    validas = [p for p in perguntas if respostas.get(p["id"]) is not None]
    total = sum(p["peso"] for p in validas)
    if not total:
        return None
    obtido = sum(p["peso"] * respostas[p["id"]] / NIVEL_MAXIMO for p in validas)
    return round(obtido / total * 100, 1)


def pontuar(respostas):
    """Notas por pilar e por subtema (0 a 100). Subtemas sem pergunta respondida são omitidos."""
    pilares = {}
    for pilar in PILARES:
        subtemas, todas = [], []
        for sub in pilar["subtemas"]:
            todas.extend(sub["perguntas"])
            pct = _percentual(sub["perguntas"], respostas)
            if pct is not None:
                subtemas.append({"nome": sub["nome"], "pct": pct})
        pilares[pilar["chave"]] = {"pct": _percentual(todas, respostas) or 0.0, "subtemas": subtemas}
    return pilares


def recomendacoes(respostas, limite=10):
    """Próximo passo de cada pergunta abaixo do nível alvo, ordenado por impacto e depois por prazo."""
    itens = []
    for p in PERGUNTAS.values():
        nivel = respostas.get(p["id"])
        if nivel is None or nivel >= NIVEL_ALVO:
            continue
        acao, pronto = p["acoes"][nivel]
        impacto = (NIVEL_ALVO - nivel) * p["peso"]
        itens.append({
            "id": p["id"], "acao": acao, "pronto": pronto, "categoria": p["pilar"], "subtema": p["subtema"],
            "nivel": nivel, "nivel_nome": NOMES_NIVEL[nivel], "proximo_nome": NOMES_NIVEL[nivel + 1],
            "prazo": PRAZO_POR_NIVEL[nivel], "impacto": impacto,
            "prioridade": "Alta" if impacto >= 6 else "Média" if impacto >= 3 else "Baixa",
            "fontes": [FONTES[f]["sigla"] for f in p["fontes"]],
        })
    itens.sort(key=lambda i: (-i["impacto"], i["prazo"], i["id"]))
    return itens[:limite]


def pontos_fortes(respostas, limite=4):
    itens = [
        {"subtema": p["subtema"], "nivel": respostas[p["id"]], "nivel_nome": NOMES_NIVEL[respostas[p["id"]]],
         "peso": p["peso"], "descricao": p["niveis"][respostas[p["id"]]]}
        for p in PERGUNTAS.values()
        if respostas.get(p["id"]) is not None and respostas[p["id"]] >= NIVEL_ALVO
    ]
    itens.sort(key=lambda i: (-i["nivel"], -i["peso"], i["subtema"]))
    return itens[:limite]


def ler_respostas(post, tipo_operacao):
    """Lê 'q_<id>' do POST só das perguntas que valem para o tipo de operação.

    Devolve (respostas, ids_sem_resposta). 'na' vira None e só é aceito em perguntas com permite_na.
    """
    respostas, faltando = {}, []
    for pid, p in aplicaveis(tipo_operacao).items():
        valor = post.get(f"q_{pid}")
        if valor == "na" and p["permite_na"]:
            respostas[pid] = NA
        elif valor is not None and valor.isdigit() and 0 <= int(valor) <= NIVEL_MAXIMO:
            respostas[pid] = int(valor)
        else:
            faltando.append(pid)
    return respostas, faltando
