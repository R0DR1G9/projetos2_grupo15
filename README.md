# [Vastra] — Plataforma de Gestão ESG para PMEs

## 📋 Descrição do Projeto

Plataforma web para pequenas e médias empresas acompanharem seus indicadores, metas e ações de sustentabilidade (ESG — Ambiental, Social e Governança) em um único painel centralizado, inspirada na análise de mercado de ferramentas como Paresi, ESG Business, Minha Pegada, Orkea e EcoVadis.

## 🧭 Páginas do site

| Página | URL | Descrição |
|---|---|---|
| Diagnóstico (Início) | `/` | Formulário e resultados do diagnóstico de maturidade ESG |
| Sobre o projeto | `/sobre/` | O que estamos construindo, para quem, e como chegamos até aqui |
| Quem somos | `/quem-somos/` | Integrantes da equipe |
| Fale conosco | `/contato/` | Formulário de contato (bug, sugestão, dúvida) — respostas ficam salvas no banco e são visíveis no `/admin/` |
| Quadro de atividades | `/atividades/` | Quadro com colunas de status (Aguardando início, Em andamento, Concluído) para as ações de sustentabilidade (H2) |
| Evolução ESG | `/evolucao/` | Gráficos de linha, barras e radar com a evolução das notas ESG entre diagnósticos (H4) |
| Ranking | `/ranking/` | Rank Bronze, Prata ou Ouro baseado na nota ESG geral (H3) |

## 👥 Equipe

- Rodrigo Barbosa
- Joao Miguel
- Arthur Siqueira
- Rafael Queiroz
- Fernando Sotero
- Joao Victor Moraes
- Paulo Andre
- Marina Pontes
- Ana Beatriz
- Maria Clara
- Daniel

## 📄 Documentação

- [Documento de Análise de Competidores](./relatório_de_análise_de_competidores.md) — benchmark com 5 concorrentes, pontos fortes/fracos e requisitos levantados
- [Histórias de Usuário](./historias.md) — 6 histórias no formato Como/Quero/Para, com cenários de validação em BDD (Dado/Quando/Então)

## ✅ Requisitos do Produto (não triviais)

1. **Matriz de setores ESG filtrável** — o sistema deve permitir visualizar e filtrar indicadores por categoria (Ambiental, Social, Governança/Econômico) e por "Todos", cruzando dados de diferentes frentes em uma única matriz.
2. **Painel de indicadores com meta e progresso** — o sistema deve calcular e exibir o percentual de atingimento de uma meta (ex: 60%) com barra de progresso, junto de métricas auxiliares (nº total de tarefas, % de tarefas em dia/TPR, status de faturamento ativo).
3. **Comparativo de desempenho por período** — o sistema deve gerar um gráfico de evolução (ex: linha temporal) comparando o desempenho do período atual com o anterior, calculando automaticamente a variação percentual (ex: +14%).
4. **Gestão de status de ações** — o sistema deve classificar e contabilizar ações em pelo menos três estados (em andamento, aguardando início, concluídas), permitindo atualização do status por meio de checkboxes.
5. **Acompanhamento de metas trimestrais de ações sustentáveis** — o sistema deve rastrear o progresso de ações sustentáveis planejadas versus realizadas dentro de um período trimestral (ex: 4/10 ações), exibindo o percentual concluído.

## 📊 Benchmark

Tabela comparativa disponível no [documento de análise de competidores](./relatório_de_análise_de_competidores.md).

## 📦 Entrega 03

### Histórias implementadas

**H2: Quadro de atividades**
- Como gestor(a) de uma confecção, quero organizar minhas ações de sustentabilidade em um quadro com colunas de status, para acompanhar o que está aguardando, em andamento e concluído.
- Página: `/atividades/`

**H3: Ranks Bronze, Prata e Ouro**
- Como gestor(a) de uma confecção, quero ver um rank baseado na minha nota ESG geral, para entender meu nível de maturidade e ter uma meta clara.
- Página: `/ranking/`

**H4: Evolução ESG com diferentes gráficos**
- Como gestor(a) de uma confecção, quero ver a evolução das minhas notas em diferentes tipos de gráfico, para analisar meu progresso ao longo do tempo.
- Página: `/evolucao/`

## 🖼️ Quadro da Sprint

### Sprint 01

![Quadro da Sprint 01](./assets/imagem_2026-09-22_102016016.png)

### Sprint 02

![Quadro da Sprint 02](./assets/imagem_2026-09-22_180543355.png)

### Sprint 03 — Backlog (JIRA)

![Backlog da Sprint 03 no JIRA](./assets/jira_backlog_sprint03.png)

### Sprint 03 — Quadro

<!-- TODO: adicionar aqui o print do quadro da Sprint 03 (SCRUM-40), ex.: ![Quadro da Sprint 03](./assets/NOME_DA_IMAGEM.png) -->

## 🐛 Issue Tracker

Bugs e pendências são registrados nas [Issues do repositório no GitHub](https://github.com/R0DR1G9/projetos2_grupo15/issues).

**Issues abertas**

![Issues abertas no GitHub](./assets/issues_abertas.png)

**Issues fechadas** (histórias H2, H3 e H4 implementadas)

![Issues fechadas no GitHub](./assets/issues_fechadas.png)

## 🚀 Deploy

- **URL em produção:** https://projetos2-grupo15.onrender.com
- **Como rodar localmente:**
```bash
git clone https://github.com/R0DR1G9/projetos2_grupo15.git
cd projetos2_grupo15
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 🎥 Screencasts

### Funcionalidades anteriores (Entrega 02)

- **Uso do sistema:** [link do YouTube](https://youtu.be/2ni9VbnhRu0)
- **Explicação do código:** [link do YouTube](https://youtu.be/rq166RePr94)

### Novas funcionalidades — Entrega 03 (H2, H3 e H4)

Vídeos gravados apenas com as funcionalidades novas (Quadro de atividades, Ranking e Evolução ESG). Os vídeos da Entrega 02 acima continuam valendo para as funcionalidades anteriores.

- **Uso do sistema** (com a URL do site em produção aparecendo): _link do YouTube em breve_
- **Explicação do código** (da URL até view, template e model): _link do YouTube em breve_

## 🔗 Acesso ao Repositório

- **Repositório GitHub:** https://github.com/R0DR1G9/projetos2_grupo15
- **Como clonar:**
```bash
  git clone https://github.com/R0DR1G9/projetos2_grupo15.git
```

## 🛠️ Tecnologias (previstas)

- [x] Backend: Django 
- [x] Frontend: HTML/CSS
- [X] Banco de dados: Sqlite
- [x] Interface: Bootstrap 5
- [x] Gráficos: Chart.js (aba Evolução ESG)

