package pagamentos.repositorio;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import pagamentos.modelo.Transacao;

/**
 * Armazena em memória as transações realizadas durante a execução.
 */
public class RepositorioTransacoes {

    private final List<Transacao> transacoes = new ArrayList<>();

    public void salvar(Transacao transacao) {
        transacoes.add(transacao);
    }

    public List<Transacao> listarTodas() {
        return Collections.unmodifiableList(transacoes);
    }

    public boolean estaVazio() {
        return transacoes.isEmpty();
    }
}
