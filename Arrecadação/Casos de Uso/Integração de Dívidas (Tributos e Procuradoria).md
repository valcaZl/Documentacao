# Documentação do Script de Integração de Dívidas (Tributos e Procuradoria)

Este script Groovy demonstra como buscar e correlacionar dados de dívidas entre os módulos de **Tributos** e **Procuradoria**. Ele é útil para verificar a consistência dos dados ou para obter informações complementares de dívidas que podem estar registradas em ambos os sistemas.

## Explicação Geral do Código

O script inicia buscando um conjunto de dívidas do módulo de Tributos. Para cada dívida encontrada neste módulo, ele tenta localizar a dívida correspondente no módulo de Procuradoria, utilizando um identificador comum (`codigo` do Tributos vs. `idUnico` da Procuradoria). O objetivo principal é demonstrar a integração e a busca cruzada de informações de dívidas entre esses dois módulos.

## Blocos de Código

### 1. Busca de Dívidas no Módulo de Tributos

```groovy
fonteDividas = Dados.tributos.v2.dividas;

dadosDividas = fonteDividas.busca().take(100)
```

Este bloco define a fonte de dados para dívidas no módulo de Tributos (`Dados.tributos.v2.dividas`). Em seguida, ele realiza uma busca para obter os primeiros 100 registros de dívidas deste módulo. Estes serão os registros base para a correlação.

### 2. Correlação e Busca de Dívidas no Módulo de Procuradoria

```groovy
percorrer (dadosDividas) { itemDividas ->
  
  fonteDividasProc = Dados.procuradoria.v2.dividas;
  
  filtroDividasProc = "idUnico = ${itemDividas.codigo}"
  
  dadosDividasProc = fonteDividasProc.buscar(criterio: filtroDividasProc)
  
  percorrer (dadosDividasProc) { itemDividasProc ->
    imprimir itemDividasProc
  } 
}
```

Este é o bloco central de integração. Ele itera sobre cada `itemDividas` obtido do módulo de Tributos. Para cada um:

*   Define a fonte de dados para dívidas no módulo de Procuradoria (`Dados.procuradoria.v2.dividas`).
*   Cria um `filtroDividasProc` usando o `codigo` da dívida do módulo de Tributos (`itemDividas.codigo`) como o `idUnico` para buscar a dívida correspondente no módulo de Procuradoria. Isso assume que o `codigo` em Tributos corresponde ao `idUnico` em Procuradoria.
*   Realiza a busca (`fonteDividasProc.buscar`) no módulo de Procuradoria com base nesse filtro.
*   Finalmente, itera sobre os resultados (`dadosDividasProc`) e imprime cada `itemDividasProc` encontrado, demonstrando a correlação entre os dois módulos.

## Código Completo

```groovy
fonteDividas = Dados.tributos.v2.dividas;

dadosDividas = fonteDividas.busca().take(100)

percorrer (dadosDividas) { itemDividas ->
  
  fonteDividasProc = Dados.procuradoria.v2.dividas;
  
  filtroDividasProc = "idUnico = ${itemDividas.codigo}"
  
  dadosDividasProc = fonteDividasProc.buscar(criterio: filtroDividasProc)
  
  percorrer (dadosDividasProc) { itemDividasProc ->
    imprimir itemDividasProc
  } 
}
```

