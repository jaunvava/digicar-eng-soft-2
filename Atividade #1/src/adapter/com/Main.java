package adapter.com;

public class Main {

    public static void main(String[] args) {

        PagamentoExterno pagamentoExterno = new PagamentoExterno();
        PagamentoInterface pagamentoInterface = new PagamentoAdapter(pagamentoExterno);

        // O sistema usa pagar(), enquanto o servico externo oferece realizarPagamento().
        pagamentoInterface.pagar(500.00);
    }

}
