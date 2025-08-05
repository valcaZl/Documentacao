# Documentação da Função `formatUtils`

Esta função Groovy é responsável por formatar strings de entrada, aplicando máscaras específicas com base no tipo de dado fornecido. Ela pode formatar números de CPF/CNPJ, CEPs e números de telefone.

## Lógica Geral da Função

A função `formatUtils` recebe dois parâmetros:

*   `tipo`: Uma String que indica o tipo de máscara a ser aplicada. Os valores aceitos são "CPFCNPJ", "CEP" e "TELEFONE".
*   `campo`: A String a ser formatada.

Com base no `tipo` fornecido, a função utiliza expressões regulares para aplicar a máscara correspondente ao `campo` e retorna a string formatada.

### Tipos de Formatação Suportados:

*   **CPF/CNPJ**: Se o campo tiver 11 dígitos (CPF), a máscara "XXX.XXX.XXX-XX" é aplicada. Se tiver 14 dígitos (CNPJ), a máscara "XX.XXX.XXX/XXXX-XX" é aplicada.
*   **CEP**: A máscara "XXXXX-XXX" é aplicada.
*   **TELEFONE**: Se o campo tiver 11 dígitos (com DDD e 9º dígito), a máscara "(XX) XXXXX-XXXX" é aplicada. Se tiver 10 dígitos (com DDD, sem 9º dígito), a máscara "(XX) XXXX-XXXX" é aplicada.

## Exemplo de Uso

```groovy
formatUtils("CPFCNPJ","12332112332112");
//└> retorno -> "12.332.112/3321-12"
formatUtils("CPFCNPJ","123321123321");
//└> retorno -> "123.321.123-31"
formatUtils("CEP","77741526");
//└> retorno -> "77741-526"
formatUtils("TELEFONE","48998567382");
//└> retorno -> "(48) 99856-7382"
formatUtils("TELEFONE","4899856738");
//└> retorno -> "(48) 9985-6738"
```

## Estrutura Interna do Código

```groovy
/*
Recebe o tipo, e o campo.
Com base no tipo, realiza a aplicação da máscara e retorna.
 */
def String formatUtils(String tipo, String campo) {
    //tipo: String relacionado ao tipo:
    //      └> "CPFCNPJ", "CEP", "TELEFONE"
    //campo: Campo a ser aplicado a máscara
    String campoFormatado = campo;

    if (tipo == "CPFCNPJ") {
        if(campo.trim().size() == 11) {
            campoFormatado = campo.trim().take(11).replaceAll(/(\d{3})(\d{3})(\d{3})(\d{2})/) { match ->
                "${match[1]}.${match[2]}.${match[3]}-${match[4]}"
            }
        } else if (campo.trim().size() == 14) {
            campoFormatado = campo.trim().take(14).replaceAll(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/) { match ->
                "${match[1]}.${match[2]}.${match[3]}/${match[4]}-${match[5]}"
            }
        }
    } else if (tipo == "CEP") {
        campoFormatado = campo.trim().replaceAll(/(\d{5})(\d{3})/) { match ->
            "${match[1]}-${match[2]}"
        }
    } else if (tipo == "TELEFONE") {
        if (campo.trim().size() == 11) {
            campoFormatado = campo.trim().replaceAll(/(\d{2})(\d{5})(\d{4})/) { match ->
                "(${match[1]}) ${match[2]}-${match[3]}"
            }
        } else if (campo.trim().size() == 10) {
            campoFormatado = campo.trim().replaceAll(/(\d{2})(\d{4})(\d{4})/) { match ->
                "(${match[1]}) ${match[2]}-${match[3]}"
            }
        }
    }
    return campoFormatado
}
```

