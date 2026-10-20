// Comportamentos comuns a todas as páginas (sem JavaScript dentro do HTML).
document.addEventListener('DOMContentLoaded', () => {
    // Anel de percentual: <div class="anel" data-pct="66.7">
    document.querySelectorAll('[data-pct]').forEach(el => {
        el.style.setProperty('--pct', el.dataset.pct);
    });

    // Barras de progresso: <div data-largura="42.5">
    document.querySelectorAll('[data-largura]').forEach(el => {
        el.style.width = el.dataset.largura + '%';
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
});
