package org.example.criador;

import org.example.produto.Notificacao;

public abstract class NotificacaoCreator {
    protected abstract Notificacao criarNotificacao();

    public void notificar(String mensagem) {
        Notificacao notificacao = criarNotificacao();
        notificacao.notificar(mensagem);
    }
}
