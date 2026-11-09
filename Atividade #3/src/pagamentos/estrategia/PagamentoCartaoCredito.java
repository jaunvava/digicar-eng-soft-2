package pagamentos.estrategia;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.YearMonth;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

import pagamentos.modelo.Transacao;
import pagamentos.util.Moeda;

/**
 * Estratégia concreta: pagamento com cartão de crédito.
 * Cobra 2,99% à vista e mais 1,49% por parcela adicional.
 */
public class PagamentoCartaoCredito implements EstrategiaPagamento {

    public static final int MAX_PARCELAS = 12;

    private static final BigDecimal TAXA_BASE = new BigDecimal("0.0299");
    private static final BigDecimal TAXA_POR_PARCELA_ADICIONAL = new BigDecimal("0.0149");
    private static final DateTimeFormatter FORMATO_VALIDADE = DateTimeFormatter.ofPattern("MM/yy");

    private final String numero;
    private final String titular;
    private final int parcelas;

    public PagamentoCartaoCredito(String numero, String titular, String validade, String cvv, int parcelas) {
        if (!numeroValido(numero)) {
            throw new IllegalArgumentException("Número de cartão inválido.");
        }
        if (titular == null || titular.isBlank()) {
            throw new IllegalArgumentException("Nome do titular é obrigatório.");
        }
        if (!validadeValida(validade)) {
            throw new IllegalArgumentException("Cartão vencido ou validade inválida.");
        }
        if (!cvvValido(cvv)) {
            throw new IllegalArgumentException("CVV inválido.");
        }
        if (!parcelasValidas(parcelas)) {
            throw new IllegalArgumentException("Parcelas devem estar entre 1 e " + MAX_PARCELAS + ".");
        }
        // O CVV é usado apenas na validação e nunca é armazenado.
        this.numero = somenteDigitos(numero);
        this.titular = titular.trim().toUpperCase();
        this.parcelas = parcelas;
    }

    /** Valida tamanho (13 a 19 dígitos) e o dígito verificador pelo algoritmo de Luhn. */
    public static boolean numeroValido(String numero) {
        if (numero == null) {
            return false;
        }
        String digitos = somenteDigitos(numero);
        if (!digitos.matches("\\d{13,19}")) {
            return false;
        }
        int soma = 0;
        boolean dobrar = false;
        for (int i = digitos.length() - 1; i >= 0; i--) {
            int d = digitos.charAt(i) - '0';
            if (dobrar) {
                d *= 2;
                if (d > 9) {
                    d -= 9;
                }
            }
            soma += d;
            dobrar = !dobrar;
        }
        return soma % 10 == 0;
    }

    /** Validade no formato MM/AA e não vencida. */
    public static boolean validadeValida(String validade) {
        try {
            YearMonth mesAno = YearMonth.parse(validade.trim(), FORMATO_VALIDADE);
            return !mesAno.isBefore(YearMonth.now());
        } catch (DateTimeParseException | NullPointerException e) {
            return false;
        }
    }

    public static boolean cvvValido(String cvv) {
        return cvv != null && cvv.trim().matches("\\d{3,4}");
    }

    public static boolean parcelasValidas(int parcelas) {
        return parcelas >= 1 && parcelas <= MAX_PARCELAS;
    }

    private static String somenteDigitos(String texto) {
        return texto.replaceAll("[\\s-]", "");
    }

    @Override
    public String getNome() {
        return "Cartão de Crédito";
    }

    @Override
    public Transacao pagar(BigDecimal valor) {
        BigDecimal percentual = TAXA_BASE.add(
                TAXA_POR_PARCELA_ADICIONAL.multiply(BigDecimal.valueOf(parcelas - 1)));
        BigDecimal taxa = valor.multiply(percentual).setScale(2, RoundingMode.HALF_UP);
        BigDecimal valorParcela = valor.add(taxa)
                .divide(BigDecimal.valueOf(parcelas), 2, RoundingMode.HALF_UP);
        String finalCartao = numero.substring(numero.length() - 4);

        System.out.println("  > Solicitando autorização à operadora para o cartão final " + finalCartao + "...");
        System.out.println("  > Pagamento autorizado em " + parcelas + "x de " + Moeda.formatar(valorParcela) + ".");

        return new Transacao(
                Transacao.novoId("CC"),
                LocalDateTime.now(),
                getNome(),
                "Cartão final " + finalCartao + " (" + titular + ") em "
                        + parcelas + "x de " + Moeda.formatar(valorParcela),
                valor,
                taxa);
    }
}
