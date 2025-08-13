# Documentação do Script de Equivalências Contábeis (Geral)

Este script Groovy é responsável por buscar dados de equivalências contábeis e seus itens informados, organizando-os em uma estrutura JSON padronizada e exportando-os em arquivos de texto. O script processa equivalências específicas (VPDs) e gera arquivos em lotes de 50 registros para facilitar o processamento.

## Explicação Geral do Código

O script automatiza a extração e formatação de dados de equivalências contábeis do sistema. Ele busca equivalências com configuração específica (VPDs - Variações Patrimoniais Diminutivas), coleta os itens informados associados a cada equivalência e organiza essas informações em uma estrutura JSON padronizada. Os dados são então agrupados em lotes de 50 registros e exportados como arquivos de texto contendo JSON, facilitando a integração ou migração de dados entre sistemas. O script utiliza um contador para gerar IDs únicos de integração e mantém a estrutura hierárquica dos dados contábeis.

## Blocos de Código

### Busca de Equivalências Contábeis

```groovy
fonteEquivalencias = Dados.contabilidade.v1.equivalencias;
filtroEquivalencias = "configuracao.id = 9638 and configuracaoEquivalencia.id = 695860 and entidade.id = ${contextoExecucao.idEntidade} and configuracaoEquivalencia.descricao = \'VPDs\''"
dadosEquivalencias = fonteEquivalencias.busca(criterio: filtroEquivalencias,campos: "mascara, configuracao(descricao, id), configuracaoEquivalencia(descricao, id)")
count = 0
ListaPost = []
```

Este bloco inicial define a fonte de dados das equivalências contábeis e estabelece o filtro para buscar apenas equivalências específicas. O filtro busca por configuração ID 9638, configuração de equivalência ID 695860, da entidade atual e com descrição \'VPDs\' (Variações Patrimoniais Diminutivas). Também inicializa o contador e a lista que armazenará os objetos processados.

### Processamento das Equivalências e Itens

```groovy
percorrer (dadosEquivalencias) { itemEquivalencias ->
  
  mascara = itemEquivalencias.mascara
  
  fonteItensEquivalenciasInformados = Dados.contabilidade.v1.itensEquivalenciasInformados;
  
  filtroItensEquivalenciasInformados = "equivalencia.id = ${itemEquivalencias.id}"
  
  dadosItensEquivalenciasInformados = fonteItensEquivalenciasInformados.busca(criterio: filtroItensEquivalenciasInformados,campos:"item(id, descricao), posicao, valor, id")
  
  percorrer (dadosItensEquivalenciasInformados) { itemItensEquivalenciasInformados ->
    item = itemItensEquivalenciasInformados.valor
  }
  
  objeto = [
    idIntegracao: count.toString(),
    content: [
      exercicio: 2025,
      configuracaoPlanoContas: [
        id: 12560
      ],
      configuracaoEquivalencia: [
        id: 727296
      ],
      mascara: mascara,
      itensEquivalencias: [
        [
          posicao: 1,
          id: 427823,
          valor: item
        ]
      ]
    ]
  ]
  ListaPost.add(objeto)
  count++
 }
```

Este bloco processa cada equivalência encontrada, extraindo sua máscara e buscando os itens de equivalências informados associados. Para cada equivalência, ele busca os itens relacionados e extrai o valor do último item processado. Em seguida, constrói um objeto JSON estruturado contendo o ID de integração sequencial, dados do exercício (2025), configurações do plano de contas e equivalência, a máscara da conta e os itens de equivalência com posição, ID e valor. O objeto é adicionado à lista e o contador é incrementado.

### Geração de Arquivos em Lotes

```groovy
ListaPost.collate(50).each{it->

	nomeArquivo = [\'teste\',\'.txt\'].join(\'_\')
arquivoCsv = Arquivo.novo(nomeArquivo, \'txt\', [encoding: \'UTF-8\', entreAspas: \'N\', delimitador:\';\'])

arquivoCsv.escrever(JSON.escrever(it))
Resultado.arquivo(arquivoCsv, nomeArquivo)

  
}
```

Este bloco final organiza os dados processados em lotes de 50 registros usando o método `collate(50)`. Para cada lote, cria um arquivo de texto com nome "teste_.txt", configurado com encoding UTF-8. O conteúdo do lote é convertido para JSON usando `JSON.escrever()` e escrito no arquivo. Cada arquivo é então disponibilizado para download através do `Resultado.arquivo()`. Esta abordagem de processamento em lotes evita problemas de memória e facilita o manuseio de grandes volumes de dados.

## Código Completo

```groovy
fonteEquivalencias = Dados.contabilidade.v1.equivalencias;
filtroEquivalencias = "configuracao.id = 9638 and configuracaoEquivalencia.id = 695860 and entidade.id = ${contextoExecucao.idEntidade} and configuracaoEquivalencia.descricao = \'VPDs\''"
dadosEquivalencias = fonteEquivalencias.busca(criterio: filtroEquivalencias,campos: "mascara, configuracao(descricao, id), configuracaoEquivalencia(descricao, id)")
count = 0
ListaPost = []
percorrer (dadosEquivalencias) { itemEquivalencias ->
  
  mascara = itemEquivalencias.mascara
  
  fonteItensEquivalenciasInformados = Dados.contabilidade.v1.itensEquivalenciasInformados;
  
  filtroItensEquivalenciasInformados = "equivalencia.id = ${itemEquivalencias.id}"
  
  dadosItensEquivalenciasInformados = fonteItensEquivalenciasInformados.busca(criterio: filtroItensEquivalenciasInformados,campos:"item(id, descricao), posicao, valor, id")
  
  percorrer (dadosItensEquivalenciasInformados) { itemItensEquivalenciasInformados ->
    item = itemItensEquivalenciasInformados.valor
  }
  
  objeto = [
    idIntegracao: count.toString(),
    content: [
      exercicio: 2025,
      configuracaoPlanoContas: [
        id: 12560
      ],
      configuracaoEquivalencia: [
        id: 727296
      ],
      mascara: mascara,
      itensEquivalencias: [
        [
          posicao: 1,
          id: 427823,
          valor: item
        ]
      ]
    ]
  ]
  ListaPost.add(objeto)
  count++
 }


ListaPost.collate(50).each{it->

	nomeArquivo = [\'teste\',\'.txt\'].join(\'_\')
arquivoCsv = Arquivo.novo(nomeArquivo, \'txt\', [encoding: \'UTF-8\', entreAspas: \'N\', delimitador:\';\'])

arquivoCsv.escrever(JSON.escrever(it))
Resultado.arquivo(arquivoCsv, nomeArquivo)

  
}
```

