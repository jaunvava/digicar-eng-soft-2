/* ══════════════════════════════════════════════════════════════════════
 *  Busca de cliente com paginação no servidor
 *  (templates/_busca_cliente.html + /clientes/buscar/)
 *
 *  O navegador nunca recebe a lista inteira de clientes: cada consulta
 *  traz 20 resultados e o restante vem ao rolar a lista ("carregar mais").
 *
 *  Ao escolher (ou limpar) um cliente, dispara no componente o evento
 *  "cliente-selecionado" com detail = {id, nome} ou null.
 * ══════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var ATRASO_DIGITACAO = 250;
  var MSG_SELECIONE = "Selecione um cliente da lista.";

  function iniciar(raiz) {
    if (raiz.dataset.iniciado) return;
    raiz.dataset.iniciado = "1";

    var url = raiz.dataset.url;
    var texto = raiz.querySelector(".busca-cliente-texto");
    var oculto = raiz.querySelector(".busca-cliente-id");
    var lista = raiz.querySelector(".busca-cliente-lista");
    var limpar = raiz.querySelector(".busca-cliente-limpar");

    var estado = { termo: "", pagina: 0, temMais: false, carregando: false, seq: 0, ativo: -1 };
    var timer = null;

    function abrir() {
      lista.hidden = false;
      texto.setAttribute("aria-expanded", "true");
    }
    function fechar() {
      lista.hidden = true;
      texto.setAttribute("aria-expanded", "false");
      estado.ativo = -1;
    }

    function itens() {
      return lista.querySelectorAll(".busca-cliente-item");
    }

    function marcarAtivo(indice) {
      var todos = itens();
      if (!todos.length) return;
      estado.ativo = Math.max(0, Math.min(indice, todos.length - 1));
      todos.forEach(function (el, i) {
        el.classList.toggle("ativo", i === estado.ativo);
        el.setAttribute("aria-selected", i === estado.ativo ? "true" : "false");
      });
      todos[estado.ativo].scrollIntoView({ block: "nearest" });
    }

    function mensagem(classe, conteudo) {
      var el = document.createElement("div");
      el.className = classe;
      el.textContent = conteudo;
      return el;
    }

    function atualizarValidade() {
      // O campo visível é o que o navegador valida (o oculto não é validado).
      texto.setCustomValidity(texto.value.trim() && !oculto.value ? MSG_SELECIONE : "");
      if (limpar) limpar.hidden = !texto.value;
    }

    function escolher(cliente) {
      oculto.value = cliente ? cliente.id : "";
      texto.value = cliente ? cliente.nome : "";
      atualizarValidade();
      texto.classList.remove("is-invalid");
      fechar();
      raiz.dispatchEvent(new CustomEvent("cliente-selecionado", { bubbles: true, detail: cliente }));
    }

    function renderizar(resultados, acrescentar) {
      lista.querySelectorAll(".busca-cliente-mais, .busca-cliente-vazio, .busca-cliente-erro").forEach(function (el) {
        el.remove();
      });
      if (!acrescentar) {
        lista.innerHTML = "";
        estado.ativo = -1;
      }
      resultados.forEach(function (c) {
        var item = document.createElement("div");
        item.className = "busca-cliente-item";
        item.setAttribute("role", "option");
        var nome = document.createElement("div");
        nome.className = "busca-cliente-nome";
        nome.textContent = c.nome;
        item.appendChild(nome);
        if (c.detalhe) {
          var detalhe = document.createElement("div");
          detalhe.className = "busca-cliente-detalhe";
          detalhe.textContent = c.detalhe;
          item.appendChild(detalhe);
        }
        // mousedown (e não click) para escolher antes do blur do campo.
        item.addEventListener("mousedown", function (e) {
          e.preventDefault();
          escolher(c);
        });
        lista.appendChild(item);
      });
      if (!itens().length) {
        lista.appendChild(mensagem("busca-cliente-vazio",
          estado.termo ? "Nenhum cliente encontrado para “" + estado.termo + "”." : "Nenhum cliente cadastrado."));
      } else if (estado.temMais) {
        lista.appendChild(mensagem("busca-cliente-mais", "Role para carregar mais…"));
      }
      abrir();
    }

    function buscar(pagina) {
      var seq = ++estado.seq;
      estado.carregando = true;
      raiz.classList.add("carregando");
      var params = new URLSearchParams({ q: estado.termo, pagina: pagina });
      fetch(url + "?" + params.toString(), { headers: { Accept: "application/json" }, credentials: "same-origin" })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          return r.json();
        })
        .then(function (dados) {
          if (seq !== estado.seq) return; // resposta de uma busca antiga
          estado.pagina = dados.pagina;
          estado.temMais = dados.tem_mais;
          renderizar(dados.resultados, pagina > 1);
        })
        .catch(function () {
          if (seq !== estado.seq) return;
          lista.innerHTML = "";
          lista.appendChild(mensagem("busca-cliente-erro", "Não foi possível buscar os clientes. Tente de novo."));
          abrir();
        })
        .finally(function () {
          if (seq !== estado.seq) return;
          estado.carregando = false;
          raiz.classList.remove("carregando");
        });
    }

    function novaBusca() {
      estado.termo = texto.value.trim();
      buscar(1);
    }

    texto.addEventListener("input", function () {
      if (oculto.value) {
        oculto.value = "";
        raiz.dispatchEvent(new CustomEvent("cliente-selecionado", { bubbles: true, detail: null }));
      }
      atualizarValidade();
      clearTimeout(timer);
      timer = setTimeout(novaBusca, ATRASO_DIGITACAO);
    });

    texto.addEventListener("focus", function () {
      // Sem cliente escolhido: mostra a primeira página para navegar como num select.
      if (!oculto.value) novaBusca();
    });

    texto.addEventListener("blur", function () {
      setTimeout(fechar, 120);
    });

    texto.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (lista.hidden) novaBusca();
        else marcarAtivo(estado.ativo + 1);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        marcarAtivo(estado.ativo - 1);
      } else if (e.key === "Enter") {
        if (!lista.hidden && estado.ativo >= 0) {
          e.preventDefault();
          itens()[estado.ativo].dispatchEvent(new MouseEvent("mousedown"));
        }
      } else if (e.key === "Escape") {
        fechar();
      }
    });

    lista.addEventListener("scroll", function () {
      var pertoDoFim = lista.scrollTop + lista.clientHeight >= lista.scrollHeight - 40;
      if (pertoDoFim && estado.temMais && !estado.carregando) buscar(estado.pagina + 1);
    });

    if (limpar) {
      limpar.addEventListener("click", function () {
        escolher(null);
        texto.focus();
      });
    }

    atualizarValidade();
  }

  function iniciarEm(raiz) {
    if (raiz.matches && raiz.matches("[data-busca-cliente]")) iniciar(raiz);
    if (raiz.querySelectorAll) raiz.querySelectorAll("[data-busca-cliente]").forEach(iniciar);
  }

  document.addEventListener("DOMContentLoaded", function () {
    iniciarEm(document);
  });
})();
