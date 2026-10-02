# Histórias de Usuário — Vastra

Plataforma de gestão ESG para PMEs (confecções e negócios têxteis).
Cada história segue o formato **Como / Quero / Para** e tem cenários de validação em **BDD** (Dado / Quando / Então).

| # | História | Prioridade |
|---|---|---|
| H1 | IA no diagnóstico ESG | Média |
| H2 | Quadro de atividades | Alta |
| H3 | Sistema de avaliação com ranks (Bronze, Prata, Ouro) | Alta |
| H4 | Evolução ESG com diferentes gráficos | Alta |
| H5 | Rede social entre empresas | Baixa |
| H6 | Biblioteca de tutoriais e vídeos | Média |

---

## H1 — IA no diagnóstico ESG

**Como** gestor(a) de uma confecção,
**quero** receber recomendações geradas por IA com base nas minhas respostas do diagnóstico,
**para** saber quais ações práticas devo priorizar para melhorar minha nota ESG.

### Cenários

**Cenário 1: Recomendações após o diagnóstico**
- **Dado** que respondi o diagnóstico ESG e vi minha pontuação
- **Quando** clico em "Gerar recomendações com IA"
- **Então** o sistema exibe uma lista de sugestões personalizadas, organizadas por Ambiental, Social e Governança

**Cenário 2: Foco nos pontos fracos**
- **Dado** que minha pontuação Ambiental é menor que as demais
- **Quando** a IA gera as recomendações
- **Então** as primeiras sugestões listadas são da categoria Ambiental

**Cenário 3: Falha do serviço de IA**
- **Dado** que o serviço de IA está indisponível
- **Quando** clico em "Gerar recomendações com IA"
- **Então** o sistema exibe uma mensagem de erro amigável e mantém meu resultado do diagnóstico visível

---

## H2 — Quadro de atividades

**Como** gestor(a) de uma confecção,
**quero** organizar minhas ações de sustentabilidade em um quadro com colunas de status,
**para** acompanhar o que está aguardando início, em andamento e concluído.

### Cenários

**Cenário 1: Criar atividade**
- **Dado** que estou na página do quadro de atividades
- **Quando** preencho título e categoria (Ambiental, Social ou Governança) e clico em "Adicionar"
- **Então** a atividade aparece na coluna "Aguardando início"

**Cenário 2: Mudar o status**
- **Dado** que existe uma atividade na coluna "Aguardando início"
- **Quando** mudo o status dela para "Em andamento"
- **Então** a atividade passa a aparecer na coluna "Em andamento" e os contadores das colunas são atualizados

**Cenário 3: Título obrigatório**
- **Dado** que estou criando uma atividade
- **Quando** tento adicionar sem preencher o título
- **Então** o sistema mostra uma mensagem de erro e não cria a atividade

---

## H3 — Sistema de avaliação com ranks (Bronze, Prata e Ouro)

**Como** gestor(a) de uma confecção,
**quero** ver um rank (Bronze, Prata ou Ouro) baseado na minha nota ESG geral,
**para** entender rapidamente meu nível de maturidade e ter uma meta clara para evoluir.

### Regra de classificação

| Rank | Nota geral |
|---|---|
| Bronze | abaixo de 50% |
| Prata | de 50% a 79,9% |
| Ouro | 80% ou mais |

### Cenários

**Cenário 1: Rank Bronze**
- **Dado** que meu diagnóstico resultou em nota geral abaixo de 50%
- **Quando** visualizo o resultado
- **Então** vejo o selo "Bronze" ao lado da minha nota

**Cenário 2: Rank Prata**
- **Dado** que meu diagnóstico resultou em nota geral de 50% a 79,9%
- **Quando** visualizo o resultado
- **Então** vejo o selo "Prata" ao lado da minha nota

**Cenário 3: Rank Ouro**
- **Dado** que meu diagnóstico resultou em nota geral de 80% ou mais
- **Quando** visualizo o resultado
- **Então** vejo o selo "Ouro" ao lado da minha nota

**Cenário 4: Quanto falta para o próximo rank**
- **Dado** que estou no rank Bronze ou Prata
- **Quando** visualizo o resultado
- **Então** o sistema mostra quantos pontos percentuais faltam para o próximo rank

---

## H4 — Evolução ESG com diferentes gráficos

**Como** gestor(a) de uma confecção,
**quero** ver a evolução das minhas notas ESG em diferentes tipos de gráfico,
**para** analisar meu progresso ao longo do tempo e comparar as três dimensões.

### Cenários

**Cenário 1: Gráfico de linha da evolução**
- **Dado** que realizei mais de um diagnóstico em datas diferentes
- **Quando** acesso a página de evolução
- **Então** vejo um gráfico de linha com a nota geral em cada diagnóstico

**Cenário 2: Comparativo entre dimensões**
- **Dado** que estou na página de evolução
- **Quando** seleciono o gráfico de barras ou radar
- **Então** vejo as notas Ambiental, Social e Governança lado a lado

**Cenário 3: Dados insuficientes**
- **Dado** que realizei apenas um diagnóstico
- **Quando** acesso a página de evolução
- **Então** o sistema informa que é preciso ao menos dois diagnósticos para mostrar a evolução

---

## H5 — Rede social entre empresas

**Como** gestor(a) de uma confecção,
**quero** publicar e comentar em um feed compartilhado com outras empresas,
**para** trocar experiências e pedir ajuda sobre práticas sustentáveis.

### Cenários

**Cenário 1: Publicar no feed**
- **Dado** que estou na página da comunidade
- **Quando** escrevo um texto e clico em "Publicar"
- **Então** minha publicação aparece no topo do feed com o nome da minha empresa e a data

**Cenário 2: Comentar**
- **Dado** que existe uma publicação de outra empresa
- **Quando** escrevo e envio um comentário
- **Então** o comentário aparece abaixo da publicação

**Cenário 3: Publicação vazia**
- **Dado** que estou na página da comunidade
- **Quando** tento publicar sem escrever nada
- **Então** o sistema não publica e exibe uma mensagem de erro

---

## H6 — Biblioteca de tutoriais e vídeos

**Como** gestor(a) de uma confecção,
**quero** acessar uma biblioteca com tutoriais e vídeos explicativos sobre ESG,
**para** aprender a aplicar boas práticas no meu negócio.

### Cenários

**Cenário 1: Listar conteúdos**
- **Dado** que existem conteúdos cadastrados na biblioteca
- **Quando** acesso a página "Biblioteca"
- **Então** vejo a lista de tutoriais com título, categoria e tipo (vídeo ou texto)

**Cenário 2: Filtrar por categoria**
- **Dado** que estou na biblioteca
- **Quando** seleciono a categoria "Ambiental"
- **Então** vejo apenas os conteúdos dessa categoria

**Cenário 3: Assistir a um vídeo**
- **Dado** que estou na biblioteca
- **Quando** clico em um conteúdo do tipo vídeo
- **Então** a página do conteúdo abre com o vídeo incorporado e uma descrição
