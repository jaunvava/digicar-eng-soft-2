package pagamentos.modelo;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Representa um pagamento já realizado.
 */
public record Transacao(
        String id,
        LocalDateTime dataHora,
        String metodo,
        String detalhes,
        BigDecimal valor,
        BigDecimal taxa) {

    public BigDecimal total() {
        return valor.add(taxa);
    }

    public static String novoId(String prefixo) {
        return prefixo + "-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }
}
