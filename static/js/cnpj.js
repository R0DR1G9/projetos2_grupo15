(function () {
    const campo = document.getElementById('id_cnpj');
    if (!campo) return;

    function formatar(valor) {
        const n = valor.replace(/\D/g, '').slice(0, 14);
        return n
            .replace(/^(\d{2})(\d)/, '$1.$2')
            .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
            .replace(/\.(\d{3})(\d)/, '.$1/$2')
            .replace(/(\d{4})(\d)/, '$1-$2');
    }

    campo.addEventListener('input', () => { campo.value = formatar(campo.value); });
    campo.value = formatar(campo.value);
})();
