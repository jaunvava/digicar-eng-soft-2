# Exemplos de padroes de projeto

Este projeto apresenta versoes simples, em Java, de dois padroes de projeto.
Cada exemplo possui uma pasta `sem`, para mostrar o problema, e uma pasta `com`,
para mostrar a aplicacao do padrao.

## Singleton

O Singleton garante que exista somente uma instancia de `Configuracao` em toda a
aplicacao. O construtor e privado e o acesso acontece por meio de
`Configuracao.getInstance()`.

Na versao sem o padrao, cada `new Configuracao()` cria um objeto independente.
Na versao com o padrao, as duas variaveis apontam para o mesmo objeto e, por isso,
enxergam o mesmo tema.

## Adapter

O Adapter permite que classes com interfaces diferentes trabalhem juntas. O
sistema espera o metodo `pagar`, definido por `PagamentoInterface`, mas o servico
externo disponibiliza `realizarPagamento`.

`PagamentoAdapter` implementa a interface esperada pelo sistema e traduz a chamada
para o metodo oferecido por `PagamentoExterno`.

## Como executar

A partir da pasta `src`, compile os exemplos:

```powershell
javac -d out (rg --files -g '*.java')
```

Execute cada versao:

```powershell
java -cp out singleton.sem.Main
java -cp out singleton.com.Main
java -cp out adapter.sem.Main
java -cp out adapter.com.Main
```
