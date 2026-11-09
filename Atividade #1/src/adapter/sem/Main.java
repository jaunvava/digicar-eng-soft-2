package adapter.sem;

public class Main {

    public static void main(String[] args) {
        PagamentoService pagamentoService = new PagamentoService();

        pagamentoService.pagar(500.00);
    }

}
