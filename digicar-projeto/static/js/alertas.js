/* ══════════════════════════════════════════════════════════════════════
 *  Avisos, confirmações e validação com SweetAlert2
 *
 *  - Mensagens do Django (messages): toast no canto superior direito, com o
 *    ícone do nível mais grave. Lidas de <script id="mensagens-django">.
 *  - Confirmação: qualquer <form data-confirm="Texto"> pede confirmação antes
 *    de enviar. Opcionais: data-confirm-titulo, data-confirm-botao e
 *    data-confirm-perigo (botão vermelho, para exclusões).
 *  - Validação: substitui os balões nativos do navegador por um modal que
 *    lista os campos com problema. Use data-validacao-nativa para desligar.
 *
 *  Precisa ser carregado depois do sweetalert2.all.min.js.
 * ══════════════════════════════════════════════════════════════════════ */

// Globais usados por páginas que chamam o SweetAlert diretamente.
var SwalCustom = null;
var Toast = null;

(function () {
  "use strict";

  if (typeof Swal === "undefined") {
    console.warn("SweetAlert2 não carregado: avisos usarão o navegador.");
    return;
  }

  SwalCustom = Swal.mixin({
    customClass: {
      confirmButton: "btn-primary-custom",
      cancelButton: "btn-outline-custom",
      actions: "swal-acoes",
    },
    buttonsStyling: false,
    reverseButtons: true,
  });

  Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 4000,
    timerProgressBar: true,
    didOpen: function (toast) {
      toast.onmouseenter = Swal.stopTimer;
      toast.onmouseleave = Swal.resumeTimer;
    },
  });

  // ── Utilitários ─────────────────────────────────────────────────────
  function lista(itens) {
    // Monta o HTML com textContent para não interpretar texto do usuário.
    if (itens.length === 1) {
      var p = document.createElement("div");
      p.textContent = itens[0];
      return p;
    }
    var ul = document.createElement("ul");
    ul.className = "swal-lista";
    itens.forEach(function (texto) {
      var li = document.createElement("li");
      li.textContent = texto;
      ul.appendChild(li);
    });
    return ul;
  }

  function lerCookie(nome) {
    var partes = ("; " + document.cookie).split("; " + nome + "=");
    return partes.length === 2 ? decodeURIComponent(partes.pop().split(";").shift()) : "";
  }

  // ── API pública ─────────────────────────────────────────────────────
  window.Alertas = {
    sucesso: function (texto) {
      return Toast.fire({ icon: "success", title: texto });
    },
    info: function (texto) {
      return Toast.fire({ icon: "info", title: texto });
    },
    erro: function (texto) {
      return Toast.fire({ icon: "error", title: texto, timer: 7000 });
    },
    aviso: function (texto) {
      return Toast.fire({ icon: "warning", title: texto, timer: 7000 });
    },
    /** Resolve com true se o usuário confirmar. */
    confirmar: function (opcoes) {
      return SwalCustom.fire({
        icon: opcoes.perigo ? "warning" : "question",
        title: opcoes.titulo || "Confirmação",
        html: lista([opcoes.texto || "Deseja continuar?"]),
        showCancelButton: true,
        confirmButtonText: opcoes.botao || (opcoes.perigo ? "Sim, excluir" : "Sim, continuar"),
        cancelButtonText: "Cancelar",
        focusCancel: !!opcoes.perigo,
        customClass: {
          confirmButton: opcoes.perigo ? "btn-primary-custom swal-perigo" : "btn-primary-custom",
          cancelButton: "btn-outline-custom",
          actions: "swal-acoes",
        },
      }).then(function (resultado) {
        return resultado.isConfirmed;
      });
    },
    /** Envia um POST (com CSRF) para a URL, como um formulário. */
    postar: function (url) {
      var form = document.createElement("form");
      form.method = "post";
      form.action = url;
      var token = document.createElement("input");
      token.type = "hidden";
      token.name = "csrfmiddlewaretoken";
      token.value = lerCookie("csrftoken");
      form.appendChild(token);
      document.body.appendChild(form);
      form.submit();
    },
  };

  // Compatibilidade: código antigo que chama confirmDelete(url, mensagem).
  window.confirmDelete = function (url, mensagem) {
    Alertas.confirmar({ texto: mensagem || "Deseja realmente excluir este registro?", perigo: true }).then(
      function (ok) {
        if (ok) Alertas.postar(url);
      }
    );
  };

  // alert() nativo passa a usar o SweetAlert.
  window.alert = function (mensagem) {
    SwalCustom.fire({ icon: "info", html: lista([String(mensagem)]) });
  };

  // ── Mensagens do Django ─────────────────────────────────────────────
  function mostrarMensagensDjango() {
    var el = document.getElementById("mensagens-django");
    if (!el) return;
    var mensagens;
    try {
      mensagens = JSON.parse(el.textContent);
    } catch (e) {
      return;
    }
    if (!mensagens.length) return;

    // O SweetAlert mostra um toast por vez: todas as mensagens vão no mesmo
    // toast, com o ícone do nível mais grave.
    function nivel(m) {
      if (/error|danger/.test(m.nivel)) return "error";
      if (/warning/.test(m.nivel)) return "warning";
      if (/success/.test(m.nivel)) return "success";
      return "info";
    }
    var gravidade = ["error", "warning", "success", "info"];
    var icone = gravidade.find(function (g) {
      return mensagens.some(function (m) { return nivel(m) === g; });
    });
    var problema = icone === "error" || icone === "warning";

    Toast.fire({
      icon: icone,
      html: lista(mensagens.map(function (m) { return m.texto; })),
      timer: problema ? 7000 : 4000,
    });
  }

  // ── Validação ───────────────────────────────────────────────────────
  function nomeDoCampo(campo) {
    var rotulo = campo.id && document.querySelector('label[for="' + campo.id + '"]');
    if (!rotulo) {
      var grupo = campo.closest(".mb-3, .login-form-group, [class*='col-'], .form-group");
      rotulo = grupo && grupo.querySelector("label");
    }
    var texto = rotulo ? rotulo.textContent : campo.placeholder || campo.name || "Campo";
    return texto.replace(/\*/g, "").replace(/\s+/g, " ").trim();
  }

  function camposInvalidos(form) {
    return Array.prototype.filter.call(form.elements, function (campo) {
      return campo.willValidate && !campo.checkValidity();
    });
  }

  function marcarInvalidos(form, campos) {
    form.querySelectorAll(".is-invalid").forEach(function (c) {
      c.classList.remove("is-invalid");
    });
    campos.forEach(function (campo) {
      // Máscaras de moeda escondem o input real; marca o visível ao lado.
      var alvo = campo.type === "hidden" && campo.previousElementSibling ? campo.previousElementSibling : campo;
      alvo.classList.add("is-invalid");
    });
  }

  function desligarValidacaoNativa(raiz) {
    (raiz.tagName === "FORM" ? [raiz] : raiz.querySelectorAll ? raiz.querySelectorAll("form") : []).forEach(
      function (form) {
        if (!form.hasAttribute("data-validacao-nativa")) form.noValidate = true;
      }
    );
  }

  document.addEventListener("input", function (e) {
    if (e.target.classList && e.target.classList.contains("is-invalid") && e.target.checkValidity()) {
      e.target.classList.remove("is-invalid");
    }
  });

  // ── Envio: validação e depois confirmação ───────────────────────────
  // Fase de captura: roda antes dos listeners da própria página.
  document.addEventListener(
    "submit",
    function (e) {
      var form = e.target;
      if (!(form instanceof HTMLFormElement)) return;

      if (form.dataset.confirmado === "1") {
        delete form.dataset.confirmado;
        return; // já confirmado: segue o envio normal
      }

      if (!form.hasAttribute("data-validacao-nativa")) {
        var invalidos = camposInvalidos(form);
        if (invalidos.length) {
          e.preventDefault();
          e.stopPropagation();
          marcarInvalidos(form, invalidos);
          SwalCustom.fire({
            icon: "warning",
            title: "Confira os campos",
            html: lista(
              invalidos.map(function (campo) {
                return nomeDoCampo(campo) + ": " + campo.validationMessage;
              })
            ),
          }).then(function () {
            var primeiro = invalidos[0];
            (primeiro.type === "hidden" && primeiro.previousElementSibling ? primeiro.previousElementSibling : primeiro).focus();
          });
          return;
        }
      }

      var texto = (e.submitter && e.submitter.dataset.confirm) || form.dataset.confirm;
      if (!texto) return;

      e.preventDefault();
      e.stopPropagation();
      var submitter = e.submitter;
      var origem = submitter && submitter.dataset.confirm ? submitter : form;
      Alertas.confirmar({
        texto: texto,
        titulo: origem.dataset.confirmTitulo,
        botao: origem.dataset.confirmBotao,
        perigo: origem.hasAttribute("data-confirm-perigo"),
      }).then(function (ok) {
        if (!ok) return;
        form.dataset.confirmado = "1";
        if (form.requestSubmit) form.requestSubmit(submitter || undefined);
        else form.submit();
      });
    },
    true
  );

  document.addEventListener("DOMContentLoaded", function () {
    desligarValidacaoNativa(document);
    new MutationObserver(function (mutacoes) {
      mutacoes.forEach(function (m) {
        m.addedNodes.forEach(function (no) {
          if (no.nodeType === 1) desligarValidacaoNativa(no);
        });
      });
    }).observe(document.body, { childList: true, subtree: true });

    mostrarMensagensDjango();
  });
})();
