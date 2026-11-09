package pagamentos.estrategia;

import java.math.BigDecimal;

import pagamentos.modelo.Transacao;

/**
 * Padrão Strategy: contrato comum a todas as formas de pagamento.
 * Cada implementação decide como o pagamento é efetuado e qual taxa é cobrada.
 */
public interface EstrategiaPagamento {

    String getNome();

    Transacao pagar(BigDecimal valor);
}
