package org.example;

import org.example.criador.EmailCreator;
import org.example.criador.NotificacaoCreator;
import org.example.criador.SmsCreator;

public class Main {
    public static void main(String[] args) {
        NotificacaoCreator email = new EmailCreator("cliente@example.com");
        email.notificar("Pedido Aprovado!");

        NotificacaoCreator sms = new SmsCreator("+55 11 99999-9999");
        sms.notificar("Pedido Enviado!");
    }
}
