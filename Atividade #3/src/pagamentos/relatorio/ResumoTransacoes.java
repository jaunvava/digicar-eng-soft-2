package pagamentos.relatorio;

import java.math.BigDecimal;
import java.util.List;

import pagamentos.modelo.Transacao;

/**
 * Totais exibidos no rodapé de todos os relatórios.
 */
public record ResumoTransacoes(int quantidade, BigDecimal valorBruto, BigDecimal taxas, BigDecimal total) {

    public static ResumoTransacoes de(List<Transacao> transacoes) {
        BigDecimal valorBruto = BigDecimal.ZERO.setScale(2);
        BigDecimal taxas = BigDecimal.ZERO.setScale(2);
        for (Transacao t : transacoes) {
            valorBruto = valorBruto.add(t.valor());
            taxas = taxas.add(t.taxa());
        }
        return new ResumoTransacoes(transacoes.size(), valorBruto, taxas, valorBruto.add(taxas));
    }
}
