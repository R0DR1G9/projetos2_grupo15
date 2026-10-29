// Formulário do diagnóstico em etapas (perfil + 3 pilares).
// Mostra só as perguntas que valem para o tipo de operação escolhido.
(function () {
    const form = document.getElementById('formDiagnostico');
    if (!form) return;

    const etapas = Array.from(form.querySelectorAll('.etapa'));
    const nomes = Array.from(document.querySelectorAll('#etapaNomes .etapa-nome'));
    const barra = document.getElementById('barra');
    const barraRespondidas = document.getElementById('barraRespondidas');
    const textoRespondidas = document.getElementById('textoRespondidas');
    const pctRespondidas = document.getElementById('pctRespondidas');
    const btnVoltar = document.getElementById('btnVoltar');
    const btnProximo = document.getElementById('btnProximo');
    const btnFinalizar = document.getElementById('btnFinalizar');
    const tipo = form.querySelector('[name="tipo_operacao"]');
    let atual = 0;

    document.querySelector('.conteudo').classList.add('js-etapas');

    function aplicarTipo() {
        const escolhido = tipo.value;
        form.querySelectorAll('.pergunta').forEach(p => {
            const vale = !escolhido || p.dataset.aplica.split(' ').includes(escolhido);
            p.classList.toggle('oculta', !vale);
        });
        atualizarProgresso();
        form.querySelectorAll('.subtema').forEach(s => {
            s.classList.toggle('oculto', !s.querySelector('.pergunta:not(.oculta)'));
        });
    }

    function atualizarProgresso() {
        const validas = Array.from(form.querySelectorAll('.pergunta:not(.oculta)'));
        const respondidas = validas.filter(p => p.querySelector('input:checked')).length;
        const total = validas.length;
        const pct = total ? Math.round(respondidas / total * 100) : 0;
        textoRespondidas.textContent = 'Respondeu ' + respondidas + ' de ' + total + (total === 1 ? ' pergunta' : ' perguntas');
        pctRespondidas.textContent = pct + '%';
        barraRespondidas.style.width = pct + '%';
        barraRespondidas.setAttribute('aria-valuenow', pct);
    }

    function mostrar(i) {
        atual = i;
        etapas.forEach((e, n) => e.classList.toggle('ativa', n === i));
        nomes.forEach((e, n) => {
            e.classList.toggle('atual', n === i);
            e.classList.toggle('feita', n < i);
        });
        barra.style.width = ((i + 1) / etapas.length * 100) + '%';
        btnVoltar.classList.toggle('invisivel', i === 0);
        btnProximo.hidden = i === etapas.length - 1;
        btnFinalizar.hidden = i !== etapas.length - 1;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function validar(i) {
        const etapa = etapas[i];
        if (i === 0) {
            const obrigatorios = etapa.querySelectorAll('[name="nome_empresa"], [name="porte"], [name="tipo_operacao"]');
            for (const campo of obrigatorios) {
                if (!campo.value.trim()) { campo.focus(); campo.classList.add('is-invalid'); return false; }
                campo.classList.remove('is-invalid');
            }
            return true;
        }
        let primeiro = null;
        etapa.querySelectorAll('.pergunta:not(.oculta)').forEach(p => {
            const respondida = p.querySelector('input:checked');
            p.classList.toggle('erro', !respondida);
            if (!respondida && !primeiro) primeiro = p;
        });
        if (primeiro) { primeiro.scrollIntoView({ behavior: 'smooth', block: 'center' }); return false; }
        return true;
    }

    form.querySelectorAll('input, select').forEach(c => c.addEventListener('input', () => c.classList.remove('is-invalid')));
    form.querySelectorAll('.pergunta input').forEach(r => r.addEventListener('change', () => { r.closest('.pergunta').classList.remove('erro'); atualizarProgresso(); }));
    tipo.addEventListener('change', aplicarTipo);
    btnProximo.addEventListener('click', () => { if (validar(atual)) mostrar(atual + 1); });
    btnVoltar.addEventListener('click', () => mostrar(atual - 1));
    form.addEventListener('submit', e => {
        for (let i = 0; i < etapas.length; i++) {
            if (!validar(i)) { e.preventDefault(); mostrar(i); validar(i); return; }
        }
    });

    aplicarTipo();
    if (form.dataset.temErro) {
        form.querySelectorAll('.pergunta:not(.oculta)').forEach(p => p.classList.toggle('erro', !p.querySelector('input:checked')));
        const comProblema = etapas.findIndex(e => e.querySelector('.pergunta.erro') || e.querySelector('.text-danger'));
        mostrar(Math.max(0, comProblema));
    } else {
        mostrar(0);
    }
})();
