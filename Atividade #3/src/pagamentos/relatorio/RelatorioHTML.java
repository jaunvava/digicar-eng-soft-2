package pagamentos.relatorio;

import java.time.LocalDateTime;

import pagamentos.modelo.Transacao;
import pagamentos.util.Moeda;

/**
 * Relatório HTML com tabela estilizada, pronto para abrir no navegador.
 */
public class RelatorioHTML extends GeradorRelatorio {

    @Override
    public String extensao() {
        return "html";
    }

    @Override
    protected String cabecalho(LocalDateTime geradoEm) {
        return """
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                  <meta charset="UTF-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                  <title>Relatório de Transações</title>
                  <style>
                    body { font-family: Segoe UI, Arial, sans-serif; margin: 32px; color: #222; background: #f6f7f9; }
                    h1 { margin-bottom: 4px; }
                    .gerado { color: #666; margin-top: 0; }
                    table { border-collapse: collapse; width: 100%%; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
                    th, td { padding: 10px 12px; border-bottom: 1px solid #e3e5e8; text-align: left; }
                    th { background: #1f4e79; color: #fff; }
                    td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
                    tbody tr:hover { background: #eef4fb; }
                    tfoot td { font-weight: bold; background: #e9eef4; }
                    .metodo { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 13px; }
                    .pix { background: #d9f5ec; color: #0b6e4f; }
                    .cartao { background: #e3e8fb; color: #2c3e9b; }
                  </style>
                </head>
                <body>
                  <h1>Relatório de Transações</h1>
                  <p class="gerado">Gerado em %s</p>
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th><th>Data/Hora</th><th>Método</th><th>Detalhes</th>
                        <th class="num">Valor</th><th class="num">Taxa</th><th class="num">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                """.formatted(geradoEm.format(FORMATO_DATA_HORA));
    }

    @Override
    protected String linha(Transacao t) {
        String classeMetodo = t.metodo().equals("Pix") ? "pix" : "cartao";
        return """
                      <tr>
                        <td>%s</td><td>%s</td><td><span class="metodo %s">%s</span></td><td>%s</td>
                        <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>
                      </tr>
                """.formatted(
                escapar(t.id()),
                t.dataHora().format(FORMATO_DATA_HORA),
                classeMetodo,
                escapar(t.metodo()),
                escapar(t.detalhes()),
                Moeda.formatar(t.valor()),
                Moeda.formatar(t.taxa()),
                Moeda.formatar(t.total()));
    }

    @Override
    protected String rodape(ResumoTransacoes resumo) {
        return """
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colspan="4">Total: %d transação(ões)</td>
                        <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>
                      </tr>
                    </tfoot>
                  </table>
                </body>
                </html>
                """.formatted(
                resumo.quantidade(),
                Moeda.formatar(resumo.valorBruto()),
                Moeda.formatar(resumo.taxas()),
                Moeda.formatar(resumo.total()));
    }

    private String escapar(String texto) {
        return texto.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;");
    }
}
