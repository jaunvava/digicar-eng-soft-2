package org.example.produto;

public class EmailNotificacao implements Notificacao {
    private final String email;

    public EmailNotificacao(String email) {
        this.email = email;
    }

    @Override
    public void notificar(String mensagem) {
        System.out.println("E-mail enviado para " + email + ": " + mensagem);
    }
}
