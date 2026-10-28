/* Menu lateral recolhível: botão #alternarMenu alterna entre o menu normal e o
   menu pequeno (só ícones). A escolha fica salva no navegador.
   No layout atual (grid) o CSS cuida de tudo, inclusive da animação; o script só
   alterna a classe, atualiza botão/dicas e liga as transições depois do 1º desenho.
   Para outros layouts (menu fixo com margem), ele ainda mede e ajusta o conteúdo. */
(function () {
  'use strict';

  var CHAVE = 'menuRecolhido';
  var html = document.documentElement;
  var lateral = document.getElementById('menuLateral');
  var botao = document.getElementById('alternarMenu');
  if (!lateral || !botao) return;

  var app = document.querySelector('.app');
  var corpo = document.querySelector('.conteudo');
  var desktop = window.matchMedia('(min-width: 992px)');
  var normal = null;   // comportamento do layout com o menu expandido
  var ajustados = [];  // elementos em que este script aplicou estilo

  function recolhido() { return html.classList.contains('menu-recolhido'); }

  function px(valor) { return parseFloat(valor) || 0; }

  // Largura do menu recolhido. Vem do CSS (--menu-recolhido): medir o elemento durante
  // a transição devolveria a largura "do meio do caminho".
  function larguraRecolhida() {
    var v = parseFloat(getComputedStyle(html).getPropertyValue('--menu-recolhido'));
    return v || lateral.getBoundingClientRect().width;
  }

  function medir() {
    var estava = recolhido();
    html.classList.add('menu-medindo');      // sem transições enquanto mede
    html.classList.remove('menu-recolhido');

    var largura = lateral.getBoundingClientRect().width;
    var posicao = getComputedStyle(lateral).position;
    var info = { modo: 'livre' };   // flex/sticky: o conteúdo acompanha sozinho

    if (app && getComputedStyle(app).display === 'grid') {
      info.modo = 'grid';           // a coluna é controlada pelo CSS (e animada por ele)
    } else if (posicao === 'fixed' || posicao === 'absolute') {
      var candidatos = [
        [corpo, 'marginLeft', 'margin-left'],
        [corpo, 'paddingLeft', 'padding-left'],
        [app, 'paddingLeft', 'padding-left'],
        [app, 'marginLeft', 'margin-left']
      ];
      for (var i = 0; i < candidatos.length; i++) {
        var el = candidatos[i][0];
        if (!el) continue;
        var valor = px(getComputedStyle(el)[candidatos[i][1]]);
        if (valor >= largura - 2 && valor <= largura + 80) {
          info = { modo: 'deslocado', alvo: el, prop: candidatos[i][2], extra: valor - largura };
          break;
        }
      }
    }

    if (estava) html.classList.add('menu-recolhido');
    html.classList.remove('menu-medindo');
    normal = info;
  }

  function limpar() {
    ajustados.forEach(function (el) {
      el.style.removeProperty('grid-template-columns');
      el.style.removeProperty('margin-left');
      el.style.removeProperty('padding-left');
    });
    ajustados = [];
  }

  function atualizarBotao(r) {
    var texto = r ? 'Expandir menu' : 'Recolher menu';
    botao.setAttribute('aria-pressed', r ? 'true' : 'false');
    botao.setAttribute('aria-label', texto);
    botao.setAttribute('title', texto);
    var icone = botao.querySelector('i');
    if (icone) icone.className = r ? 'ci ci-chevron-double-right' : 'ci ci-chevron-double-left';
  }

  function atualizarDicas(r) {
    var itens = lateral.querySelectorAll('a.menu-item');
    for (var i = 0; i < itens.length; i++) {
      var item = itens[i];
      if (r) {
        var rotulo = item.querySelector('span');
        if (rotulo && !item.hasAttribute('title')) {
          item.setAttribute('title', rotulo.textContent.trim());
          item.setAttribute('aria-label', rotulo.textContent.trim());
          item.setAttribute('data-rs-dica', '1');
        }
      } else if (item.hasAttribute('data-rs-dica')) {
        item.removeAttribute('title');
        item.removeAttribute('aria-label');
        item.removeAttribute('data-rs-dica');
      }
    }
  }

  function aplicar() {
    limpar();
    var r = recolhido();
    atualizarBotao(r);
    atualizarDicas(r);
    if (!r || !desktop.matches) return;

    if (!normal) medir();
    // modo 'grid': nada a fazer aqui, o CSS (html.menu-recolhido .app) define a coluna.
    if (normal.modo === 'deslocado') {
      var nova = larguraRecolhida();
      normal.alvo.style.setProperty(normal.prop, (nova + normal.extra) + 'px', 'important');
      ajustados.push(normal.alvo);
    }
  }

  botao.addEventListener('click', function () {
    var r = !recolhido();
    html.classList.toggle('menu-recolhido', r);
    try { localStorage.setItem(CHAVE, r ? '1' : '0'); } catch (e) { /* ignora */ }
    aplicar();
  });

  function aoMudarTela() { normal = null; if (desktop.matches) medir(); aplicar(); }
  if (desktop.addEventListener) desktop.addEventListener('change', aoMudarTela);
  else if (desktop.addListener) desktop.addListener(aoMudarTela);

  var salvo = false;
  try { salvo = localStorage.getItem(CHAVE) === '1'; } catch (e) { /* ignora */ }
  html.classList.toggle('menu-recolhido', salvo);
  if (desktop.matches) medir();   // detecta o tipo de layout antes de qualquer clique
  aplicar();

  // Liga as transições só depois do primeiro desenho: a página abre direto no estado
  // salvo (aberto ou recolhido), sem animar.
  requestAnimationFrame(function () {
    requestAnimationFrame(function () { html.classList.add('menu-animavel'); });
  });
})();
