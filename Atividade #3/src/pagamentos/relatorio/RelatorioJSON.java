package pagamentos.relatorio;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import pagamentos.modelo.Transacao;

/**
 * Relatório JSON. Usa o hook separadorEntreLinhas() para inserir as vírgulas entre os objetos do array.
 */
public class RelatorioJSON extends GeradorRelatorio {

    private static final DateTimeFormatter ISO = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    @Override
    public String extensao() {
        return "json";
    }

    @Override
    protected String cabecalho(LocalDateTime geradoEm) {
        return "{\n"
                + "  \"geradoEm\": \"" + geradoEm.withNano(0).format(ISO) + "\",\n"
                + "  \"transacoes\": [\n";
    }

    @Override
    protected String linha(Transacao t) {
        return "    {\n"
                + "      \"id\": \"" + escapar(t.id()) + "\",\n"
                + "      \"dataHora\": \"" + t.dataHora().withNano(0).format(ISO) + "\",\n"
                + "      \"metodo\": \"" + escapar(t.metodo()) + "\",\n"
                + "      \"detalhes\": \"" + escapar(t.detalhes()) + "\",\n"
                + "      \"valor\": " + t.valor().toPlainString() + ",\n"
                + "      \"taxa\": " + t.taxa().toPlainString() + ",\n"
                + "      \"total\": " + t.total().toPlainString() + "\n"
                + "    }";
    }

    @Override
    protected String separadorEntreLinhas() {
        return ",\n";
    }

    @Override
    protected String rodape(ResumoTransacoes resumo) {
        return "\n  ],\n"
                + "  \"resumo\": {\n"
                + "    \"quantidade\": " + resumo.quantidade() + ",\n"
                + "    \"valorBruto\": " + resumo.valorBruto().toPlainString() + ",\n"
                + "    \"taxas\": " + resumo.taxas().toPlainString() + ",\n"
                + "    \"total\": " + resumo.total().toPlainString() + "\n"
                + "  }\n"
                + "}\n";
    }

    private String escapar(String texto) {
        StringBuilder sb = new StringBuilder();
        for (char c : texto.toCharArray()) {
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (c < 0x20) {
                        sb.append(String.format("\\u%04x", (int) c));
                    } else {
                        sb.append(c);
                    }
                }
            }
        }
        return sb.toString();
    }
}
