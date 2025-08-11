# Documentação do Script de Exportação de Materiais para CSV

Este script Groovy é projetado para extrair dados de materiais de uma fonte (`Dados.compras.v1.materiais`), limpar e formatar esses dados, e então exportá-los para um arquivo CSV. Ele inclui uma função utilitária para garantir que o texto esteja adequado para o formato CSV, lidando com quebras de linha e caracteres problemáticos.

## Explicação Geral do Código

O script começa definindo uma função (`limparTextoCSV`) que é crucial para a integridade do CSV, pois ela sanitiza strings removendo quebras de linha, substituindo ponto-e-vírgulas e tratando aspas duplas. Em seguida, ele busca dados de materiais de um sistema, cria um novo arquivo CSV com configurações específicas (como delimitador e codificação), escreve um cabeçalho e, finalmente, itera sobre os dados dos materiais, aplicando a função de limpeza e escrevendo cada registro no arquivo CSV. Ao final, o arquivo gerado é retornado como resultado do script.

## Blocos de Código

### Função `limparTextoCSV`

```groovy
def limparTextoCSV(texto) {
    if (texto == null) return ""
    return "\"" + texto
        .replaceAll("[\\r\\n\\u2028\\u2029]+", " ") // quebra de linha
        .replaceAll(";", ",")                      // substitui ponto-e-vírgula por vírgula
        .replaceAll("\"", "'")                     // aspas duplas viram aspas simples
        .trim() + "\""                             // encapsula entre aspas
}
```

Esta função é fundamental para a correta formatação dos dados no CSV. Ela recebe uma string (`texto`) e realiza as seguintes operações:

*   **Tratamento de Nulos**: Se o `texto` for nulo, retorna uma string vazia.
*   **Remoção de Quebras de Linha**: Substitui todas as quebras de linha (`\r`, `\n`, `\u2028`, `\u2029`) por um espaço simples. Isso evita que um campo de texto ocupe múltiplas linhas no CSV, o que poderia corromper o formato.
*   **Substituição de Delimitador**: Troca todos os ponto-e-vírgulas (`;`) por vírgulas (`,`). Isso é importante porque o CSV será delimitado por vírgulas, e a presença de ponto-e-vírgulas nos dados poderia causar problemas de parseamento.
*   **Tratamento de Aspas Duplas**: Converte todas as aspas duplas (`"`) em aspas simples (`'`). Isso é feito porque o campo será encapsulado por aspas duplas, e aspas duplas internas não escapadas corretamente podem quebrar o formato CSV.
*   **Remoção de Espaços Extras**: Remove espaços em branco no início e no fim da string (`trim()`).
*   **Encapsulamento com Aspas Duplas**: Finalmente, encapsula toda a string resultante entre aspas duplas (`"`). Isso é uma prática comum em CSV para lidar com campos que podem conter o caractere delimitador ou quebras de linha (mesmo que já tratadas, é uma camada de segurança).

### Fonte de Dados e Busca de Materiais

```groovy
def fonteMateriais = Dados.compras.v1.materiais

// Busca dos materiais com o campo id
def dadosMateriais = fonteMateriais.busca(campos: "id, descricao, codigoMaterial")
```

Neste bloco, o script define a origem dos dados e realiza a primeira operação de busca:

*   `fonteMateriais = Dados.compras.v1.materiais`: Inicializa uma variável `fonteMateriais` com a referência a uma fonte de dados de materiais, presumivelmente um serviço ou API de compras.
*   `dadosMateriais = fonteMateriais.busca(campos: "id, descricao, codigoMaterial")`: Realiza uma busca nessa fonte de dados para obter todos os materiais disponíveis, solicitando especificamente os campos `id`, `descricao` e `codigoMaterial`.

### Criação e Configuração do Arquivo CSV

```groovy
def nomeArquivo = "exporta_materiais.csv"
def arquivoCSV = Arquivo.novo(
  nomeArquivo,
  'csv',
  [encoding: 'UTF-8', entreAspas: 'N', delimitador: ',', quebraLinha: '\n'] 
  // aqui 'entreAspas' mudou para 'N' porque você já está encapsulando manualmente no limparTextoCSV
)
```

Esta seção é crucial para a **criação e configuração do arquivo CSV de saída**:

*   `nomeArquivo = "exporta_materiais.csv"`: Define o nome do arquivo CSV que será gerado.
*   `arquivoCSV = Arquivo.novo(...)`: Cria uma nova instância de arquivo CSV com as seguintes configurações:
    *   `nomeArquivo`: O nome definido para o arquivo.
    *   `'csv'`: Especifica que o tipo de arquivo é CSV.
    *   `encoding: 'UTF-8'`: Define a codificação do arquivo como UTF-8, garantindo a correta exibição de caracteres especiais e acentuados.
    *   `entreAspas: 'N'`: **Importante**: Esta configuração indica que o sistema *não* deve encapsular automaticamente os campos com aspas duplas. Isso é intencional, pois a função `limparTextoCSV` já realiza esse encapsulamento manualmente, dando mais controle sobre o formato de cada campo.
    *   `delimitador: ','`: Define a vírgula como o caractere que separará os campos dentro de cada linha do CSV.
    *   `quebraLinha: '\n'`: Especifica que a quebra de linha padrão (`\n`) deve ser usada para separar os registros.

### Escrita do Cabeçalho do CSV

```groovy
// Cabeçalho
arquivoCSV.escrever("ID")
arquivoCSV.escrever("Código Material")
arquivoCSV.escrever("Descrição")
arquivoCSV.novaLinha()
```

Antes de escrever os dados, este bloco adiciona o cabeçalho ao arquivo CSV, definindo os nomes das colunas:

*   `arquivoCSV.escrever(...)`: Cada chamada a este método escreve um valor em uma célula da linha atual. Aqui, são escritos os títulos das colunas: 

`ID`, `Código Material` e `Descrição`.
*   `arquivoCSV.novaLinha()`: Move o cursor para a próxima linha no arquivo CSV, garantindo que os dados começarão em uma nova linha após o cabeçalho.

### Contador e Preenchimento do Arquivo com os Dados

```groovy
// Contador
def total = 0

// Preenchimento do arquivo com os dados
percorrer(dadosMateriais) { item ->
    arquivoCSV.escrever("${item.id}")
    arquivoCSV.escrever("${item.codigoMaterial}")
    arquivoCSV.escrever(limparTextoCSV(item.descricao))
    arquivoCSV.novaLinha()
    total++
}
```

Esta é a parte principal onde os dados são processados e escritos no CSV:

*   `def total = 0`: Inicializa um contador para acompanhar o número de registros exportados.
*   `percorrer(dadosMateriais) { item -> ... }`: Itera sobre cada `item` (material) obtido na busca inicial (`dadosMateriais`). Para cada item:
    *   `arquivoCSV.escrever("${item.id}")`: Escreve o ID do material no arquivo CSV.
    *   `arquivoCSV.escrever("${item.codigoMaterial}")`: Escreve o código do material no arquivo CSV.
    *   `arquivoCSV.escrever(limparTextoCSV(item.descricao))`: **Chave para a qualidade do CSV**: Escreve a descrição do material no arquivo CSV, mas antes passa a descrição pela função `limparTextoCSV`. Isso garante que a descrição esteja livre de caracteres problemáticos (quebras de linha, ponto-e-vírgulas, aspas duplas) e esteja corretamente encapsulada para o formato CSV.
    *   `arquivoCSV.novaLinha()`: Adiciona uma nova linha após cada registro completo, garantindo que cada material ocupe uma linha separada no CSV.
    *   `total++`: Incrementa o contador de registros.

### Retorno do Arquivo e Impressão de Status

```groovy
// Retorno do arquivo
Resultado.arquivo(arquivoCSV, nomeArquivo)
imprimir "Arquivo \'${nomeArquivo}\' gerado com sucesso com ${total} registros."
```

Este bloco finaliza o script, disponibilizando o arquivo e fornecendo feedback:

*   `Resultado.arquivo(arquivoCSV, nomeArquivo)`: Esta linha é fundamental. Ela associa o objeto `arquivoCSV` (que agora contém todos os dados e o cabeçalho) ao resultado final do script. Isso significa que o arquivo `exporta_materiais.csv` será disponibilizado para download ou para o próximo passo do fluxo de trabalho.
*   `imprimir "Arquivo \'${nomeArquivo}\' gerado com sucesso com ${total} registros."`: Imprime uma mensagem no console (ou log) indicando que o arquivo foi gerado com sucesso e quantos registros foram exportados. Isso é útil para monitoramento e depuração.

## Código Completo

```groovy
// Função para formatar quebras de linhas e caracteres problemáticos no CSV
def limparTextoCSV(texto) {
    if (texto == null) return ""
    return "\"" + texto
        .replaceAll("[\\r\\n\\u2028\\u2029]+", " ") // quebra de linha
        .replaceAll(";", ",")                      // substitui ponto-e-vírgula por vírgula
        .replaceAll("\"", "'")                     // aspas duplas viram aspas simples
        .trim() + "\""                             // encapsula entre aspas
}

// Fonte de dados
def fonteMateriais = Dados.compras.v1.materiais

// Busca dos materiais com o campo id
def dadosMateriais = fonteMateriais.busca(campos: "id, descricao, codigoMaterial")

// Criação do arquivo CSV com delimitador vírgula
def nomeArquivo = "exporta_materiais.csv"
def arquivoCSV = Arquivo.novo(
  nomeArquivo,
  'csv',
  [encoding: 'UTF-8', entreAspas: 'N', delimitador: ',', quebraLinha: '\n'] 
  // aqui 'entreAspas' mudou para 'N' porque você já está encapsulando manualmente no limparTextoCSV
)

// Cabeçalho
arquivoCSV.escrever("ID")
arquivoCSV.escrever("Código Material")
arquivoCSV.escrever("Descrição")
arquivoCSV.novaLinha()

// Contador
def total = 0

// Preenchimento do arquivo com os dados
percorrer(dadosMateriais) { item ->
    arquivoCSV.escrever("${item.id}")
    arquivoCSV.escrever("${item.codigoMaterial}")
    arquivoCSV.escrever(limparTextoCSV(item.descricao))
    arquivoCSV.novaLinha()
    total++
}

// Retorno do arquivo
Resultado.arquivo(arquivoCSV, nomeArquivo)
imprimir "Arquivo \'${nomeArquivo}\' gerado com sucesso com ${total} registros."
```

