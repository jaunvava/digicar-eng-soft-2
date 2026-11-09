package org.example.criador;

import org.example.produto.EmailNotificacao;
import org.example.produto.Notificacao;

public class EmailCreator extends NotificacaoCreator {
    private final String email;

    public EmailCreator(String email) {
        this.email = email;
    }

    @Override
    protected Notificacao criarNotificacao() {
        return new EmailNotificacao(email);
    }
}
