package adapter.com;

public class PagamentoService implements PagamentoInterface {

    @Override
    public void pagar(double valor) {
        System.out.println("Pagamento de R$" + valor + " realizado.");
    }

}
