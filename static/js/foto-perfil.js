(function () {
    const campo = document.getElementById('id_foto');
    if (!campo) return;

    campo.addEventListener('change', () => {
        if (campo.files.length) campo.form.submit();
    });
})();