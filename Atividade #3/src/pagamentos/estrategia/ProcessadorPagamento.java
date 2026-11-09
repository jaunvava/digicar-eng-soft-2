package pagamentos.estrategia;

import java.math.BigDecimal;

import pagamentos.modelo.Transacao;
import pagamentos.repositorio.RepositorioTransacoes;

/**
 * Contexto do padrão Strategy: executa o pagamento com a estratégia escolhida
 * sem precisar saber qual forma de pagamento está sendo usada.
 */
public class ProcessadorPagamento {

    private final RepositorioTransacoes repositorio;
    private EstrategiaPagamento estrategia;

    public ProcessadorPagamento(RepositorioTransacoes repositorio) {
        this.repositorio = repositorio;
    }

    public void setEstrategia(EstrategiaPagamento estrategia) {
        this.estrategia = estrategia;
    }

    public Transacao processar(BigDecimal valor) {
        if (estrategia == null) {
            throw new IllegalStateException("Nenhuma forma de pagamento foi selecionada.");
        }
        if (valor == null || valor.signum() <= 0) {
            throw new IllegalArgumentException("O valor deve ser maior que zero.");
        }
        Transacao transacao = estrategia.pagar(valor);
        repositorio.salvar(transacao);
        return transacao;
    }
}
