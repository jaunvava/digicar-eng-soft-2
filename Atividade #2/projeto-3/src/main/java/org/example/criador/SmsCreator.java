package org.example.criador;

import org.example.produto.Notificacao;
import org.example.produto.Smsnotificacao;

public class SmsCreator extends NotificacaoCreator {
    private final String telefone;

    public SmsCreator(String telefone) {
        this.telefone = telefone;
    }

    @Override
    protected Notificacao criarNotificacao() {
        return new Smsnotificacao(telefone);
    }
}
