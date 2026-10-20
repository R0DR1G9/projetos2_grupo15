// Lista de diagnósticos: exclusão via botão com data-excluir="<id>".
document.querySelectorAll('[data-excluir]').forEach(botao => {
    botao.addEventListener('click', () => {
        if (!confirm('Tem certeza de que deseja excluir este diagnóstico?')) return;
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch(`/deletar/${botao.dataset.excluir}/`, { method: 'POST', headers: { 'X-CSRFToken': csrf } })
            .then(r => r.json())
            .then(d => (d.success ? window.location.reload() : alert('Erro ao excluir o diagnóstico.')))
            .catch(() => alert('Ocorreu um erro ao excluir.'));
    });
});
