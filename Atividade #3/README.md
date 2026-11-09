# Sistema de Pagamentos — Strategy + Template Method

Sistema em Java (terminal) para registrar pagamentos via **Pix** ou **cartão de crédito** e gerar
relatórios das transações nos formatos **CSV**, **HTML** e **JSON**.

## Estrutura do projeto

```
AULA-3/
├── src/pagamentos/
│   ├── app/
│   │   ├── Main.java                  # Menu e fluxo pelo terminal
│   │   └── Terminal.java              # Leitura e validação da entrada do usuário
│   ├── estrategia/                    # ── Padrão STRATEGY ──
│   │   ├── EstrategiaPagamento.java   # Interface (Strategy)
│   │   ├── PagamentoPix.java          # Estratégia concreta
│   │   ├── PagamentoCartaoCredito.java# Estratégia concreta
│   │   └── ProcessadorPagamento.java  # Contexto
│   ├── relatorio/                     # ── Padrão TEMPLATE METHOD ──
│   │   ├── GeradorRelatorio.java      # Classe abstrata com o método-template gerar()
│   │   ├── RelatorioCSV.java          # Subclasse concreta
│   │   ├── RelatorioHTML.java         # Subclasse concreta
│   │   ├── RelatorioJSON.java         # Subclasse concreta
│   │   └── ResumoTransacoes.java      # Totais usados no rodapé
│   ├── modelo/Transacao.java          # Dados de uma transação (record)
│   ├── repositorio/RepositorioTransacoes.java  # Armazenamento em memória
│   └── util/Moeda.java                # Formatação/leitura de valores em R$
├── demo/entrada-demo.txt              # Roteiro de entradas para demonstração automática
├── relatorios/                        # Arquivos gerados (.csv, .html, .json)
├── executar.bat                       # Compila e executa (Windows)
└── executar.sh                        # Compila e executa (Linux/macOS/Git Bash)
```

## Como executar

Requisito: **JDK 21** ou superior.

- **Windows:** dê dois cliques em `executar.bat` (ou rode no terminal).
- **Linux/macOS/Git Bash:** `./executar.sh`
- **Manualmente:**
  ```bash
  javac -encoding UTF-8 -d out $(find src -name "*.java")
  java -cp out pagamentos.app.Main
  ```
- **Demonstração automática** (faz 3 pagamentos, inclusive com entradas inválidas, e gera os 3 relatórios):
  ```bash
  java -cp out pagamentos.app.Main < demo/entrada-demo.txt
  ```

Os relatórios são salvos na pasta `relatorios/` com o nome `relatorio_transacoes_AAAAMMDD_HHMMSS.<extensão>`.

## Padrões de projeto

### Strategy (formas de pagamento)

```
            ┌─────────────────────────┐
            │  «interface»            │
            │  EstrategiaPagamento    │◄────── ProcessadorPagamento (contexto)
            │  + getNome()            │          setEstrategia(e)
            │  + pagar(valor)         │          processar(valor)
            └──────────▲──────────────┘
                       │
         ┌─────────────┴──────────────┐
  PagamentoPix               PagamentoCartaoCredito
  - sem taxa                 - 2,99% à vista + 1,49% por parcela adicional
  - valida chave Pix         - valida número (Luhn), validade, CVV e parcelas
```

O `ProcessadorPagamento` não sabe qual forma de pagamento está usando; ele apenas chama
`estrategia.pagar(valor)`. Para criar uma nova forma (ex.: boleto) basta criar outra classe
que implemente `EstrategiaPagamento`, sem alterar o processador.

### Template Method (relatórios)

`GeradorRelatorio.gerar()` é **final** e define o algoritmo fixo:

1. `validar()` — garante que existem transações *(comum)*
2. `cabecalho()` — *(abstrato)*
3. `linha()` para cada transação, com `separadorEntreLinhas()` entre elas *(abstrato + hook)*
4. `rodape()` com o resumo/totais *(abstrato)*
5. `salvar()` — grava o arquivo com a `extensao()` correta *(comum)*

| Etapa        | CSV                         | HTML                       | JSON                          |
|--------------|-----------------------------|----------------------------|-------------------------------|
| cabeçalho    | linha de colunas (`;`)      | `<html>`, CSS, `<thead>`   | `{ "geradoEm", "transacoes": [` |
| linha        | campos separados por `;`    | `<tr>…</tr>`               | objeto `{ … }`                |
| separador (hook) | padrão (vazio)          | padrão (vazio)             | **sobrescrito**: `,`          |
| rodapé       | linha `TOTAL`               | `<tfoot>` e fechamento     | `], "resumo": { … } }`        |

## Dados para teste

| Campo              | Exemplo válido                                  |
|--------------------|-------------------------------------------------|
| Chave Pix          | `joao@email.com`, `123.456.789-09`, `+5511999998888` |
| Número do cartão   | `4111 1111 1111 1111` (número de teste Visa)    |
| Validade           | `12/30`                                         |
| CVV                | `123`                                           |
| Valor              | `150`, `150,75` ou `1.500,00`                   |
