package pagamentos.app;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Path;
import java.util.List;
import java.util.NoSuchElementException;

import pagamentos.estrategia.EstrategiaPagamento;
import pagamentos.estrategia.PagamentoCartaoCredito;
import pagamentos.estrategia.PagamentoPix;
import pagamentos.estrategia.ProcessadorPagamento;
import pagamentos.modelo.Transacao;
import pagamentos.relatorio.GeradorRelatorio;
import pagamentos.relatorio.RelatorioCSV;
import pagamentos.relatorio.RelatorioHTML;
import pagamentos.relatorio.RelatorioJSON;
import pagamentos.repositorio.RepositorioTransacoes;
import pagamentos.util.Moeda;

public class Main {

    private static final Path PASTA_RELATORIOS = Path.of("relatorios");

    private final Terminal terminal = new Terminal();
    private final RepositorioTransacoes repositorio = new RepositorioTransacoes();
    private final ProcessadorPagamento processador = new ProcessadorPagamento(repositorio);

    public static void main(String[] args) {
        try {
            new Main().executar();
        } catch (NoSuchElementException e) {
            System.out.println("\nEntrada encerrada. Até logo!");
        }
    }

    private void executar() {
        System.out.println("==========================================");
        System.out.println("       SISTEMA DE PAGAMENTOS - v1.0       ");
        System.out.println("==========================================");

        while (true) {
            System.out.println();
            System.out.println("--------------- MENU ---------------");
            System.out.println("1 - Realizar pagamento");
            System.out.println("2 - Listar transações");
            System.out.println("3 - Gerar relatório");
            System.out.println("0 - Sair");
            int opcao = terminal.lerInteiro("Escolha uma opção: ", 0, 3);

            switch (opcao) {
                case 1 -> realizarPagamento();
                case 2 -> listarTransacoes();
                case 3 -> gerarRelatorio();
                case 0 -> {
                    encerrar();
                    return;
                }
            }
        }
    }

    // ---------------------------------------------------------------- Pagamento

    private void realizarPagamento() {
        System.out.println();
        System.out.println("=== NOVO PAGAMENTO ===");
        System.out.println("Forma de pagamento:");
        System.out.println("1 - Pix");
        System.out.println("2 - Cartão de crédito");
        int forma = terminal.lerInteiro("Escolha: ", 1, 2);

        BigDecimal valor = terminal.lerValor("Valor da transação (R$): ");

        EstrategiaPagamento estrategia = (forma == 1) ? lerDadosPix() : lerDadosCartao();

        // Strategy: o processador recebe a estratégia escolhida e a executa sem conhecer os detalhes.
        processador.setEstrategia(estrategia);
        System.out.println();
        System.out.println("Processando pagamento via " + estrategia.getNome() + "...");
        Transacao transacao = processador.processar(valor);

        System.out.println();
        System.out.println("[OK] Pagamento aprovado!");
        System.out.println("  ID ......: " + transacao.id());
        System.out.println("  Valor ...: " + Moeda.formatar(transacao.valor()));
        System.out.println("  Taxa ....: " + Moeda.formatar(transacao.taxa()));
        System.out.println("  Total ...: " + Moeda.formatar(transacao.total()));
        System.out.println("  Detalhes : " + transacao.detalhes());
    }

    private EstrategiaPagamento lerDadosPix() {
        String chave = terminal.lerTexto(
                "Chave Pix do recebedor (CPF, CNPJ, e-mail, +55telefone ou aleatória): ",
                PagamentoPix::chaveValida,
                "Chave Pix inválida.");
        return new PagamentoPix(chave);
    }

    private EstrategiaPagamento lerDadosCartao() {
        String numero = terminal.lerTexto("Número do cartão: ",
                PagamentoCartaoCredito::numeroValido,
                "Número de cartão inválido (verifique os dígitos).");
        String titular = terminal.lerTextoObrigatorio("Nome do titular (como no cartão): ");
        String validade = terminal.lerTexto("Validade (MM/AA): ",
                PagamentoCartaoCredito::validadeValida,
                "Validade inválida ou cartão vencido. Use o formato MM/AA.");
        String cvv = terminal.lerTexto("CVV: ",
                PagamentoCartaoCredito::cvvValido,
                "O CVV deve ter 3 ou 4 dígitos.");
        int parcelas = terminal.lerInteiro(
                "Parcelas (1 a " + PagamentoCartaoCredito.MAX_PARCELAS + "): ",
                1, PagamentoCartaoCredito.MAX_PARCELAS);
        return new PagamentoCartaoCredito(numero, titular, validade, cvv, parcelas);
    }

    // ---------------------------------------------------------------- Listagem

    private void listarTransacoes() {
        System.out.println();
        if (repositorio.estaVazio()) {
            System.out.println("Nenhuma transação registrada ainda.");
            return;
        }
        System.out.println("=== TRANSAÇÕES REGISTRADAS ===");
        System.out.printf("%-12s %-20s %15s %12s %15s%n", "ID", "Método", "Valor", "Taxa", "Total");
        for (Transacao t : repositorio.listarTodas()) {
            System.out.printf("%-12s %-20s %15s %12s %15s%n",
                    t.id(), t.metodo(),
                    Moeda.formatar(t.valor()), Moeda.formatar(t.taxa()), Moeda.formatar(t.total()));
        }
    }

    // ---------------------------------------------------------------- Relatórios

    private void gerarRelatorio() {
        System.out.println();
        if (repositorio.estaVazio()) {
            System.out.println("Nenhuma transação registrada. Realize um pagamento antes de gerar relatórios.");
            return;
        }
        System.out.println("=== GERAR RELATÓRIO ===");
        System.out.println("1 - CSV");
        System.out.println("2 - HTML");
        System.out.println("3 - JSON");
        System.out.println("4 - Todos os formatos");
        System.out.println("0 - Voltar");
        int formato = terminal.lerInteiro("Escolha o formato: ", 0, 4);

        List<GeradorRelatorio> geradores = switch (formato) {
            case 1 -> List.of(new RelatorioCSV());
            case 2 -> List.of(new RelatorioHTML());
            case 3 -> List.of(new RelatorioJSON());
            case 4 -> List.of(new RelatorioCSV(), new RelatorioHTML(), new RelatorioJSON());
            default -> List.of();
        };

        for (GeradorRelatorio gerador : geradores) {
            try {
                // Template Method: todos os formatos seguem o mesmo algoritmo definido em gerar().
                Path arquivo = gerador.gerar(repositorio.listarTodas(), PASTA_RELATORIOS);
                System.out.println("[OK] Relatório " + gerador.extensao().toUpperCase()
                        + " gerado em: " + arquivo.toAbsolutePath());
            } catch (IOException e) {
                System.out.println("  ! Erro ao salvar o relatório: " + e.getMessage());
            }
        }
    }

    private void encerrar() {
        if (!repositorio.estaVazio() && terminal.confirmar("\nDeseja gerar um relatório antes de sair?")) {
            gerarRelatorio();
        }
        System.out.println("\nSistema encerrado. Até logo!");
    }
}
