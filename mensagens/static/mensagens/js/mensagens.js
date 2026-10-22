/* Direct: envio sem recarregar, novas mensagens automáticas (consulta a cada 4 s),
   Enter envia (Shift+Enter quebra linha) e "desfazer envio".
   Sem JavaScript, o formulário continua funcionando (recarrega a página). */
(function () {
  'use strict';

  var lista = document.getElementById('ms-mensagens');
  var form = document.getElementById('ms-form');
  if (!lista || !form) return;

  document.documentElement.classList.add('ms-js');

  var campo = form.querySelector('textarea');
  var botao = form.querySelector('button[type=submit]');
  var status = document.getElementById('ms-status');
  var erro = document.getElementById('ms-erro');
  var token = form.querySelector('input[name=csrfmiddlewaretoken]').value;
  var urlNovas = lista.getAttribute('data-novas-url');
  var ultima = parseInt(lista.getAttribute('data-ultima'), 10) || 0;
  var enviando = false;
  var CABECALHO = { 'X-Requested-With': 'XMLHttpRequest' };

  function rolarParaOFim() { lista.scrollTop = lista.scrollHeight; }
  function pertoDoFim() { return lista.scrollHeight - lista.scrollTop - lista.clientHeight < 90; }

  function mostrarErro(texto) {
    erro.textContent = texto;
    erro.hidden = !texto;
  }

  function atualizarCampo() {
    campo.style.height = 'auto';
    campo.style.height = Math.min(campo.scrollHeight, 120) + 'px';
    botao.disabled = enviando || campo.value.trim() === '';
  }

  // Insere o HTML (já escapado pelo servidor) sem duplicar mensagens.
  function inserir(html) {
    if (!html || !html.trim()) return false;
    var modelo = document.createElement('template');
    modelo.innerHTML = html.trim();
    var inseriu = false;
    Array.prototype.slice.call(modelo.content.children).forEach(function (no) {
      var id = no.getAttribute('data-msg-id');
      if (id && lista.querySelector('[data-msg-id="' + id + '"]')) return;
      var inicio = lista.querySelector('.ms-inicio');
      if (inicio) inicio.remove();
      lista.insertBefore(no, document.getElementById('ms-fim'));
      inseriu = true;
    });
    return inseriu;
  }

  function enviar() {
    if (enviando || campo.value.trim() === '') return;
    enviando = true;
    atualizarCampo();
    mostrarErro('');

    fetch(form.action, { method: 'POST', body: new FormData(form), headers: CABECALHO, credentials: 'same-origin' })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error((res.j && res.j.erro) || 'Não foi possível enviar.');
        inserir(res.j.html);
        ultima = Math.max(ultima, res.j.id);
        campo.value = '';
        status.textContent = res.j.status || '';
        rolarParaOFim();
      })
      .catch(function (e) { mostrarErro(e.message || 'Não foi possível enviar.'); })
      .then(function () { enviando = false; atualizarCampo(); campo.focus(); });
  }

  form.addEventListener('submit', function (e) { e.preventDefault(); enviar(); });
  campo.addEventListener('input', atualizarCampo);
  campo.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); enviar(); }
  });

  // Novas mensagens e "Visto"
  function consultar() {
    if (document.hidden || enviando) return;
    fetch(urlNovas + '?depois=' + ultima, { headers: CABECALHO, credentials: 'same-origin' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        if (!j) return;
        var noFim = pertoDoFim();
        if (inserir(j.html) && noFim) rolarParaOFim();
        if (j.ultima > ultima) ultima = j.ultima;
        status.textContent = j.status || '';
      })
      .catch(function () { /* sem rede: tenta de novo no próximo ciclo */ });
  }
  setInterval(consultar, 4000);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) consultar(); });

  // Desfazer envio
  lista.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('.ms-desfazer') : null;
    if (!b || !confirm('Desfazer o envio desta mensagem?')) return;
    fetch(b.getAttribute('data-url'), {
      method: 'POST',
      headers: { 'X-CSRFToken': token, 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'same-origin'
    })
      .then(function (r) {
        if (!r.ok) throw new Error();
        var linha = b.closest('.ms-linha');
        if (linha) linha.remove();
      })
      .catch(function () { mostrarErro('Não foi possível desfazer o envio.'); });
  });

  atualizarCampo();
  rolarParaOFim();
  if (window.matchMedia && window.matchMedia('(min-width: 861px)').matches) campo.focus();
})();
