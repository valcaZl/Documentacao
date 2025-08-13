# Documentação do Script de Busca de Imóveis e Campos Adicionais

Este script Groovy é responsável por buscar imóveis com situação 'ATIVADO' e, para cada um deles, buscar seus campos adicionais. Ele utiliza a API de Tributos para obter os dados dos imóveis e dos campos adicionais.

## Explicação Geral do Código

O script inicia buscando até 1000 imóveis que estão com a situação 'ATIVADO'. Ele armazena o `id` do imóvel, o nome do `responsavel` e o `codigoImovel` em um mapa (`mapImoveis`). Em seguida, ele itera sobre as chaves (IDs dos imóveis) desse mapa em lotes de 500. Para cada lote, ele busca os campos adicionais relacionados a esses imóveis e os imprime. Este script é útil para inspecionar dados adicionais associados a imóveis ativos no sistema.

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

Este bloco define a fonte de dados para imóveis (`Dados.tributos.v2.imoveis`) e um filtro para buscar apenas imóveis com a situação 'ATIVADO'. Ele busca até 1000 desses imóveis e popula o `mapImoveis` com o ID do imóvel como chave e um mapa contendo o nome do responsável e o código do imóvel como valor. Isso cria uma estrutura de dados para referência rápida aos imóveis e seus responsáveis.

### 2. Busca de Campos Adicionais por Lote

```groovy
mapImoveis.keySet().collate(500).each { key ->
  //imprimir key
  //imprimir value
  
  fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;
  
  filtroCamposAdicionais = "idImovel in (${key.join(',')})"
  imprimir filtroCamposAdicionais
  
  dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais)
  
  percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
    imprimir itemCamposAdicionais
  }
}
```

Este bloco itera sobre as chaves (IDs dos imóveis) do `mapImoveis` em lotes de 500. Para cada lote, ele define a fonte de dados para campos adicionais (`Dados.tributos.v2.imoveis.camposAdicionais`) e constrói um filtro para buscar campos adicionais associados aos IDs de imóveis no lote atual. O filtro é impresso para depuração. Em seguida, ele busca os `dadosCamposAdicionais` e itera sobre eles, imprimindo cada `itemCamposAdicionais`. Isso permite processar um grande número de imóveis de forma eficiente, buscando seus campos adicionais em grupos menores.

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
  imprimir filtroCamposAdicionais
  
  dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais)
  
  percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
    imprimir itemCamposAdicionais
  }
}
```

