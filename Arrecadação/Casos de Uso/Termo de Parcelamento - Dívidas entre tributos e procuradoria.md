# Documentação do Script de Rastreamento de Termo de Parcelamento para Execução Fiscal

Este script Groovy tem como objetivo rastrear a relação entre um termo de parcelamento, suas dívidas componentes e as execuções fiscais associadas a essas dívidas. Ele navega por diferentes fontes de dados para correlacionar informações tributárias e de procuradoria.

## Explicação Geral do Código

O script começa buscando um termo de parcelamento específico usando o número do parcelamento e o número do documento. Para cada termo de parcelamento encontrado (neste caso, um único termo é esperado, dado os parâmetros de busca), ele itera sobre a composição desse parcelamento. Cada item da composição está ligado a uma dívida. Para cada dívida, o script busca a execução fiscal correspondente e, em seguida, os detalhes dessa execução fiscal. Em resumo, ele estabelece uma ligação entre um parcelamento e as execuções fiscais relacionadas às dívidas que compõem esse parcelamento.

## Blocos de Código

### 1. Busca do Termo de Parcelamento

```groovy
Dados.tributos.v2.termoParcelamento.busca(parametros:["nroParcelamento":1632848,"nroDocumento":298]).each{ itemTermoParcelamento ->
  // ... código aninhado ...
}
```

Este é o ponto de entrada do script. Ele realiza uma busca na fonte de dados `Dados.tributos.v2.termoParcelamento` por um termo de parcelamento específico, utilizando os parâmetros `nroParcelamento` (número do parcelamento) e `nroDocumento` (número do documento). O `.each` indica que o script irá iterar sobre os resultados da busca, embora com esses parâmetros, um único resultado seja esperado.

### 2. Busca da Composição do Parcelamento

```groovy
Dados.tributos.v2.termoParcelamento.composicao.busca(parametros:["nroParcelamento":itemTermoParcelamento.nroParcelamento]).each{ itemComposicao ->
  // ... código aninhado ...
}
```

Aninhado ao primeiro laço, este bloco busca a composição do termo de parcelamento atualmente em iteração. A composição de um parcelamento detalha as dívidas que o compõem. O parâmetro `nroParcelamento` é usado para vincular a composição ao termo de parcelamento pai.

### 3. Busca da Dívida Associada

```groovy
Dados.procuradoria.v2.dividas.buscar(criterio: "idUnico = ${itemComposicao.divida.codigo}").each{ itemDividas ->
  // ... código aninhado ...
}
```

Para cada item da composição do parcelamento (`itemComposicao`), este bloco busca a dívida correspondente na fonte de dados `Dados.procuradoria.v2.dividas`. O `idUnico` da dívida é obtido a partir do `codigo` da dívida dentro do `itemComposicao`.

### 4. Busca da Execução Fiscal e Detalhes

```groovy
dividaExecucaoFiscal = Dados.procuradoria.v2.execucoesFiscaisDividas.buscar(criterio: "idDivida = ${itemDividas.id}",campos: "idExecucaoFiscal", primeiro:true)
execucaoFiscal = Dados.procuradoria.v2.execucoesFiscais.buscar(criterio: "id = ${dividaExecucaoFiscal.idExecucaoFiscal}", primeiro:true)
```

Este é o passo final do rastreamento. Para cada dívida (`itemDividas`), o script primeiro busca a ligação entre a dívida e a execução fiscal (`Dados.procuradoria.v2.execucoesFiscaisDividas`), obtendo o `idExecucaoFiscal`. Em seguida, usando esse ID, ele busca os detalhes completos da `execucaoFiscal` na fonte de dados `Dados.procuradoria.v2.execucoesFiscais`. O `primeiro:true` indica que apenas o primeiro resultado encontrado será retornado.

## Código Completo

```groovy
Dados.tributos.v2.termoParcelamento.busca(parametros:["nroParcelamento":1632848,"nroDocumento":298]).each{ itemTermoParcelamento ->
      Dados.tributos.v2.termoParcelamento.composicao.busca(parametros:["nroParcelamento":itemTermoParcelamento.nroParcelamento]).each{ itemComposicao ->
            Dados.procuradoria.v2.dividas.buscar(criterio: "idUnico = ${itemComposicao.divida.codigo}").each{ itemDividas ->
                 dividaExecucaoFiscal = Dados.procuradoria.v2.execucoesFiscaisDividas.buscar(criterio: "idDivida = ${itemDividas.id}",campos: "idExecucaoFiscal", primeiro:true)
                execucaoFiscal = Dados.procuradoria.v2.execucoesFiscais.buscar(criterio: "id = ${dividaExecucaoFiscal.idExecucaoFiscal}", primeiro:true)
            }
      }
}
```

