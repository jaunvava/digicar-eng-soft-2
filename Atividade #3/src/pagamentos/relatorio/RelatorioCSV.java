package pagamentos.relatorio;

import java.time.LocalDateTime;

import pagamentos.modelo.Transacao;
import pagamentos.util.Moeda;

/**
 * Relatório CSV separado por ";" (padrão do Excel em português).
 */
public class RelatorioCSV extends GeradorRelatorio {

    private static final String BOM_UTF8 = "﻿";

    @Override
    public String extensao() {
        return "csv";
    }

    @Override
    protected String cabecalho(LocalDateTime geradoEm) {
        // O BOM faz o Excel reconhecer o arquivo como UTF-8 e exibir os acentos corretamente.
        return BOM_UTF8 + "id;data_hora;metodo;detalhes;valor;taxa;total\n";
    }

    @Override
    protected String linha(Transacao t) {
        return String.join(";",
                escapar(t.id()),
                escapar(t.dataHora().format(FORMATO_DATA_HORA)),
                escapar(t.metodo()),
                escapar(t.detalhes()),
                escapar(Moeda.decimal(t.valor())),
                escapar(Moeda.decimal(t.taxa())),
                escapar(Moeda.decimal(t.total()))) + "\n";
    }

    @Override
    protected String rodape(ResumoTransacoes resumo) {
        return String.join(";",
                "TOTAL", "", "",
                escapar(resumo.quantidade() + " transação(ões)"),
                escapar(Moeda.decimal(resumo.valorBruto())),
                escapar(Moeda.decimal(resumo.taxas())),
                escapar(Moeda.decimal(resumo.total()))) + "\n";
    }

    /** Envolve o campo em aspas quando ele contém ";", aspas ou quebra de linha. */
    private String escapar(String campo) {
        if (campo.contains(";") || campo.contains("\"") || campo.contains("\n")) {
            return "\"" + campo.replace("\"", "\"\"") + "\"";
        }
        return campo;
    }
}
