package org.example.produto;

public class Smsnotificacao implements Notificacao {
    private final String telefone;

    public Smsnotificacao(String telefone) {
        this.telefone = telefone;
    }

    @Override
    public void notificar(String mensagem) {
        System.out.println("SMS enviado para " + telefone + ": " + mensagem);
    }
}
