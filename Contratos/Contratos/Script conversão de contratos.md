# Documentação do Script de Atualização de Número de Contrato de Conversão

Este script Groovy tem como finalidade atualizar o número de contrato de conversão de um contrato específico no sistema, utilizando uma requisição PUT para uma API externa. Após a atualização, ele gera um arquivo CSV com os detalhes do contrato atualizado ou com a mensagem de erro, caso a atualização não seja bem-sucedida.

## Explicação Geral do Código

O script recebe como parâmetros o ID da entidade, o sequencial, o ano do contrato e o novo número de contrato de conversão, além de um token de autorização. Primeiramente, ele busca o ID interno do contrato com base nos parâmetros fornecidos. Em seguida, constrói um payload JSON com o ID do contrato e o novo número de conversão e realiza uma chamada PUT para a API de contratos para efetivar a atualização. Dependendo do sucesso da requisição (código de resposta 200), o script busca novamente os dados do contrato (agora com o número de conversão atualizado) e os exporta para um arquivo CSV. Se a requisição falhar, o CSV conterá a mensagem de erro da API.

## Blocos de Código

### Obtenção de Parâmetros e Inicialização do CSV

```groovy
entidade = parametros.entidade.selecionado
sequencial = parametros.sequencial.valor
ano = parametros.ano.valor
numeroContratoConversao = parametros.numeroContratoConversao.valor
pAutorizacao = parametros.pAutorizacao.valor


csv = Arquivo.novo("Contrato_Conversao.csv",'csv',[encoding: 'iso-8859-1', delimitador:";"]);
```

Neste bloco, o script obtém os valores dos parâmetros de entrada e inicializa o arquivo CSV de saída:

*   `entidade`, `sequencial`, `ano`, `numeroContratoConversao`, `pAutorizacao`: Estas variáveis recebem os valores passados como parâmetros para o script. `entidade.selecionado` sugere que o parâmetro `entidade` é uma lista de opções.
*   `csv = Arquivo.novo(...)`: Cria um novo arquivo CSV chamado `Contrato_Conversao.csv`. É configurado com codificação `iso-8859-1` e delimitador `;`.

### Busca do ID do Contrato

```groovy
filtroContratacoes = "sequencial = ${sequencial} and entidade.id = ${entidade} and ano = ${ano}"
fonteContratacoes = Dados.contratos.v1.contratacoes;
contrato = fonteContratacoes.busca(primeiro:true,criterio: filtroContratacoes,campos: "id").id
```

Esta seção busca o ID interno do contrato que será atualizado:

*   `filtroContratacoes = ...`: Constrói uma string de filtro para localizar o contrato exato com base no `sequencial`, `entidade.id` e `ano` fornecidos.
*   `fonteContratacoes = Dados.contratos.v1.contratacoes;`: Define a fonte de dados para contratações.
*   `contrato = fonteContratacoes.busca(primeiro:true,criterio: filtroContratacoes,campos: "id").id`: Realiza a busca. `primeiro:true` garante que apenas o primeiro resultado seja retornado, e `.id` extrai diretamente o ID do contrato encontrado.

### Preparação dos Dados e Requisição PUT para Atualização

```groovy
dados = [
  "contratacao": [
    "id": contrato.toInteger()
  ],
  "numeroContratoConversao": "${numeroContratoConversao}"
]

dados = JSON.escrever(dados)

svcPUT = Http.servico("https://contratos.betha.cloud/contratacao-services/api/exercicios/${ano}/contratacoes/${contrato}/atualizar-numero-conversao")
.cabecalho(\'Authorization\': \'Bearer \'+pAutorizacao)
.PUT(dados,Http.JSON)  
imprimir  respostaPUT = svcPUT.codigo() + " - " + svcPUT.conteudo()
```

Neste bloco, o script prepara o payload para a API e executa a requisição PUT:

*   `dados = [...]`: Cria um mapa que representa o payload JSON a ser enviado na requisição. Ele inclui o `id` do contrato e o `numeroContratoConversao`.
*   `dados = JSON.escrever(dados)`: Converte o mapa `dados` para uma string JSON.
*   `svcPUT = Http.servico(...)`: Constrói o serviço HTTP para a requisição PUT:
    *   A URL é montada dinamicamente com o `ano` e o `contrato`.
    *   `.cabecalho(\'Authorization\': \'Bearer \'+pAutorizacao)`: Adiciona o cabeçalho de autorização com o token fornecido.
    *   `.PUT(dados,Http.JSON)`: Realiza a requisição PUT, enviando o payload JSON.
*   `imprimir respostaPUT = svcPUT.codigo() + " - " + svcPUT.conteudo()`: Imprime o código de status da resposta HTTP e o conteúdo da resposta para fins de depuração.

### Processamento da Resposta e Geração do CSV (Sucesso)

```groovy
se(svcPUT.codigo() == 200){
fonteContratacoes = Dados.contratos.v1.contratacoes;
dadosContratacoes = fonteContratacoes.busca(criterio: filtroContratacoes,campos: "numeroContratoConversao,entidade(nome, id), fornecedor(pessoa(nome)), numeroTermo, ano, id, sequencial")
percorrer (dadosContratacoes) { itemContratacoes ->

respostaPUT = svcPUT.codigo() + " - " + svcPUT.conteudo()
  

//colunas CSV
csv.escrever(\'Entidade\')
csv.escrever(\'numeroTermo\')
csv.escrever(\'sequencial\')
csv.escrever(\'ano\')
csv.escrever(\'numeroContratoConversao\')
csv.novaLinha()
 
  
csv.escrever(itemContratacoes.entidade.nome)
csv.escrever(itemContratacoes.numeroTermo)
csv.escrever(itemContratacoes.sequencial)
csv.escrever(itemContratacoes.ano)
csv.escrever(itemContratacoes.numeroContratoConversao)
csv.novaLinha()
  
  
  
  
}}
```

Este bloco é executado se a requisição PUT for bem-sucedida (código 200):

*   `se(svcPUT.codigo() == 200)`: Condição para verificar o sucesso da requisição.
*   **Nova Busca de Contrato**: O script realiza uma nova busca pelo contrato para obter os dados atualizados, incluindo o `numeroContratoConversao`.
*   **Escrita do Cabeçalho CSV**: Escreve o cabeçalho das colunas no arquivo CSV: `Entidade`, `numeroTermo`, `sequencial`, `ano`, `numeroContratoConversao`.
*   **Escrita dos Dados no CSV**: Itera sobre o contrato encontrado (apenas um, pois a busca é por um contrato específico) e escreve seus detalhes no CSV, incluindo o novo número de contrato de conversão.

### Processamento da Resposta e Geração do CSV (Erro)

```groovy
senao{

imprimir  respostaPUT = svcPUT.codigo() + " - " + svcPUT.conteudo()
  

//colunas CSV
csv.escrever(\'Retorno\')
csv.novaLinha()
 
  
csv.escrever(respostaPUT)
csv.novaLinha()  

}
```

Este bloco é executado se a requisição PUT falhar (código diferente de 200):

*   `senao`: Bloco executado em caso de falha da requisição PUT.
*   `imprimir respostaPUT = svcPUT.codigo() + " - " + svcPUT.conteudo()`: Imprime o código de status e o conteúdo da resposta de erro da API.
*   **Escrita do Cabeçalho CSV (Erro)**: Escreve um cabeçalho simples 'Retorno' no CSV.
*   **Escrita da Mensagem de Erro no CSV**: Escreve a `respostaPUT` (código e conteúdo da resposta de erro) no arquivo CSV, indicando o problema ocorrido.

### Resultado Final

```groovy
Resultado.arquivo(csv,'Contrato_Conversao.csv')  
```

Esta linha finaliza o script, disponibilizando o arquivo CSV gerado:

*   `Resultado.arquivo(csv,'Contrato_Conversao.csv')`: Associa o objeto `csv` (que contém os dados do contrato atualizado ou a mensagem de erro) ao resultado final do script, tornando o arquivo `Contrato_Conversao.csv` disponível para download.

## Código Completo

```groovy
entidade = parametros.entidade.selecionado
sequencial = parametros.sequencial.valor
ano = parametros.ano.valor
numeroContratoConversao = parametros.numeroContratoConversao.valor
pAutorizacao = parametros.pAutorizacao.valor


csv = Arquivo.novo('Contrato_Conversao.csv','csv',[encoding: 'iso-8859-1', delimitador:';']);



filtroContratacoes = "sequencial = ${sequencial} and entidade.id = ${entidade} and ano = ${ano}"
fonteContratacoes = Dados.contratos.v1.contratacoes;
contrato = fonteContratacoes.busca(primeiro:true,criterio: filtroContratacoes,campos: "id").id


dados = [
  "contratacao": [
    "id": contrato.toInteger()
  ],
  "numeroContratoConversao": "${numeroContratoConversao}"
]

dados = JSON.escrever(dados)

svcPUT = Http.servico("https://contratos.betha.cloud/contratacao-services/api/exercicios/${ano}/contratacoes/${contrato}/atualizar-numero-conversao")
.cabecalho('Authorization': 'Bearer '+pAutorizacao)
.PUT(dados,Http.JSON)  
imprimir  respostaPUT = svcPUT.codigo() + " - " + svcPUT.conteudo()


se(svcPUT.codigo() == 200){
fonteContratacoes = Dados.contratos.v1.contratacoes;
dadosContratacoes = fonteContratacoes.busca(criterio: filtroContratacoes,campos: "numeroContratoConversao,entidade(nome, id), fornecedor(pessoa(nome)), numeroTermo, ano, id, sequencial")
percorrer (dadosContratacoes) { itemContratacoes ->

respostaPUT = svcPUT.codigo() + " - " + svcPUT.conteudo()
  

//colunas CSV
csv.escrever('Entidade')
csv.escrever('numeroTermo')
csv.escrever('sequencial')
csv.escrever('ano')
csv.escrever('numeroContratoConversao')
csv.novaLinha()
 
  
csv.escrever(itemContratacoes.entidade.nome)
csv.escrever(itemContratacoes.numeroTermo)
csv.escrever(itemContratacoes.sequencial)
csv.escrever(itemContratacoes.ano)
csv.escrever(itemContratacoes.numeroContratoConversao)
csv.novaLinha()
  
  
  
  
}}senao{

imprimir  respostaPUT = svcPUT.codigo() + " - " + svcPUT.conteudo()
  

//colunas CSV
csv.escrever('Retorno')
csv.novaLinha()
 
  
csv.escrever(respostaPUT)
csv.novaLinha()  

}

Resultado.arquivo(csv,'Contrato_Conversao.csv')  
```

