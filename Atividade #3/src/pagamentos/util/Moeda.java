package pagamentos.util;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.util.Locale;

/**
 * Utilitários para formatar e interpretar valores em reais.
 */
public final class Moeda {

    private static final Locale PT_BR = Locale.of("pt", "BR");

    private Moeda() {
    }

    /** Ex.: 1234.5 -> "R$ 1.234,50" */
    public static String formatar(BigDecimal valor) {
        return "R$ " + decimal(valor, "#,##0.00");
    }

    /** Ex.: 1234.5 -> "1234,50" (sem separador de milhar, ideal para CSV) */
    public static String decimal(BigDecimal valor) {
        return decimal(valor, "0.00");
    }

    /**
     * Converte o texto digitado pelo usuário em valor monetário.
     * Aceita "150", "150.75", "150,75" e "1.500,75".
     *
     * @throws NumberFormatException se o texto não for um valor válido com até 2 casas decimais
     */
    public static BigDecimal interpretar(String texto) {
        String normalizado = texto.trim().replace("R$", "").replace(" ", "");
        if (normalizado.contains(",")) {
            normalizado = normalizado.replace(".", "").replace(",", ".");
        }
        BigDecimal valor = new BigDecimal(normalizado);
        if (valor.scale() > 2) {
            throw new NumberFormatException("Use no máximo 2 casas decimais.");
        }
        return valor.setScale(2, RoundingMode.UNNECESSARY);
    }

    private static String decimal(BigDecimal valor, String padrao) {
        DecimalFormat formato = new DecimalFormat(padrao, DecimalFormatSymbols.getInstance(PT_BR));
        return formato.format(valor);
    }
}
