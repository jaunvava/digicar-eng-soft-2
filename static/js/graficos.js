/* ══════════════════════════════════════════════════════════════════════
 *  Gráficos do sistema (Chart.js)
 *
 *  Os dados vêm da view via {{ dados|json_script:"id" }} e são lidos com
 *  Graficos.ler("id"). Precisa ser carregado depois do chart.umd.min.js.
 *
 *  Graficos.rosca(canvas, {rotulos, valores, cores, moeda})
 *  Graficos.barras(canvas, {rotulos, valores, cores, moeda, horizontal, rotulo})
 * ══════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var CORES = {
    primaria: "#2563eb",
    sucesso: "#10b981",
    alerta: "#f59e0b",
    perigo: "#ef4444",
    info: "#0ea5e9",
    roxo: "#8b5cf6",
    neutra: "#94a3b8",
    vazio: "#e2e8f0",
  };

  var formatoMoeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
  var formatoNumero = new Intl.NumberFormat("pt-BR");

  function formatar(valor, moeda) {
    return moeda ? formatoMoeda.format(valor) : formatoNumero.format(valor);
  }

  function configurarPadroes() {
    if (typeof Chart === "undefined" || Chart.__digicar) return;
    Chart.defaults.font.family = "'Inter', 'Segoe UI', Arial, sans-serif";
    Chart.defaults.color = "#64748b";
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
    Chart.defaults.plugins.legend.labels.padding = 15;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.maintainAspectRatio = false;
    Chart.__digicar = true;
  }

  function canvasDe(alvo) {
    return typeof alvo === "string" ? document.getElementById(alvo) : alvo;
  }

  function criar(alvo, config) {
    if (typeof Chart === "undefined") {
      console.warn("Chart.js não carregado.");
      return null;
    }
    var canvas = canvasDe(alvo);
    if (!canvas) return null;
    configurarPadroes();
    var anterior = Chart.getChart(canvas);
    if (anterior) anterior.destroy();
    return new Chart(canvas, config);
  }

  function semDados(valores) {
    return !valores.length || valores.every(function (v) { return !v; });
  }

  /** Mostra uma mensagem no lugar do gráfico quando não há dados. */
  function avisoVazio(canvas, texto) {
    var aviso = document.createElement("div");
    aviso.className = "grafico-vazio";
    aviso.textContent = texto || "Sem dados para exibir.";
    canvas.replaceWith(aviso);
  }

  window.Graficos = {
    CORES: CORES,
    formatar: formatar,

    ler: function (id) {
      var el = document.getElementById(id);
      return el ? JSON.parse(el.textContent) : null;
    },

    rosca: function (alvo, d) {
      var canvas = canvasDe(alvo);
      if (!canvas) return null;
      if (semDados(d.valores)) return avisoVazio(canvas, d.vazio);
      return criar(canvas, {
        type: "doughnut",
        data: {
          labels: d.rotulos,
          datasets: [{ data: d.valores, backgroundColor: d.cores, borderWidth: 0, hoverOffset: 6 }],
        },
        options: {
          cutout: "70%",
          plugins: {
            legend: { position: "bottom" },
            tooltip: {
              callbacks: {
                label: function (ctx) {
                  var total = ctx.dataset.data.reduce(function (a, b) { return a + b; }, 0);
                  var pct = total ? Math.round((ctx.parsed / total) * 100) : 0;
                  return " " + ctx.label + ": " + formatar(ctx.parsed, d.moeda) + " (" + pct + "%)";
                },
              },
            },
          },
        },
      });
    },

    barras: function (alvo, d) {
      var canvas = canvasDe(alvo);
      if (!canvas) return null;
      if (semDados(d.valores)) return avisoVazio(canvas, d.vazio);
      var eixoValor = d.horizontal ? "x" : "y";
      var escalas = {};
      escalas[eixoValor] = {
        beginAtZero: true,
        ticks: {
          precision: d.moeda ? undefined : 0,
          callback: function (v) { return formatar(v, d.moeda); },
        },
        grid: { color: "#f1f5f9" },
      };
      escalas[d.horizontal ? "y" : "x"] = { grid: { display: false } };
      return criar(canvas, {
        type: "bar",
        data: {
          labels: d.rotulos,
          datasets: [{
            label: d.rotulo || "",
            data: d.valores,
            backgroundColor: d.cores || CORES.primaria,
            borderRadius: 4,
            maxBarThickness: 36,
          }],
        },
        options: {
          indexAxis: d.horizontal ? "y" : "x",
          scales: escalas,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function (ctx) {
                  return " " + formatar(ctx.parsed[eixoValor], d.moeda);
                },
              },
            },
          },
        },
      });
    },
  };
})();
