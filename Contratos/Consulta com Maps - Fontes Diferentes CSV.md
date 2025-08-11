# Documentação do Script de Exportação de Bens (Materiais e Especificações) para CSV

Este script Groovy tem como objetivo principal coletar informações de materiais e suas respectivas especificações de fontes de dados (`Dados.contratos.v1.materiais` e `Dados.contratos.v1.materiais.especificacoes`), estruturá-las em um objeto e, finalmente, exportar esses dados para um arquivo CSV. O arquivo CSV gerado conterá o ID do material, sua descrição e uma lista de IDs de suas especificações.

## Explicação Geral do Código

O script começa inicializando um objeto vazio que servirá como um contêiner para os dados estruturados. Ele então realiza duas buscas principais: primeiro, busca materiais com base em uma lista predefinida de códigos; segundo, busca as especificações associadas a esses materiais. Os dados são organizados de forma que cada material tenha suas especificações aninhadas. Por fim, o script cria um arquivo CSV com um nome dinâmico, escreve um cabeçalho e preenche o arquivo com os dados coletados e estruturados, imprimindo também cada linha no console.

## Blocos de Código

### Inicialização e Busca de Materiais

```groovy
objeto = [:]

// Buscar os materiais filtrados
Dados.contratos.v1.materiais.busca(
  criterio: "codigoMaterial in (10010421, 50010101, 10010642)",
  campos: "id, descricao"
).each { itemMateriais ->

  chave = itemMateriais.id

  if (!objeto[chave]) {
    objeto[chave] = [
      id: itemMateriais.id,
      descricao: itemMateriais.descricao,
      listaEspecificacoes: []
    ]
  }
}
```

Neste bloco, o script inicializa a estrutura de dados e busca os materiais:

*   `objeto = [:]`: Cria um mapa vazio (`objeto`) que será usado para armazenar os materiais e suas especificações de forma organizada, onde a chave será o ID do material.
*   `Dados.contratos.v1.materiais.busca(...)`: Realiza uma busca na fonte de dados de materiais. O `criterio` filtra os materiais pelos `codigoMaterial` especificados (10010421, 50010101, 10010642), e os `campos` `id` e `descricao` são solicitados.
*   `.each { itemMateriais -> ... }`: Itera sobre cada material encontrado na busca:
    *   `chave = itemMateriais.id`: Define o ID do material como a chave para o `objeto`.
    *   `if (!objeto[chave]) { ... }`: Verifica se o material já foi adicionado ao `objeto`. Se não, ele é adicionado com seu `id`, `descricao` e uma `listaEspecificacoes` vazia, que será preenchida posteriormente.

### Busca de Especificações por Material

```groovy
// Buscar as especificações por material
objeto.keySet().collate(300).each { listaIdsCollated ->
  Dados.contratos.v1.materiais.especificacoes.busca(
    campos: "id, material.id",
    criterio: "material.id in (${listaIdsCollated.join(\",\")})"
  ).each { itemEspecificacoes ->

    chaveMaterial = itemEspecificacoes.material.id
    if (objeto.containsKey(chaveMaterial)) {
      objeto[chaveMaterial].listaEspecificacoes << itemEspecificacoes.id
    }
  }
}
```

Esta seção busca as especificações e as associa aos materiais correspondentes:

*   `objeto.keySet().collate(300)`: Obtém todos os IDs dos materiais já coletados (`keySet()`) e os agrupa em lotes de 300 (`collate(300)`). Isso é útil para otimizar as buscas, evitando que a URL da requisição fique muito longa se houver muitos IDs.
*   `.each { listaIdsCollated -> ... }`: Itera sobre cada lote de IDs:
    *   `Dados.contratos.v1.materiais.especificacoes.busca(...)`: Busca especificações, filtrando por `material.id` que estejam no lote atual (`listaIdsCollated`). Apenas os campos `id` da especificação e `material.id` são solicitados.
    *   `.each { itemEspecificacoes -> ... }`: Itera sobre cada especificação encontrada:
        *   `chaveMaterial = itemEspecificacoes.material.id`: Obtém o ID do material ao qual a especificação pertence.
        *   `if (objeto.containsKey(chaveMaterial)) { ... }`: Verifica se o material correspondente à especificação já existe no `objeto`.
        *   `objeto[chaveMaterial].listaEspecificacoes << itemEspecificacoes.id`: Se o material existir, o ID da especificação é adicionado à `listaEspecificacoes` do material correspondente no `objeto`.

### Criação e Configuração do Arquivo CSV de Saída

```groovy
nomeArquivo = [Datas.formatar(Datas.hoje(), 'dd-MM-yyyy_hh-mm-ss'), 'ExportacaoBens.csv'].join('_')
arquivo = Arquivo.novo(nomeArquivo, 'csv', [delimitador: ','])
```

Neste bloco, o script prepara o arquivo CSV para a exportação:

*   `nomeArquivo = [...]`: Constrói o nome do arquivo CSV dinamicamente, incluindo a data e hora atuais (ex: `05-08-2025_14-30-00_ExportacaoBens.csv`).
*   `arquivo = Arquivo.novo(nomeArquivo, 'csv', [delimitador: ','])`: Cria uma nova instância de arquivo CSV com o nome gerado e define a vírgula (`,`) como delimitador.

### Escrita do Cabeçalho e Dados no CSV

```groovy
// Cabeçalho CSV
cabecalho = ['ID Material', 'Descrição', 'IDs Especificações']
arquivo.escrever(cabecalho.join(';'))
arquivo.novaLinha()
//imprimir "ID Material;Descrição;IDs Especificações"

// Imprimir os dados em formato CSV
objeto.each { chave, dados ->
  linha = "${dados.id};\"${dados.descricao}\";\"${dados.listaEspecificacoes.join(';')}\"


"
  imprimir linha
  
  arquivo.escrever(linha)
  arquivo.novaLinha()
  
}
```

Esta seção é responsável por escrever o cabeçalho e os dados no arquivo CSV:

*   `cabecalho = [...]`: Define um array com os nomes das colunas do CSV.
*   `arquivo.escrever(cabecalho.join(";"))`: Escreve a linha do cabeçalho no arquivo CSV, unindo os elementos do array `cabecalho` com ponto e vírgula. Note que, embora o arquivo seja configurado com delimitador `,`, o cabeçalho está sendo escrito com `;`. Isso pode ser uma inconsistência ou uma escolha intencional para um formato específico de importação/exportação.
*   `arquivo.novaLinha()`: Adiciona uma nova linha após o cabeçalho.
*   `objeto.each { chave, dados -> ... }`: Itera sobre cada material e seus dados estruturados no `objeto`:
    *   `linha = ...`: Constrói a string da linha CSV para o material atual. Os campos `id` e `descricao` do material, e a lista de `listaEspecificacoes` (unida por ponto e vírgula) são concatenados. Note que a `descricao` e a `listaEspecificacoes` são encapsuladas por aspas duplas, o que é uma boa prática para campos que podem conter o caractere delimitador ou outros caracteres especiais.
    *   `imprimir linha`: Imprime a linha CSV no console.
    *   `arquivo.escrever(linha)`: Escreve a linha CSV no arquivo.
    *   `arquivo.novaLinha()`: Adiciona uma nova linha após cada registro de material.

### Resultado Final

```groovy
Resultado.arquivo(arquivo, nomeArquivo)
```

Esta linha finaliza o script, disponibilizando o arquivo CSV gerado:

*   `Resultado.arquivo(arquivo, nomeArquivo)`: Associa o objeto `arquivo` (que contém todos os dados exportados) ao resultado final do script. Isso permite que o arquivo CSV seja baixado ou acessado por outros sistemas após a execução do script.

## Código Completo

```groovy
objeto = [:]

// Buscar os materiais filtrados
Dados.contratos.v1.materiais.busca(
  criterio: "codigoMaterial in (10010421, 50010101, 10010642)",
  campos: "id, descricao"
).each { itemMateriais ->

  chave = itemMateriais.id

  if (!objeto[chave]) {
    objeto[chave] = [
      id: itemMateriais.id,
      descricao: itemMateriais.descricao,
      listaEspecificacoes: []
    ]
  }
}

// Buscar as especificações por material
objeto.keySet().collate(300).each { listaIdsCollated ->
  Dados.contratos.v1.materiais.especificacoes.busca(
    campos: "id, material.id",
    criterio: "material.id in (${listaIdsCollated.join(\",\")})"
  ).each { itemEspecificacoes ->

    chaveMaterial = itemEspecificacoes.material.id
    if (objeto.containsKey(chaveMaterial)) {
      objeto[chaveMaterial].listaEspecificacoes << itemEspecificacoes.id
    }
  }
}

nomeArquivo = [Datas.formatar(Datas.hoje(), 'dd-MM-yyyy_hh-mm-ss'), 'ExportacaoBens.csv'].join('_')
arquivo = Arquivo.novo(nomeArquivo, 'csv', [delimitador: ','])

// Cabeçalho CSV
cabecalho = ['ID Material', 'Descrição', 'IDs Especificações']
arquivo.escrever(cabecalho.join(';'))
arquivo.novaLinha()
//imprimir "ID Material;Descrição;IDs Especificações"

// Imprimir os dados em formato CSV
objeto.each { chave, dados ->
  linha = "${dados.id};\"${dados.descricao}\";\"${dados.listaEspecificacoes.join(';')}\"
  imprimir linha
  
  arquivo.escrever(linha)
  arquivo.novaLinha()
  
}

Resultado.arquivo(arquivo, nomeArquivo)
```

