/* =====================================================
   DigiCAR - App JS
   Sidebar toggle, submenu, global interactions
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {
  // ── Sobrescrever alertas nativos do navegador com SweetAlert2 ─────────
  const originalAlert = window.alert;
  window.alert = function (message) {
    if (typeof Swal !== "undefined") {
      Swal.fire({
        text: message,
        confirmButtonColor: "#2563eb",
      });
    } else {
      console.warn("SweetAlert2 not loaded, falling back to native alert");
      originalAlert(message);
    }
  };

  const originalConfirm = window.confirm;
  window.confirm = function (message) {
    // Nota: window.confirm é síncrono e bloqueia a UI. Swal é assíncrono.
    // Sobrescrever globalmente o comportamento síncrono é complexo,
    // então mantemos o confirmDelete como padrão recomendado.
    // Mas para alertas simples (alert), a substituição acima funciona.
    return originalConfirm(message);
  };

  const sidebar = document.getElementById("sidebar");
  const mainContent = document.getElementById("mainContent");
  const toggleBtn = document.getElementById("sidebarToggle");

  // ── Sidebar toggle ──────────────────────────────────
  if (toggleBtn) {
    toggleBtn.addEventListener("click", function () {
      sidebar.classList.toggle("collapsed");
      mainContent.classList.toggle("sidebar-collapsed");
      // Persist state
      const collapsed = sidebar.classList.contains("collapsed");
      localStorage.setItem("sidebarCollapsed", collapsed);
    });
  }

  // Restore sidebar state
  if (localStorage.getItem("sidebarCollapsed") === "true") {
    sidebar && sidebar.classList.add("collapsed");
    mainContent && mainContent.classList.add("sidebar-collapsed");
  }

  // ── Auto-open active submenus ────────────────────────
  const activeSubItem = document.querySelector(
    ".nav-submenu .nav-link-sidebar.active",
  );
  if (activeSubItem) {
    const submenu = activeSubItem.closest(".nav-submenu");
    if (submenu) {
      submenu.classList.add("open");
      const arrow =
        submenu.previousElementSibling &&
        submenu.previousElementSibling.querySelector(".nav-arrow");
      if (arrow) arrow.classList.add("rotated");
    }
  }

  // ── Search shortcut (Ctrl+K) ─────────────────────────
  const searchInput = document.getElementById("globalSearch");
  if (searchInput) {
    document.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    });
  }

  // ── Auto-dismiss alerts ───────────────────────────────
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ── Tooltips Bootstrap ────────────────────────────────
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach((el) => new bootstrap.Tooltip(el, { trigger: "hover" }));
});

// ── Toggle submenu (usado inline no template) ──────────
function toggleSubmenu(menuId, event) {
  if (event) {
    event.stopPropagation();
  }
  const menu = document.getElementById(menuId);
  const arrow = document.getElementById(menuId.replace("Menu", "Arrow"));

  if (!menu) return;

  const isOpen = menu.classList.contains("open");

  // Fechar apenas os submenus que não são ancestrais ou descendentes do menu clicado
  document.querySelectorAll(".nav-submenu.open").forEach(function (m) {
    if (m !== menu && !m.contains(menu) && !menu.contains(m)) {
      m.classList.remove("open");
      const arrId = m.id.replace("Menu", "Arrow");
      const arr = document.getElementById(arrId);
      if (arr) arr.classList.remove("rotated");
    }
  });

  // Abrir ou fechar o clicado
  if (!isOpen) {
    menu.classList.add("open");
    if (arrow) arrow.classList.add("rotated");
  } else {
    menu.classList.remove("open");
    if (arrow) arrow.classList.remove("rotated");
  }
}

// ══════════════════════════════════════════════════════
//  MÁSCARAS GLOBAIS DE CAMPOS — Moeda e Quantidade
// ══════════════════════════════════════════════════════

/**
 * Formata um valor numérico para o padrão BRL de exibição.
 * Ex: 1234.56  → "1.234,56"
 */
function _numToBRL(num) {
  return num.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/**
 * Converte string BRL de volta para float.
 * Ex: "1.234,56" → 1234.56
 */
function _brlToNum(str) {
  if (!str) return 0;
  // Remove pontos de milhar, troca vírgula decimal por ponto
  return parseFloat(str.replace(/\./g, "").replace(",", ".")) || 0;
}

/**
 * Aplica máscara de moeda a um <input type="text"> com data-mask="currency".
 * Mantém um <input type="hidden"> com o nome original para envio ao backend.
 */
function _applyCurrencyMask(input) {
  if (input._currencyMaskApplied) return;
  input._currencyMaskApplied = true;

  // Recupera o valor inicial (pode vir de value="0.50" ou value="1234.56")
  const initialRaw = parseFloat(input.value) || 0;

  // Cria o hidden input que carrega o valor numérico real para o backend
  const hidden = document.createElement("input");
  hidden.type = "hidden";
  hidden.name = input.name;
  hidden.value = initialRaw.toFixed(2);
  input.removeAttribute("name"); // retira o name do campo visível
  input.insertAdjacentElement("afterend", hidden);

  // Exibe valor formatado no campo visível
  input.value = _numToBRL(initialRaw);
  input.setAttribute("autocomplete", "off");
  input.style.textAlign = "right";

  function applyMask() {
    // Remove tudo que não for dígito
    let digits = input.value.replace(/\D/g, "");
    if (!digits) digits = "0";
    const num = parseInt(digits, 10) / 100;
    input.value = _numToBRL(num);
    hidden.value = num.toFixed(2);
    // Dispara evento personalizado para que cálculos de linha/total re-executem
    hidden.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(
      new CustomEvent("maskedInput", { bubbles: true, detail: { value: num } }),
    );
  }

  input.addEventListener("input", applyMask);

  // Ao focar: seleciona tudo para facilitar edição
  input.addEventListener("focus", function () {
    this.select();
  });

  // Ao perder foco: garante formatação correta
  input.addEventListener("blur", function () {
    let num = _brlToNum(this.value);
    if (isNaN(num)) num = 0;
    this.value = _numToBRL(num);
    hidden.value = num.toFixed(2);
  });
}

/**
 * Aplica validação visual a um <input type="number"> com data-mask="quantity".
 */
function _applyQuantityMask(input) {
  if (input._qtyMaskApplied) return;
  input._qtyMaskApplied = true;

  const minVal = parseFloat(input.min) || 0;

  function validate() {
    const v = parseFloat(input.value);
    if (isNaN(v) || v < minVal) {
      input.style.borderColor = "#ef4444";
      input.style.boxShadow = "0 0 0 2px rgba(239,68,68,0.2)";
    } else {
      input.style.borderColor = "";
      input.style.boxShadow = "";
    }
  }

  input.addEventListener("input", validate);
  input.addEventListener("blur", function () {
    const v = parseFloat(this.value);
    if (isNaN(v) || v < minVal) {
      this.value = minVal || 1;
      validate();
    }
  });
  validate();
}

/**
 * Escaneia o DOM (ou um nó raiz) e inicializa todas as máscaras.
 */
function initFieldMasks(root) {
  root = root || document;

  // Campos de moeda: data-mask="currency"
  root
    .querySelectorAll('input[data-mask="currency"]')
    .forEach(_applyCurrencyMask);

  // Campos de quantidade: data-mask="quantity"
  root
    .querySelectorAll('input[data-mask="quantity"]')
    .forEach(_applyQuantityMask);
}

// Inicializa ao carregar e observa inserções dinâmicas (linhas de itens)
document.addEventListener("DOMContentLoaded", function () {
  initFieldMasks(document);

  // MutationObserver para linhas adicionadas dinamicamente (orçamentos, ordens, PDV…)
  const observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      mutation.addedNodes.forEach(function (node) {
        if (node.nodeType === 1) {
          initFieldMasks(node);
          // O próprio nó pode ser o input
          if (node.matches && node.matches('input[data-mask="currency"]'))
            _applyCurrencyMask(node);
          if (node.matches && node.matches('input[data-mask="quantity"]'))
            _applyQuantityMask(node);
        }
      });
    });
  });
  observer.observe(document.body, { childList: true, subtree: true });
});

// ── Format currency inputs (legacy helper) ─────────────
function formatCurrency(input) {
  let v = input.value.replace(/\D/g, "");
  v = (parseInt(v, 10) / 100).toFixed(2);
  input.value = v.replace(".", ",");
}

// ── Confirm delete (COM SWEETALERT2) ──────────────────
function confirmDelete(
  url,
  message = "Deseja realmente excluir este registro?",
) {
  // Se o Swal (SweetAlert2) estiver disponível, usa ele. Caso contrário, usa confirm original.
  if (typeof Swal !== "undefined") {
    Swal.fire({
      title: "Confirmação",
      text: message,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#2563eb",
      cancelButtonColor: "#64748b",
      confirmButtonText: "Sim, prosseguir",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        window.location.href = url;
      }
    });
  } else {
    if (confirm(message)) {
      window.location.href = url;
    }
  }
}

// ══════════════════════════════════════════════════════
//  SISTEMA DE NOTIFICAÇÕES
// ══════════════════════════════════════════════════════
(function () {
  var badge = document.getElementById("notifBadge");
  var list = document.getElementById("notifList");
  var countEl = document.getElementById("notifCount");
  var dropdown = document.getElementById("notifDropdown");
  var wrapper = document.getElementById("notifWrapper");

  if (!badge || !dropdown) return; // página sem navbar (ex: login)

  // Cores por tipo de notificação
  var TIPO_STYLE = {
    urgente: { bg: "#fee2e2", color: "#ef4444" },
    perigo: { bg: "#fee2e2", color: "#ef4444" },
    aviso: { bg: "#fef3c7", color: "#f59e0b" },
    info: { bg: "#dbeafe", color: "#2563eb" },
  };

  function renderNotifs(data) {
    var total = data.total || 0;
    var items = data.items || [];

    // Badge do sino
    if (total > 0) {
      badge.textContent = total > 99 ? "99+" : total;
      badge.style.display = "flex";
    } else {
      badge.style.display = "none";
    }

    // Contador no header
    if (countEl) countEl.textContent = total;

    // Lista de itens
    if (!list) return;
    if (items.length === 0) {
      list.innerHTML =
        '<div class="notif-empty">' +
        '<i class="bi bi-check-circle" style="font-size:24px;color:#10b981;"></i>' +
        "<p>Tudo em ordem!</p></div>";
      return;
    }

    list.innerHTML = items
      .map(function (n) {
        var s = TIPO_STYLE[n.tipo] || TIPO_STYLE.info;
        return (
          '<a href="' +
          n.url +
          '" class="notif-item">' +
          '<div class="notif-icon" style="background:' +
          s.bg +
          ";color:" +
          s.color +
          ';">' +
          '<i class="bi ' +
          n.icone +
          '"></i></div>' +
          '<div><div class="notif-item-title">' +
          n.titulo +
          "</div>" +
          '<div class="notif-item-desc">' +
          n.descricao +
          "</div></div>" +
          "</a>"
        );
      })
      .join("");
  }

  function fetchNotifs() {
    fetch("/notificacoes/", { credentials: "same-origin" })
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (data) {
        if (data) renderNotifs(data);
      })
      .catch(function () {});
  }

  // Fetch imediato + polling cada 60s
  fetchNotifs();
  setInterval(fetchNotifs, 60000);

  // Fechar ao clicar fora do wrapper
  document.addEventListener("click", function (e) {
    if (wrapper && !wrapper.contains(e.target)) {
      dropdown.style.display = "none";
    }
  });
})();

// Toggle do dropdown — manipula style.display diretamente
function toggleNotif(e) {
  e.stopPropagation();
  var dd = document.getElementById("notifDropdown");
  if (!dd) return;
  if (dd.style.display === "none" || dd.style.display === "") {
    dd.style.display = "block";
  } else {
    dd.style.display = "none";
  }
}
