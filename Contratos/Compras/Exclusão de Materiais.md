# Documentação do Script de Exclusão de Materiais via CSV

Este script Groovy é responsável por ler um arquivo CSV contendo IDs de materiais e, para cada ID, realizar uma requisição DELETE para excluir o material correspondente em um serviço externo (API de Compras da Betha Cloud). É uma ferramenta útil para exclusão em massa de materiais.

## Explicação Geral do Código

O script começa configurando a URL base da API e a chave de integração necessária para autenticação. Em seguida, ele lê um arquivo CSV fornecido como parâmetro, linha por linha. Para cada linha (ignorando o cabeçalho), ele extrai o ID do material e constrói uma requisição HTTP DELETE para a API de materiais, utilizando o ID extraído. A resposta da requisição é impressa, e o processo continua até que todas as linhas do CSV sejam processadas. Ao final, uma mensagem de conclusão é exibida.

## Blocos de Código

### Configuração Inicial

```groovy
def urlBase = "https://services.compras.betha.cloud/compras-services/api"
def chave = Variavel.chaveIntegracao
```

Neste bloco, são definidas as configurações essenciais para a comunicação com a API:

*   `urlBase`: Define a URL base para o serviço de API de compras da Betha Cloud. Todas as requisições serão construídas a partir desta URL.
*   `chave`: Obtém a chave de integração. Presume-se que `Variavel.chaveIntegracao` seja uma forma de acessar uma variável de ambiente ou configuração que armazena a chave de autenticação necessária para interagir com a API.

### Leitura do Arquivo CSV

```groovy
def documento = Arquivo.ler(parametros.arquivo.valor, 'csv', [encoding: 'UTF-8', delimitador: ';'])
def linhaAtual = 0
```

Esta seção é responsável por ler e preparar o arquivo CSV de entrada:

*   `documento = Arquivo.ler(...)`: Lê o arquivo CSV. O caminho do arquivo é obtido de `parametros.arquivo.valor`, indicando que o script espera um arquivo como parâmetro de entrada. As configurações de leitura especificam que é um arquivo CSV, com codificação UTF-8 e delimitador de ponto e vírgula.
*   `linhaAtual = 0`: Inicializa um contador para controlar a linha atual que está sendo processada no CSV.

### Processamento das Linhas do CSV e Requisição DELETE

```groovy
while (documento.contemProximaLinha()) {
    linhaAtual++
    def registro = documento.lerLinha().split(";")
    if (linhaAtual == 1) continue // Pula cabeçalho

    def id = registro.getAt(0)?.toLong()
    if (!id) continue

    // Apenas para log
    def payload = [material: [id: id]]
    def jsonPayload = JSON.escrever(payload)
    imprimir "jsonPayload: " + jsonPayload

    // Executa o DELETE
    def resposta = Http.servico("${urlBase}/materiais/${id}")
        .chaveIntegracao(chave)
        .cabecalho("Content-Type", "application/json")
        .DELETE()

    imprimir resposta.conteudo()
}
```

Este é o coração do script, onde cada linha do CSV é processada para realizar a exclusão:

*   `while (documento.contemProximaLinha())`: Loop que continua enquanto houver linhas para ler no documento CSV.
*   `linhaAtual++`: Incrementa o contador de linha.
*   `registro = documento.lerLinha().split(";")`: Lê a linha atual do CSV e a divide em um array de strings usando o ponto e vírgula como delimitador.
*   `if (linhaAtual == 1) continue`: Pula a primeira linha do arquivo, assumindo que seja o cabeçalho do CSV.
*   `id = registro.getAt(0)?.toLong()`: Tenta extrair o ID do material da primeira coluna (`getAt(0)`) da linha atual e convertê-lo para um tipo `Long`. O operador `?.` (safe navigation) evita erros caso a coluna esteja vazia.
*   `if (!id) continue`: Se o ID não puder ser extraído ou for nulo, a linha é ignorada e o loop continua para a próxima.
*   **Log do Payload**: `payload` e `jsonPayload` são criados e impressos para fins de depuração, mostrando o formato do dado que *poderia* ser enviado em uma requisição POST/PUT, embora para um DELETE, o ID já esteja na URL.
*   **Execução do DELETE**: `Http.servico(...)` constrói a requisição HTTP:
    *   `${urlBase}/materiais/${id}`: Monta a URL completa para a exclusão, incluindo o ID do material.
    *   `.chaveIntegracao(chave)`: Adiciona a chave de integração para autenticação.
    *   `.cabecalho("Content-Type", "application/json")`: Define o cabeçalho `Content-Type` como `application/json`.
    *   `.DELETE()`: Especifica que a requisição é do tipo DELETE.
*   `imprimir resposta.conteudo()`: Imprime o conteúdo da resposta da API, que pode indicar o sucesso ou falha da exclusão.

### Finalização do Processo

```groovy
imprimir "Processo de exclusão finalizado."
```

Após o loop processar todas as linhas do CSV, esta linha final é impressa, indicando que o script concluiu sua execução.

## Código Completo

```groovy
// Configuração inicial
def urlBase = "https://services.compras.betha.cloud/compras-services/api"
def chave = Variavel.chaveIntegracao

// Leitura do CSV
def documento = Arquivo.ler(parametros.arquivo.valor, 'csv', [encoding: 'UTF-8', delimitador: ';'])
def linhaAtual = 0

while (documento.contemProximaLinha()) {
    linhaAtual++
    def registro = documento.lerLinha().split(";")
    if (linhaAtual == 1) continue // Pula cabeçalho

    def id = registro.getAt(0)?.toLong()
    if (!id) continue

    // Apenas para log
    def payload = [material: [id: id]]
    def jsonPayload = JSON.escrever(payload)
    imprimir "jsonPayload: " + jsonPayload

    // Executa o DELETE
    def resposta = Http.servico("${urlBase}/materiais/${id}")
        .chaveIntegracao(chave)
        .cabecalho("Content-Type", "application/json")
        .DELETE()

    imprimir resposta.conteudo()
}

imprimir "Processo de exclusão finalizado."
```

