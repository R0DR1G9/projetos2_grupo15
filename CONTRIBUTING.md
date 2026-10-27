# Como contribuir com o Vastra

Obrigado por ajudar! Este guia explica como rodar o projeto, como organizar o trabalho e o que o pipeline confere antes de qualquer código entrar na `main`.

## Sumário

1. [Visão geral](#visão-geral)
2. [Rodando o projeto na sua máquina](#rodando-o-projeto-na-sua-máquina)
3. [Estrutura do repositório](#estrutura-do-repositório)
4. [Fluxo de trabalho](#fluxo-de-trabalho)
5. [Testes e pipeline (CI)](#testes-e-pipeline-ci)
6. [Padrões do projeto](#padrões-do-projeto)
7. [Variáveis de ambiente e deploy](#variáveis-de-ambiente-e-deploy)
8. [Como reportar um problema](#como-reportar-um-problema)

## Visão geral

O Vastra é uma plataforma web de gestão ESG para PMEs, feita com **Django 5** e **SQLite** (local). Em produção usa **Postgres (Neon)** e é publicada no **Vercel**. O que o produto faz está descrito no [README](./README.md), e as histórias de usuário estão em [historias.md](./historias.md).

## Rodando o projeto na sua máquina

Você precisa de **Python 3.12** e **Git**.

```bash
git clone https://github.com/R0DR1G9/projetos2_grupo15.git
cd projetos2_grupo15
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

No Windows, ative o ambiente com `venv\Scripts\activate`.

Abra http://127.0.0.1:8000/ e crie uma conta em `/cadastro/`. O banco local é o arquivo `db.sqlite3`, que **não** vai para o GitHub. Para criar um administrador do `/admin/`, rode `python manage.py createsuperuser`.

## Estrutura do repositório

| Pasta | O que tem |
|---|---|
| `setup/` | Configurações do Django (`settings.py`) e rotas gerais |
| `templates/` | Layout base (`base.html`) usado por todas as páginas |
| `static/css/` e `static/js/` | CSS e JavaScript compartilhados |
| `inicio/` | Painel inicial |
| `diagnostico/` | Diagnóstico de maturidade ESG (perguntas, pontuação, recomendações) |
| `atividades/` | Quadro de atividades / Plano de Ação (H2) |
| `ranking/` | Ranks Bronze, Prata e Ouro (H3) |
| `evolucao/` | Gráficos de evolução (H4) |
| `rede_social/` e `mensagens/` | Rede social entre empresas e mensagens privadas |
| `contas/` | Login, cadastro e saída |
| `institucional/` | Sobre, Quem somos e Fale conosco |

Cada app tem o seu próprio `models.py`, `views.py`, `urls.py`, `tests.py` e a pasta `templates/` (e `static/`, quando precisa).

## Fluxo de trabalho

1. **Atualize a `main`:** `git checkout main && git pull`.
2. **Crie uma branch** para a sua tarefa, com um nome que diga o que ela faz: `feature/h6-biblioteca`, `fix/erro-no-login`, `docs/contributing`.
3. **Trabalhe em commits pequenos e frequentes.** Pelo menos um commit por semana de código, e de preferência um commit por ideia concluída. Use mensagens no formato `tipo: o que mudou`:
   - `feat:` funcionalidade nova
   - `fix:` correção de erro
   - `test:` testes
   - `docs:` documentação
   - `chore:` configuração e manutenção
4. **Rode os testes** antes de subir (veja abaixo).
5. **Suba a branch e abra um Pull Request** para a `main`: `git push -u origin nome-da-branch`. Descreva o que mudou e cite o card do Jira (por exemplo, `SCRUM-12`).
6. **Peça revisão de pelo menos um colega.** Só faça o merge com o pipeline **verde**.
7. Depois do merge, apague a branch e atualize a sua `main`.

Nunca faça commit direto de código na `main` e nunca use `git push --force` nela. Para desfazer algo que já está na `main`, use `git revert <hash>`, que cria um commit novo desfazendo o anterior.

## Testes e pipeline (CI)

Para rodar todos os testes na sua máquina:

```bash
python manage.py test
```

Para rodar só um app: `python manage.py test diagnostico`.

Todo `push` na `main` e todo Pull Request disparam o pipeline em [`.github/workflows/ci.yml`](./.github/workflows/ci.yml), que faz, nesta ordem:

1. instala as dependências;
2. `python manage.py check`, que confere a configuração do Django;
3. `python manage.py makemigrations --check --dry-run`, que falha se você mudou um model e esqueceu de criar a migração;
4. `python manage.py test`, que roda toda a suíte.

Se algum passo falhar, o Pull Request fica vermelho e não deve ser aceito. Abra o passo que falhou na aba **Actions** do GitHub para ver o erro.

Se você criar ou alterar um model, gere e **commite** a migração:

```bash
python manage.py makemigrations
python manage.py migrate
```

Toda funcionalidade nova deve vir com testes. Cada história tem cenários em BDD no [historias.md](./historias.md), e esses cenários viram os testes.

## Padrões do projeto

- **HTML, CSS e JavaScript ficam em arquivos separados.** Não use `<style>`, `style="..."`, `<script>` com código nem atributos como `onclick` dentro dos templates. O CSS vai em `static/css/` (ou `static/` do app) e o JavaScript em `static/js/`. Para passar valores do servidor ao JavaScript, use atributos `data-*` no HTML. Um teste automatizado (`ArquivosSeparadosTests`) falha se algum template quebrar essa regra.
- **Confirmações antes de ações destrutivas:** coloque `data-confirmar="Mensagem"` no `<form>`; o `static/js/base.js` cuida do resto.
- **Páginas que exigem conta** usam `@login_required` e só mostram dados do próprio usuário.
- **Textos da interface em português do Brasil.**
- **Tipografia e cores** vêm de `static/css/tipografia.css` e das variáveis em `static/css/base.css`. Use as variáveis em vez de escrever cores soltas.

## Variáveis de ambiente e deploy

Localmente você não precisa configurar nada. Em produção, estas variáveis existem no Vercel:

| Variável | Para que serve |
|---|---|
| `SECRET_KEY` | Chave secreta do Django |
| `DATABASE_URL` | Endereço do Postgres (Neon). Sem ela o projeto usa SQLite |
| `BLOB_READ_WRITE_TOKEN` | Permite salvar as fotos da rede social no Vercel Blob. Sem ela as fotos vão para a pasta `media/` |

**Nunca** coloque senhas, tokens ou o arquivo `.env` no Git, e não cole essas informações em Issues, Pull Requests ou conversas públicas. Se algum segredo vazar, troque-o no serviço de origem (Neon, Vercel) e atualize a variável.

## Como reportar um problema

Abra uma [Issue no GitHub](https://github.com/R0DR1G9/projetos2_grupo15/issues) dizendo:

- o que você fez, passo a passo;
- o que esperava que acontecesse;
- o que aconteceu de fato, com um print se ajudar.
