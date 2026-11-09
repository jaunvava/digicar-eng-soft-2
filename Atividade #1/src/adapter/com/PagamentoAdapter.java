package adapter.com;

public class PagamentoAdapter implements PagamentoInterface {

    private final PagamentoExterno pagamentoExterno;

    public PagamentoAdapter(PagamentoExterno pagamentoExterno){
        this.pagamentoExterno = pagamentoExterno;
    }

    @Override
    public void pagar(double valor) {
        pagamentoExterno.realizarPagamento(valor);
    }
}
