/* ══════════════════════════════════════════════════════════════════════
 *  Calendários do sistema (Flatpickr)
 *
 *  Todo <input type="date"> vira um calendário em português. O campo
 *  original continua enviando AAAA-MM-DD para o Django; o usuário vê e
 *  digita DD/MM/AAAA. Use data-sem-calendario para manter o nativo.
 *
 *  Para alterar a data por JavaScript: Calendarios.definir(input, 'AAAA-MM-DD').
 *  Precisa ser carregado depois do flatpickr e do l10n/pt.
 * ══════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  if (typeof flatpickr === "undefined") {
    console.warn("Flatpickr não carregado: usando o calendário do navegador.");
    window.Calendarios = {
      aplicar: function () {},
      definir: function (el, valor) { el.value = valor || ""; },
    };
    return;
  }

  function botao(texto, acao) {
    var b = document.createElement("button");
    b.type = "button";
    b.textContent = texto;
    b.addEventListener("click", acao);
    return b;
  }

  function aplicar(el) {
    if (el._flatpickr || el.hasAttribute("data-sem-calendario")) return;

    var estilo = el.getAttribute("style");
    var instancia = flatpickr(el, {
      locale: "pt",
      dateFormat: "Y-m-d",
      altInput: true,
      altFormat: "d/m/Y",
      altInputClass: (el.className || "form-control-custom") + " campo-data",
      allowInput: true,
      disableMobile: true,
      monthSelectorType: "static",
      // Dentro de modais o calendário fica junto do campo, senão o
      // bloqueio de foco do Bootstrap impede a interação.
      static: !!el.closest(".modal"),
      onReady: function (_datas, _texto, fp) {
        var rodape = document.createElement("div");
        rodape.className = "fp-rodape";
        rodape.appendChild(botao("Limpar", function () { fp.clear(); fp.close(); }));
        rodape.appendChild(botao("Hoje", function () { fp.setDate(new Date(), true); fp.close(); }));
        fp.calendarContainer.appendChild(rodape);
      },
    });

    var visivel = instancia.altInput;
    if (estilo) visivel.setAttribute("style", estilo);
    visivel.placeholder = el.getAttribute("placeholder") || "dd/mm/aaaa";
    visivel.setAttribute("autocomplete", "off");
  }

  function aplicarEm(raiz) {
    if (raiz.matches && raiz.matches('input[type="date"]')) aplicar(raiz);
    if (raiz.querySelectorAll) raiz.querySelectorAll('input[type="date"]').forEach(aplicar);
  }

  window.Calendarios = {
    aplicar: aplicar,
    /** Altera a data de um campo (com ou sem calendário) e dispara "change". */
    definir: function (el, valor) {
      if (el._flatpickr) el._flatpickr.setDate(valor || null, true);
      else {
        el.value = valor || "";
        el.dispatchEvent(new Event("change", { bubbles: true }));
      }
    },
  };

  document.addEventListener("DOMContentLoaded", function () {
    aplicarEm(document);
    new MutationObserver(function (mutacoes) {
      mutacoes.forEach(function (m) {
        m.addedNodes.forEach(function (no) {
          if (no.nodeType === 1) aplicarEm(no);
        });
      });
    }).observe(document.body, { childList: true, subtree: true });
  });
})();
