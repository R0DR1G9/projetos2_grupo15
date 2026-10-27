(function () {
  var input = document.getElementById("id_imagem");
  var caixa = document.getElementById("rs-preview");
  var img = document.getElementById("rs-preview-img");
  var erro = document.getElementById("rs-erro-imagem");
  var LIMITE = 4 * 1024 * 1024; // mantenha igual a TAMANHO_MAXIMO_IMAGEM em models.py
  if (!input) return;

  function limpar() {
    if (img.src) URL.revokeObjectURL(img.src);
    img.removeAttribute("src");
    input.value = "";
    caixa.hidden = true;
  }

  input.addEventListener("change", function () {
    var arquivo = input.files[0];
    erro.hidden = true;
    if (!arquivo) { limpar(); return; }
    if (arquivo.size > LIMITE) {
      limpar();
      erro.textContent = "A imagem é muito grande (máximo de 4 MB).";
      erro.hidden = false;
      return;
    }
    if (img.src) URL.revokeObjectURL(img.src);
    img.src = URL.createObjectURL(arquivo);
    caixa.hidden = false;
  });

  document.getElementById("rs-preview-remover").addEventListener("click", limpar);
})();
