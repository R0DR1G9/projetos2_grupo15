(function () {
    const colunas = Array.from(document.querySelectorAll('[data-coluna]'));
    if (!colunas.length) return;

    const INTERATIVOS = 'select, button, a, input, textarea, label, form[data-confirmar]';
    let arraste = null;

    function colunaSob(x, y) {
        const el = document.elementFromPoint(x, y);
        return el ? el.closest('[data-coluna]') : null;
    }

    function marcarAlvo(coluna) {
        colunas.forEach(c => c.classList.toggle('coluna-alvo', c === coluna));
    }

    function mover(e) {
        if (!arraste || e.pointerId !== arraste.id) return;
        const dx = e.clientX - arraste.x0;
        const dy = e.clientY - arraste.y0;
        if (!arraste.ativo) {
            if (Math.hypot(dx, dy) < 6) return;
            iniciar();
        }
        e.preventDefault();
        arraste.fantasma.style.left = (e.clientX - arraste.offX) + 'px';
        arraste.fantasma.style.top = (e.clientY - arraste.offY) + 'px';
        marcarAlvo(colunaSob(e.clientX, e.clientY));
        const borda = 70;
        if (e.clientY < borda) window.scrollBy(0, -14);
        else if (window.innerHeight - e.clientY < borda) window.scrollBy(0, 14);
    }

    function iniciar() {
        const caixa = arraste.cartao.getBoundingClientRect();
        const fantasma = arraste.cartao.cloneNode(true);
        fantasma.classList.add('cartao-fantasma');
        fantasma.style.width = caixa.width + 'px';
        document.body.appendChild(fantasma);
        arraste.fantasma = fantasma;
        arraste.offX = arraste.x0 - caixa.left;
        arraste.offY = arraste.y0 - caixa.top;
        arraste.cartao.classList.add('arrastando-origem');
        document.body.classList.add('arrastando');
        arraste.ativo = true;
    }

    function terminar(e) {
        if (!arraste || e.pointerId !== arraste.id) return;
        const { cartao, ativo, fantasma } = arraste;
        const destino = ativo && e.type === 'pointerup' ? colunaSob(e.clientX, e.clientY) : null;
        if (fantasma) fantasma.remove();
        cartao.classList.remove('arrastando-origem');
        document.body.classList.remove('arrastando');
        marcarAlvo(null);
        document.removeEventListener('pointermove', mover);
        document.removeEventListener('pointerup', terminar);
        document.removeEventListener('pointercancel', terminar);
        arraste = null;
        if (!destino) return;
        const select = cartao.querySelector('select[name="status"]');
        if (!select || select.value === destino.dataset.coluna) return;
        select.value = destino.dataset.coluna;
        select.form.submit();
    }

    function comecar(e) {
        if (arraste || (e.pointerType === 'mouse' && e.button !== 0)) return;
        const cartao = e.target.closest('[data-atividade]');
        if (!cartao) return;
        const naAlca = e.target.closest('.alca-arrastar');
        if (!naAlca && e.target.closest(INTERATIVOS)) return;
        if (!naAlca && e.pointerType !== 'mouse') return;
        arraste = { id: e.pointerId, cartao, x0: e.clientX, y0: e.clientY, ativo: false };
        document.addEventListener('pointermove', mover, { passive: false });
        document.addEventListener('pointerup', terminar);
        document.addEventListener('pointercancel', terminar);
    }

    document.addEventListener('pointerdown', comecar);
    document.addEventListener('dragstart', e => { if (e.target.closest('[data-atividade]')) e.preventDefault(); });
})();
