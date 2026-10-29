/* Troca animada entre login e cadastro.
   Funciona em qualquer navegador: ao chegar na tela, os dois painéis deslizam da
   posição em que estavam na tela anterior até a posição atual. Roda no fim
   do body, para começar antes do primeiro desenho (sem "piscar"). */
(function () {
    'use strict';

    var CHAVE_ULTIMA = 'authUltimaTela';
    var CHAVE_TROCA = 'authTrocaEm';
    var atual = document.body.classList.contains('auth-invertido') ? 'cadastro' : 'login';

    function ler(chave) { try { return sessionStorage.getItem(chave); } catch (e) { return null; } }
    function gravar(chave, valor) { try { sessionStorage.setItem(chave, valor); } catch (e) { /* ignora */ } }
    function apagar(chave) { try { sessionStorage.removeItem(chave); } catch (e) { /* ignora */ } }

    function tipoDeNavegacao() {
        try {
            var n = performance.getEntriesByType('navigation')[0];
            return n ? n.type : 'navigate';
        } catch (e) { return 'navigate'; }
    }

    // Clicou no link "Entrar" / "Cadastrar": avisa a próxima tela que ela deve animar.
    document.addEventListener('click', function (e) {
        var link = e.target && e.target.closest ? e.target.closest('.auth-rodape a') : null;
        if (!link || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        gravar(CHAVE_TROCA, String(Date.now()));
    });

    function animarChegada() {
        if (!document.body.animate) return;
        var marca = document.querySelector('.auth-marca');
        var form = document.querySelector('.auth-form');
        var caixa = document.querySelector('.auth-caixa');
        if (!marca || !form || !caixa) return;

        var m = marca.getBoundingClientRect();
        var f = form.getBoundingClientRect();
        var ladoALado = Math.abs(m.top - f.top) < 8;
        if (!ladoALado) return;   // celular: painéis empilhados, quem anima é o auth-mobile.css

        var reduzir = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // Quem pede menos movimento só vê o formulário aparecendo suavemente.
        caixa.animate(
            [{ opacity: 0, transform: reduzir ? 'none' : 'translateY(10px)' }, { opacity: 1, transform: 'none' }],
            { duration: reduzir ? 250 : 450, delay: reduzir ? 0 : 200, easing: 'ease-out', fill: 'backwards' }
        );
        if (reduzir) return;

        // Na tela anterior os painéis estavam espelhados: o bordô do outro lado.
        var invertido = atual === 'cadastro';
        var dxMarca = invertido ? -f.width : f.width;
        var dxForm = invertido ? m.width : -m.width;
        var opcoes = { duration: 650, easing: 'cubic-bezier(0.77, 0, 0.18, 1)' };

        marca.style.zIndex = '2';   // o bordô passa por cima do formulário
        var animMarca = marca.animate(
            [{ transform: 'translateX(' + dxMarca + 'px)' }, { transform: 'translateX(0)' }], opcoes);
        form.animate(
            [{ transform: 'translateX(' + dxForm + 'px)' }, { transform: 'translateX(0)' }], opcoes);
        animMarca.onfinish = animMarca.oncancel = function () { marca.style.zIndex = ''; };
    }

    function aoChegar(restauradaDoHistorico) {
        var anterior = ler(CHAVE_ULTIMA);
        var clicouEm = parseInt(ler(CHAVE_TROCA), 10);
        apagar(CHAVE_TROCA);
        gravar(CHAVE_ULTIMA, atual);

        var porLink = !!clicouEm && Date.now() - clicouEm < 15000;
        var porHistorico = restauradaDoHistorico || tipoDeNavegacao() === 'back_forward';
        var veioDaOutra = anterior ? anterior !== atual : porLink;

        if ((porLink || porHistorico) && veioDaOutra) animarChegada();
    }

    aoChegar(false);
    // Voltar/avançar pode restaurar a página já pronta (sem recarregar): anima de novo.
    window.addEventListener('pageshow', function (e) { if (e.persisted) aoChegar(true); });
})();
