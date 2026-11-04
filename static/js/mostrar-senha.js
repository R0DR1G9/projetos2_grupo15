(function () {
    var OLHO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
    var OLHO_CORTADO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';

    document.querySelectorAll('.auth-caixa input[type="password"]').forEach(function (input) {
        var envoltorio = document.createElement('div');
        envoltorio.className = 'campo-senha';
        input.parentNode.insertBefore(envoltorio, input);
        envoltorio.appendChild(input);

        var botao = document.createElement('button');
        botao.type = 'button';
        botao.className = 'campo-senha-botao';
        botao.setAttribute('aria-label', 'Mostrar senha');
        botao.innerHTML = OLHO;

        botao.addEventListener('click', function () {
            var mostrar = input.type === 'password';
            input.type = mostrar ? 'text' : 'password';
            botao.innerHTML = mostrar ? OLHO_CORTADO : OLHO;
            botao.setAttribute('aria-label', mostrar ? 'Ocultar senha' : 'Mostrar senha');
        });

        envoltorio.appendChild(botao);
    });
})();