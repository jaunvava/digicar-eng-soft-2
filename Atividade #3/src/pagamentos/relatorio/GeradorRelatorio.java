package pagamentos.relatorio;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

import pagamentos.modelo.Transacao;

/**
 * Padrão Template Method: define o algoritmo fixo de geração de relatórios.
 * As subclasses (CSV, HTML, JSON) implementam apenas as etapas que mudam de formato para formato.
 */
public abstract class GeradorRelatorio {

    protected static final DateTimeFormatter FORMATO_DATA_HORA = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
    private static final DateTimeFormatter FORMATO_NOME_ARQUIVO = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");

    /**
     * Template Method. É final para que as subclasses não alterem a ordem das etapas:
     * validar -> cabeçalho -> linhas (com separador) -> rodapé -> salvar arquivo.
     */
    public final Path gerar(List<Transacao> transacoes, Path diretorio) throws IOException {
        validar(transacoes);
        LocalDateTime geradoEm = LocalDateTime.now();

        StringBuilder conteudo = new StringBuilder();
        conteudo.append(cabecalho(geradoEm));
        for (int i = 0; i < transacoes.size(); i++) {
            if (i > 0) {
                conteudo.append(separadorEntreLinhas());
            }
            conteudo.append(linha(transacoes.get(i)));
        }
        conteudo.append(rodape(ResumoTransacoes.de(transacoes)));

        return salvar(conteudo.toString(), diretorio, geradoEm);
    }

    // ---- Etapas abstratas: cada formato é obrigado a implementar ----

    public abstract String extensao();

    protected abstract String cabecalho(LocalDateTime geradoEm);

    protected abstract String linha(Transacao transacao);

    protected abstract String rodape(ResumoTransacoes resumo);

    // ---- Hook: etapa com comportamento padrão que pode ser sobrescrita ----

    protected String separadorEntreLinhas() {
        return "";
    }

    // ---- Etapas comuns a todos os formatos ----

    private void validar(List<Transacao> transacoes) {
        if (transacoes == null || transacoes.isEmpty()) {
            throw new IllegalStateException("Não há transações para gerar o relatório.");
        }
    }

    private Path salvar(String conteudo, Path diretorio, LocalDateTime geradoEm) throws IOException {
        Files.createDirectories(diretorio);
        String nomeArquivo = "relatorio_transacoes_" + geradoEm.format(FORMATO_NOME_ARQUIVO) + "." + extensao();
        Path arquivo = diretorio.resolve(nomeArquivo);
        Files.writeString(arquivo, conteudo, StandardCharsets.UTF_8);
        return arquivo;
    }
}
