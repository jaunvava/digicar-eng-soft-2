package pagamentos.app;

import java.math.BigDecimal;
import java.nio.charset.Charset;
import java.util.Scanner;
import java.util.function.Predicate;

import pagamentos.util.Moeda;

/**
 * Leitura de dados do terminal, repetindo a pergunta até o usuário digitar algo válido.
 */
public class Terminal {

    // Usa a codificação do console (ex.: cp850 no Windows) para ler acentos corretamente.
    private final Scanner scanner = new Scanner(System.in,
            System.console() != null ? System.console().charset() : Charset.defaultCharset());

    public String lerTexto(String rotulo, Predicate<String> valido, String mensagemErro) {
        while (true) {
            System.out.print(rotulo);
            String entrada = scanner.nextLine().trim();
            if (valido.test(entrada)) {
                return entrada;
            }
            System.out.println("  ! " + mensagemErro);
        }
    }

    public String lerTextoObrigatorio(String rotulo) {
        return lerTexto(rotulo, texto -> !texto.isBlank(), "Este campo é obrigatório.");
    }

    public int lerInteiro(String rotulo, int minimo, int maximo) {
        while (true) {
            System.out.print(rotulo);
            String entrada = scanner.nextLine().trim();
            try {
                int numero = Integer.parseInt(entrada);
                if (numero >= minimo && numero <= maximo) {
                    return numero;
                }
            } catch (NumberFormatException ignorada) {
                // cai na mensagem de erro abaixo
            }
            System.out.println("  ! Digite um número entre " + minimo + " e " + maximo + ".");
        }
    }

    public BigDecimal lerValor(String rotulo) {
        while (true) {
            System.out.print(rotulo);
            String entrada = scanner.nextLine();
            try {
                BigDecimal valor = Moeda.interpretar(entrada);
                if (valor.signum() > 0) {
                    return valor;
                }
                System.out.println("  ! O valor deve ser maior que zero.");
            } catch (NumberFormatException | ArithmeticException e) {
                System.out.println("  ! Valor inválido. Exemplos: 150 | 150,75 | 1.500,00");
            }
        }
    }

    public boolean confirmar(String pergunta) {
        String resposta = lerTexto(pergunta + " (S/N): ",
                texto -> texto.equalsIgnoreCase("S") || texto.equalsIgnoreCase("N"),
                "Responda S ou N.");
        return resposta.equalsIgnoreCase("S");
    }
}
