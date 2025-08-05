# Documentação da Função `formatValor`

Esta função Groovy é responsável por formatar valores monetários (BigDecimal) para o formato de moeda brasileira (R$ X.XXX,XX).

## Lógica Geral da Função

A função `formatValor` recebe um parâmetro:

*   `valorInicial`: Um BigDecimal com o valor numérico a ser formatado.

A função realiza os seguintes passos:

1.  Formata o `valorInicial` para duas casas decimais, substituindo o ponto decimal por vírgula.
2.  Divide o valor em parte inteira e parte decimal.
3.  Inverte a parte inteira para facilitar a inserção dos pontos de milhar.
4.  Aplica a máscara de pontos de milhar na parte inteira invertida.
5.  Remove um ponto inicial extra, se houver.
6.  Concatena o prefixo "R$", a parte inteira formatada e a parte decimal para formar o valor final.

## Exemplo de Uso

```groovy
formatValor(120312.13);
//└> retorno -> "R$120.312,13"
formatValor(1234.56);
//└> retorno -> "R$1.234,56"
formatValor(99.99);
//└> retorno -> "R$99,99"
```

## Estrutura Interna do Código

```groovy
/*
Recebe um BigDecimal, e retorna o valor formatado
 */
def String formatValor(BigDecimal valorInicial) {
    //valorInicial: BigDecimal com o valor a ser formatado
    def valor = String.format("%.2f", valorInicial).replace('.', ',')

    def partes = valor.split(',')
    def parteInteira = partes[0]
    def parteDecimal = partes[1]
    def parteInteiraInvertida = parteInteira.reverse()
    def parteInteiraComPontos = parteInteiraInvertida.replaceAll(/(\d{3})/, '$1.').reverse()

    if (parteInteiraComPontos.startsWith('.')) {
        parteInteiraComPontos = parteInteiraComPontos.substring(1)
    }

    def valorFormatado = "R\$${parteInteiraComPontos},${parteDecimal}"
    return valorFormatado
}
```

