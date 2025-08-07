# Documentação do Script de Processamento de Inscrições Imobiliárias

Este script Groovy tem como objetivo principal coletar inscrições imobiliárias de uma fonte de dados, adicionar valores específicos e, em seguida, identificar e exibir quaisquer valores repetidos dentro da lista resultante.

## Explicação Geral do Código

O script começa inicializando uma lista vazia para armazenar as inscrições imobiliárias. Ele então busca as 20 primeiras inscrições imobiliárias formatadas de uma fonte de dados de imóveis e as adiciona a essa lista. Em seguida, dois valores de inscrição imobiliária são adicionados manualmente à lista. Finalmente, o script processa essa lista para encontrar e isolar quaisquer valores que apareçam mais de uma vez, imprimindo tanto a lista completa quanto os valores repetidos.

## Blocos de Código

### Inicialização e Busca de Dados de Imóveis

```groovy
listaValores = []

fonteImoveis = Dados.tributos.v2.imoveis;
dadosImoveis = fonteImoveis.busca(campos: "inscricaoImobiliariaFormatada, inscricaoAnterior, inscricaoIncra, codigo, id").take(20)
percorrer (dadosImoveis) { itemImoveis ->
  listaValores << itemImoveis.inscricaoImobiliariaFormatada
}
```

Neste bloco:

*   `listaValores = []`: Uma lista vazia é criada para armazenar as inscrições imobiliárias.
*   `fonteImoveis = Dados.tributos.v2.imoveis;`: Define a fonte de dados para imóveis, presumivelmente um serviço ou API que fornece dados de imóveis.
*   `dadosImoveis = fonteImoveis.busca(...).take(20)`: Busca os primeiros 20 registros de imóveis da fonte, selecionando campos específicos como `inscricaoImobiliariaFormatada`.
*   `percorrer (dadosImoveis) { ... }`: Itera sobre os imóveis encontrados e adiciona o valor de `inscricaoImobiliariaFormatada` de cada item à `listaValores`.

### Adição de Valores Manuais

```groovy
listaValores << '02.04.121.0281.1'
listaValores << '02.02.025.0421.112'
```

Duas inscrições imobiliárias são adicionadas manualmente à `listaValores`. Isso pode ser útil para testes ou para incluir dados que não vêm diretamente da fonte de dados.

### Identificação de Valores Repetidos

```groovy
def repetidos = listaValores.groupBy { it }
                     .findAll { it.value.size() > 1 }
                     .values()
                     .flatten()
```

Este bloco de código é responsável por encontrar os valores duplicados na `listaValores`:

*   `listaValores.groupBy { it }`: Agrupa os elementos da lista, criando um mapa onde as chaves são os valores únicos e os valores são listas de todas as ocorrências desses valores na lista original.
*   `.findAll { it.value.size() > 1 }`: Filtra os grupos, mantendo apenas aqueles cujas listas de ocorrências (`it.value`) têm mais de um elemento, ou seja, os valores que são repetidos.
*   `.values()`: Retorna uma coleção das listas de ocorrências dos valores repetidos.
*   `.flatten()`: Transforma a coleção de listas em uma única lista, contendo todos os valores repetidos (incluindo suas duplicatas).

### Impressão dos Resultados

```groovy
imprimir listaValores
imprimir repetidos
```

Finalmente, o script imprime no console:

*   A `listaValores` completa, incluindo todos os valores coletados e adicionados.
*   A lista `repetidos`, contendo apenas os valores que foram encontrados mais de uma vez.

## Código Completo

```groovy
listaValores = []

fonteImoveis = Dados.tributos.v2.imoveis;
dadosImoveis = fonteImoveis.busca(campos: "inscricaoImobiliariaFormatada, inscricaoAnterior, inscricaoIncra, codigo, id").take(20)
percorrer (dadosImoveis) { itemImoveis ->
  listaValores << itemImoveis.inscricaoImobiliariaFormatada
}

listaValores << '02.04.121.0281.1'
listaValores << '02.02.025.0421.112'

def repetidos = listaValores.groupBy { it }
                     .findAll { it.value.size() > 1 }
                     .values()
                     .flatten()

imprimir listaValores
imprimir repetidos
```

