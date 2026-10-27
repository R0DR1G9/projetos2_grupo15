// Comportamentos comuns a todas as páginas (sem JavaScript dentro do HTML).
document.addEventListener('DOMContentLoaded', () => {
    // Anel de percentual: <div class="anel" data-pct="66.7">
    // Começa em 0 e preenche até o valor (a animação está no animacoes.css).
    document.querySelectorAll('[data-pct]').forEach(el => {
        void el.offsetWidth; // fixa o estado inicial (0) antes de definir o valor final
        requestAnimationFrame(() => el.style.setProperty('--pct', el.dataset.pct));
    });

    // Barras de progresso: <div data-largura="42.5"> (cresce de 0% até o valor)
    document.querySelectorAll('[data-largura]').forEach(el => {
        const alvo = el.dataset.largura + '%';
        el.style.width = '0%';
        void el.offsetWidth;
        requestAnimationFrame(() => { el.style.width = alvo; });
    });

    // Select que envia o formulário ao mudar: <select data-auto-enviar>
    document.querySelectorAll('select[data-auto-enviar]').forEach(sel => {
        sel.addEventListener('change', () => sel.form.submit());
    });

    // Formulário que pede confirmação: <form data-confirmar="Tem certeza?">
    document.querySelectorAll('form[data-confirmar]').forEach(form => {
        form.addEventListener('submit', e => {
            if (!confirm(form.dataset.confirmar)) e.preventDefault();
        });
    });

    document.querySelectorAll('a[data-focar]').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const alvo = document.getElementById(link.dataset.focar);
            if (alvo) alvo.focus();
        });
    });
});
