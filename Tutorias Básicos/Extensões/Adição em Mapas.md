# Documentação do Script de Busca de Imóveis e Campos Adicionais (Com Enriquecimento de Dados)

Este script Groovy é projetado para buscar imóveis com situação 'ATIVADO', coletar suas informações básicas e, em seguida, enriquecer esses dados com informações de campos adicionais, que são anexadas diretamente ao objeto do imóvel no mapa principal. Ele utiliza a API de Tributos para obter os dados dos imóveis e dos campos adicionais.

## Explicação Geral do Código

O script começa buscando até 1000 imóveis ativos e os armazena em um mapa (`mapImoveis`), onde a chave é o ID do imóvel e o valor é um mapa contendo o responsável e o código do imóvel. Em seguida, ele itera sobre as chaves (IDs dos imóveis) desse mapa em lotes. Para cada lote, ele busca os campos adicionais correspondentes e, crucialmente, **adiciona esses campos adicionais como uma nova propriedade a cada objeto de imóvel já existente no `mapImoveis`**. Finalmente, ele itera sobre o `mapImoveis` enriquecido e imprime o conteúdo dos campos adicionais para cada imóvel.

## Blocos de Código

### 1. Busca Inicial de Imóveis Ativos

```groovy
fonteImoveis = Dados.tributos.v2.imoveis;

filtroImoveis = "situacao = 'ATIVADO'"

mapImoveis = [:]

dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis).take(1000)

percorrer (dadosImoveis) { itemImoveis ->
  
  chave = itemImoveis.id
  
  mapImoveis[chave] = [
    responsavel: itemImoveis.responsavel.nome,
    codigoImovel: itemImoveis.codigo
  ]
}
```

Este bloco inicializa a fonte de dados para imóveis (`Dados.tributos.v2.imoveis`) e define um filtro para buscar imóveis com a situação 'ATIVADO'. Ele busca até 1000 desses imóveis e popula o `mapImoveis`. Cada entrada no `mapImoveis` tem o ID do imóvel como chave e um mapa contendo o nome do responsável e o código do imóvel como valor. Neste ponto, o `mapImoveis` contém apenas as informações básicas dos imóveis.

### 2. Busca e Enriquecimento com Campos Adicionais

```groovy
mapImoveis.keySet().collate(500).each { key ->
  
  fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;
  
  filtroCamposAdicionais = "idImovel in (${key.join(',')})"
  
  dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais)
  
  percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
    idImovel = itemCamposAdicionais.idImovel
    mapImoveis[idImovel].itemCamposAdicionais = itemCamposAdicionais
  }
}
```

Este é o bloco central para o enriquecimento dos dados. Ele itera sobre as chaves (IDs dos imóveis) do `mapImoveis` em lotes de 500 para otimizar as chamadas à API. Para cada lote, ele busca os `camposAdicionais` associados a esses IDs. A parte mais importante é dentro do segundo `percorrer`:

*   `idImovel = itemCamposAdicionais.idImovel`: Obtém o ID do imóvel ao qual o `itemCamposAdicionais` pertence.
*   `mapImoveis[idImovel].itemCamposAdicionais = itemCamposAdicionais`: Esta linha acessa o objeto do imóvel já existente no `mapImoveis` (usando `mapImoveis[idImovel]`) e adiciona uma nova propriedade chamada `itemCamposAdicionais` a ele. O valor dessa nova propriedade é o objeto completo `itemCamposAdicionais` retornado da busca. Dessa forma, cada objeto de imóvel no `mapImoveis` é dinamicamente enriquecido com seus dados adicionais.

### 3. Impressão dos Dados Enriquecidos

```groovy
mapImoveis.each{ key, value ->
  imprimir value.itemCamposAdicionais
}
```

Este bloco final itera sobre o `mapImoveis` já enriquecido. Para cada entrada, ele acessa a propriedade `itemCamposAdicionais` (que foi adicionada no passo anterior) e imprime seu conteúdo. Isso demonstra que os dados dos campos adicionais foram efetivamente associados a cada imóvel no mapa.

## Código Completo

```groovy
fonteImoveis = Dados.tributos.v2.imoveis;

filtroImoveis = "situacao = 'ATIVADO'"

mapImoveis = [:]

dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis).take(1000)

percorrer (dadosImoveis) { itemImoveis ->
  
  chave = itemImoveis.id
  
  mapImoveis[chave] = [
    responsavel: itemImoveis.responsavel.nome,
    codigoImovel: itemImoveis.codigo
  ]
}

mapImoveis.keySet().collate(500).each { key ->
  //imprimir key
  //imprimir value
  
  fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;
  
  filtroCamposAdicionais = "idImovel in (${key.join(',')})"
  //imprimir filtroCamposAdicionais
  
  dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais)
  
  percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
    idImovel = itemCamposAdicionais.idImovel
    mapImoveis[idImovel].itemCamposAdicionais = itemCamposAdicionais
  }
}

mapImoveis.each{ key, value ->
  imprimir value.itemCamposAdicionais
}
```

