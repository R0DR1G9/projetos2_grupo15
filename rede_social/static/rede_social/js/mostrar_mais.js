(function () {
  document.querySelectorAll("[data-mostrar-mais]").forEach(function (lista) {
    var limite = parseInt(lista.dataset.limite, 10) || 5;
    var itens = Array.prototype.filter.call(lista.children, function (el) {
      return el.tagName !== "BUTTON";
    });
    if (itens.length <= limite) return;

    var escondidos = itens.slice(limite);
    escondidos.forEach(function (el) { el.hidden = true; });

    var botao = document.createElement("button");
    botao.type = "button";
    botao.className = "rs-btn rs-mostrar-mais";
    botao.textContent = "Mostrar mais (" + escondidos.length + ")";
    botao.addEventListener("click", function () {
      escondidos.forEach(function (el) { el.hidden = false; });
      botao.remove();
    });
    lista.appendChild(botao);
  });
})();
