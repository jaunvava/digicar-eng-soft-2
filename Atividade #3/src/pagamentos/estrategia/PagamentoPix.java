package pagamentos.estrategia;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import pagamentos.modelo.Transacao;

/**
 * Estratégia concreta: pagamento via Pix (sem taxa).
 */
public class PagamentoPix implements EstrategiaPagamento {

    private final String chave;
    private final String tipoChave;

    public PagamentoPix(String chave) {
        this.tipoChave = identificarTipoChave(chave);
        if (tipoChave == null) {
            throw new IllegalArgumentException("Chave Pix inválida: " + chave);
        }
        this.chave = chave.trim();
    }

    public static boolean chaveValida(String chave) {
        return identificarTipoChave(chave) != null;
    }

    /** Retorna o tipo da chave (CPF, CNPJ, e-mail, telefone ou aleatória) ou null se for inválida. */
    private static String identificarTipoChave(String chave) {
        if (chave == null || chave.isBlank()) {
            return null;
        }
        String texto = chave.trim();
        String digitos = texto.replaceAll("[.\\-/]", "");
        if (texto.matches("[^@\\s]+@[^@\\s]+\\.[^@\\s]+")) {
            return "e-mail";
        }
        if (texto.matches("\\+\\d{12,13}")) {
            return "telefone";
        }
        if (texto.matches("(?i)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")) {
            return "aleatória";
        }
        if (digitos.matches("\\d{11}")) {
            return "CPF";
        }
        if (digitos.matches("\\d{14}")) {
            return "CNPJ";
        }
        return null;
    }

    @Override
    public String getNome() {
        return "Pix";
    }

    @Override
    public Transacao pagar(BigDecimal valor) {
        System.out.println("  > Enviando Pix para a chave " + tipoChave + " " + chave + "...");
        System.out.println("  > Pix confirmado instantaneamente (sem taxa).");
        return new Transacao(
                Transacao.novoId("PIX"),
                LocalDateTime.now(),
                getNome(),
                "Chave " + tipoChave + ": " + chave,
                valor,
                BigDecimal.ZERO.setScale(2));
    }
}
