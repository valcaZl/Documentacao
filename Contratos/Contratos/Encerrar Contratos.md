# Documentação do Script de Encerramento de Contratos e Geração de Log

Este script Groovy tem como objetivo principal automatizar o encerramento de contratos com situação 'EXECUCAO' para entidades específicas, com base em uma data de encerramento fornecida. Ele busca contratos e seus aditivos, atualiza as datas de vigência com base nos aditivos e, para os contratos que se enquadram nos critérios de encerramento, realiza uma chamada de API para encerrá-los e gera um arquivo CSV de log com os contratos encerrados.

## Explicação Geral do Código

O script começa definindo o ano de encerramento e uma lista de anos para busca de contratos. Ele também configura tokens de integração para diferentes entidades. Em seguida, busca contratos em execução dentro do período definido, mapeando-os para uma estrutura de dados que inclui informações básicas e uma lista para aditivos. Uma segunda busca é realizada para encontrar aditivos de prazo para esses contratos e atualizar suas datas de vigência. Finalmente, o script itera sobre os contratos, filtra por entidade (Câmara Municipal de Luzerna) e data de encerramento, realiza a chamada de API para encerrar o contrato e registra os detalhes do contrato encerrado em um arquivo CSV de log. Duas funções auxiliares são usadas para conversão de datas e para realizar a chamada de API de encerramento.

## Blocos de Código

### Configuração Inicial e Definição de Anos e Tokens

```groovy
dataEncerramento = parametros.p_anoEncerramento.valor
anos = []

for(i=2010;i<=2024;i++){
  	anos<<i
}

tokens = [
         "MUNICIPIO DE LUZERNA":"760688d3-f5e0-46f5-87ac-2edb8801388b",
         "CAMARA MUNICIPAL DE LUZERNA":"ee746119-d4a9-4bc5-89fa-90c0dce56efd",
  		 "FUNDO MUNICIPAL SAUDE LUZERNA":"f1be864b-94d5-4c0c-9280-a803dea99e88"
]
```

Neste bloco, o script define as variáveis e configurações iniciais:

*   `dataEncerramento = parametros.p_anoEncerramento.valor`: Obtém a data de encerramento a partir de um parâmetro de entrada (`p_anoEncerramento`).
*   `anos = []` e o loop `for`: Popula a lista `anos` com um intervalo de anos (de 2010 a 2024). Esta lista será usada para definir o período de busca dos contratos.
*   `tokens = [...]`: Define um mapa (`tokens`) que associa o nome de cada entidade a um token de integração (chave de API). Estes tokens são essenciais para autenticação nas chamadas de API.

### Busca e Mapeamento de Contratos

```groovy
fonteContratacoes = Dados.contratos.v1.contratacoes;
filtroContratacoes = "dataAssinatura >= ${anos[0]}-01-01 and dataAssinatura <= ${anos[-1]}-12-31 and situacao = \'EXECUCAO\'";
mapaContratos = [:]

dadosContratacoes = fonteContratacoes.busca(criterio: filtroContratacoes,campos: "entidade(id,nome), id, numeroProcesso, anoProcesso, sequencial, numeroTermo, ano, dataAssinatura,dataInicioVigencia,dataFimVigencia")
percorrer (dadosContratacoes) { itemContratacoes ->
  chave = itemContratacoes.id
  if(!mapaContratos[chave]){
    mapaContratos[chave]=[
      entidade:itemContratacoes.entidade.nome,
      idEntidade: itemContratacoes.entidade.id,
      idContratacao: itemContratacoes.id,
      numeroProcesso:itemContratacoes.numeroProcesso,
      anoProcesso:itemContratacoes.anoProcesso,
      sequencial:itemContratacoes.sequencial,
      numeroTermo:itemContratacoes.numeroTermo,
      ano:itemContratacoes.ano,
      dataAssinatura:itemContratacoes.dataAssinatura.format("dd/MM/yyyy"),
      dataInicioVigencia:itemContratacoes.dataInicioVigencia.format("dd/MM/yyyy"),
      dataFimVigencia:itemContratacoes.dataFimVigencia.format("dd/MM/yyyy"),
      aditivos:[]
    ]
  }
}
```

Esta seção busca os contratos e os organiza em um mapa:

*   `fonteContratacoes = Dados.contratos.v1.contratacoes;`: Define a fonte de dados para contratações.
*   `filtroContratacoes = ...`: Constrói um filtro para buscar contratos com `dataAssinatura` dentro do intervalo de anos definido e com `situacao` igual a 'EXECUCAO'.
*   `mapaContratos = [:]`: Inicializa um mapa vazio para armazenar os contratos, usando o ID do contrato como chave.
*   `dadosContratacoes = fonteContratacoes.busca(...)`: Realiza a busca dos contratos com base no filtro e nos campos especificados.
*   `percorrer (dadosContratacoes) { ... }`: Itera sobre cada contrato encontrado e o adiciona ao `mapaContratos` com suas informações formatadas e uma lista vazia para `aditivos`.

### Busca e Vinculação de Aditivos

```groovy
//Busca aditivos e vincula a seus contratos caso haverem
idsContratos = mapaContratos.keySet()
idsContratos.collate(50).each{idsContratos->
  Dados.contratos.v1.contratacoes.aditivos.busca(criterio: "contratacao.id in(${idsContratos.join(",")}) and tipoAditivo.classificacao in (\'PRAZO\',\'PRAZO_ACRESCIMO\',\'PRAZO_SUPRESSAO\')",campos: "id,dataAditivo,dataFinalNova,contratacao(id,ano,numeroProcesso, sequencial, anoProcesso,numeroTermo,situacao), entidade(id, nome), tipoAditivo(id, descricao, classificacao)").each{itemAditivos ->
    chave = itemAditivos.contratacao.id.toLong()
    if(mapaContratos[chave]){      
      mapaContratos[chave][\'aditivos\']<<[
        dataFinalNova: itemAditivos?.dataFinalNova?.format("dd/MM/yyyy")
      ]
    }    
    if(mapaContratos[chave].aditivos){
      novaDataA =  mapaContratos[chave].aditivos.collect{converteDataFormatada(it.dataFinalNova)}.sort().last()
      mapaContratos[chave].dataFimVigencia = (novaDataA >= converteDataFormatada(mapaContratos[chave].dataFimVigencia))? novaDataA.format("dd/MM/yyyy") : mapaContratos[chave].dataFimVigencia  
    }    
  }
}
```

Esta seção busca os aditivos de prazo e atualiza a data de fim de vigência dos contratos:

*   `idsContratos = mapaContratos.keySet()`: Obtém todos os IDs dos contratos já mapeados.
*   `idsContratos.collate(50).each{idsContratos-> ... }`: Itera sobre os IDs dos contratos em lotes de 50 para otimizar a busca de aditivos.
*   `Dados.contratos.v1.contratacoes.aditivos.busca(...)`: Busca aditivos de prazo (`PRAZO`, `PRAZO_ACRESCIMO`, `PRAZO_SUPRESSAO`) para os contratos do lote atual.
*   `itemAditivos -> ...`: Para cada aditivo encontrado:
    *   O aditivo é adicionado à lista `aditivos` do contrato correspondente no `mapaContratos`.
    *   A `dataFimVigencia` do contrato é atualizada para a data final mais recente entre a data de fim de vigência original e as datas finais dos aditivos de prazo.

### Encerramento de Contratações e Geração de Arquivo de Log

```groovy
//Faz encerramento das contratacoes e gera arquivo log
mapaContratos = mapaContratos.values().groupBy{it.entidade}
mapaContratos.each{chave,valor->
  nomeArquivo = [chave+"_Contratacoes",".csv"].join("_")
  arquivoCsv = Arquivo.novo(nomeArquivo, \'txt\', [encoding: \'UTF-8\', entreAspas: \'N\', delimitador:\';\'])
  arquivoCsv.escrever("id;Sequencial;Exercicio;dataInicioVigencia;dataFimVigencia")
  arquivoCsv.novaLinha()
      valor.each{it->
        if(it.entidade == "CAMARA MUNICIPAL DE LUZERNA"){
          if(converteDataFormatada(it.dataFimVigencia) <= dataEncerramento){
            //dataEnc = it.dataFimVigencia == "01/01/1800"? dataEncerramento : converteDataFormatada(it.dataFimVigencia)
            PostEncerramentoContratacao(it.entidade,it.idContratacao,it.ano,dataEncerramento)  
            arquivoCsv.escrever(it.idContratacao+";"+it.sequencial+";"+it.ano+";"+it.dataInicioVigencia+";"+it.dataFimVigencia)
            arquivoCsv.novaLinha()
          }
        }  	
    } 
  Resultado.arquivo(arquivoCsv, nomeArquivo)
  }		
```

Esta seção agrupa os contratos por entidade, processa o encerramento e gera os arquivos de log:

*   `mapaContratos = mapaContratos.values().groupBy{it.entidade}`: Reorganiza o `mapaContratos`, agrupando os contratos por entidade.
*   `mapaContratos.each{chave,valor-> ... }`: Itera sobre cada grupo de contratos (por entidade):
    *   `nomeArquivo = [chave+"_Contratacoes",".csv"].join("_")`: Define o nome do arquivo CSV de log para a entidade atual.
    *   `arquivoCsv = Arquivo.novo(...)`: Cria um novo arquivo CSV para o log, com codificação UTF-8 e delimitador de ponto e vírgula.
    *   `arquivoCsv.escrever(...)` e `arquivoCsv.novaLinha()`: Escreve o cabeçalho no arquivo CSV de log.
    *   `valor.each{it-> ... }`: Itera sobre cada contrato dentro do grupo da entidade atual:
        *   `if(it.entidade == "CAMARA MUNICIPAL DE LUZERNA")`: Filtra os contratos para processar apenas os da "CAMARA MUNICIPAL DE LUZERNA".
        *   `if(converteDataFormatada(it.dataFimVigencia) <= dataEncerramento)`: Verifica se a data de fim de vigência do contrato é menor ou igual à `dataEncerramento` fornecida.
        *   `PostEncerramentoContratacao(...)`: Se as condições forem atendidas, chama a função auxiliar para realizar a requisição de encerramento do contrato via API.
        *   `arquivoCsv.escrever(...)` e `arquivoCsv.novaLinha()`: Escreve os detalhes do contrato encerrado no arquivo CSV de log.
    *   `Resultado.arquivo(arquivoCsv, nomeArquivo)`: Associa o arquivo CSV de log gerado ao resultado final do script, tornando-o disponível para download.

### Função Auxiliar `converteDataFormatada`

```groovy
def converteDataFormatada(NovaData){
	return Datas.data(NovaData[6..9].toInteger(),NovaData[3..4].toInteger(),NovaData[0..1].toInteger())
}
```

Esta função auxiliar converte uma string de data no formato "dd/MM/yyyy" para um objeto de data Groovy.

### Função Auxiliar `PostEncerramentoContratacao`

```groovy
def PostEncerramentoContratacao(entidade,idContratacao,ExercicioContratacao,dataEncerramento){
      obj = [
          id:idContratacao.toInteger(),
          dataEncerramento: dataEncerramento.format("yyyy-MM-dd")
      ]
  	  token = tokens[entidade]
      url = "https://services.contratos.betha.cloud/contratacao-services/api/exercicios/${ExercicioContratacao}/contratacoes/${idContratacao}/encerrar"
      servico = Http.servico(url).chaveIntegracao(token).POST(obj,Http.JSON)
   
}
```

Esta função auxiliar é responsável por realizar a chamada de API para encerrar um contrato:

*   `obj = [...]`: Cria um objeto JSON com o ID do contrato e a data de encerramento formatada.
*   `token = tokens[entidade]`: Obtém o token de integração da entidade correspondente.
*   `url = ...`: Constrói a URL completa para a requisição de encerramento da API.
*   `servico = Http.servico(url).chaveIntegracao(token).POST(obj,Http.JSON)`: Realiza a requisição HTTP POST para a API, enviando o objeto `obj` como JSON e utilizando a chave de integração para autenticação.

## Código Completo

```groovy
dataEncerramento = parametros.p_anoEncerramento.valor
anos = []

for(i=2010;i<=2024;i++){
  	anos<<i
}

tokens = [
         "MUNICIPIO DE LUZERNA":"760688d3-f5e0-46f5-87ac-2edb8801388b",
         "CAMARA MUNICIPAL DE LUZERNA":"ee746119-d4a9-4bc5-89fa-90c0dce56efd",
  		 "FUNDO MUNICIPAL SAUDE LUZERNA":"f1be864b-94d5-4c0c-9280-a803dea99e88"
]

fonteContratacoes = Dados.contratos.v1.contratacoes;
filtroContratacoes = "dataAssinatura >= ${anos[0]}-01-01 and dataAssinatura <= ${anos[-1]}-12-31 and situacao = \'EXECUCAO\'";
mapaContratos = [:]

dadosContratacoes = fonteContratacoes.busca(criterio: filtroContratacoes,campos: "entidade(id,nome), id, numeroProcesso, anoProcesso, sequencial, numeroTermo, ano, dataAssinatura,dataInicioVigencia,dataFimVigencia")
percorrer (dadosContratacoes) { itemContratacoes ->
  chave = itemContratacoes.id
  if(!mapaContratos[chave]){
    mapaContratos[chave]=[
      entidade:itemContratacoes.entidade.nome,
      idEntidade: itemContratacoes.entidade.id,
      idContratacao: itemContratacoes.id,
      numeroProcesso:itemContratacoes.numeroProcesso,
      anoProcesso:itemContratacoes.anoProcesso,
      sequencial:itemContratacoes.sequencial,
      numeroTermo:itemContratacoes.numeroTermo,
      ano:itemContratacoes.ano,
      dataAssinatura:itemContratacoes.dataAssinatura.format("dd/MM/yyyy"),
      dataInicioVigencia:itemContratacoes.dataInicioVigencia.format("dd/MM/yyyy"),
      dataFimVigencia:itemContratacoes.dataFimVigencia.format("dd/MM/yyyy"),
      aditivos:[]
    ]
  }
}

//Busca aditivos e vincula a seus contratos caso haverem
idsContratos = mapaContratos.keySet()
idsContratos.collate(50).each{idsContratos->
  Dados.contratos.v1.contratacoes.aditivos.busca(criterio: "contratacao.id in(${idsContratos.join(",")}) and tipoAditivo.classificacao in (\'PRAZO\',\'PRAZO_ACRESCIMO\',\'PRAZO_SUPRESSAO\')",campos: "id,dataAditivo,dataFinalNova,contratacao(id,ano,numeroProcesso, sequencial, anoProcesso,numeroTermo,situacao), entidade(id, nome), tipoAditivo(id, descricao, classificacao)").each{itemAditivos ->
    chave = itemAditivos.contratacao.id.toLong()
    if(mapaContratos[chave]){      
      mapaContratos[chave][\'aditivos\']<<[
        dataFinalNova: itemAditivos?.dataFinalNova?.format("dd/MM/yyyy")
      ]
    }    
    if(mapaContratos[chave].aditivos){
      novaDataA =  mapaContratos[chave].aditivos.collect{converteDataFormatada(it.dataFinalNova)}.sort().last()
      mapaContratos[chave].dataFimVigencia = (novaDataA >= converteDataFormatada(mapaContratos[chave].dataFimVigencia))? novaDataA.format("dd/MM/yyyy") : mapaContratos[chave].dataFimVigencia  
    }    
  }
}

//Faz encerramento das contratacoes e gera arquivo log
mapaContratos = mapaContratos.values().groupBy{it.entidade}
mapaContratos.each{chave,valor->
  nomeArquivo = [chave+"_Contratacoes",".csv"].join("_")
  arquivoCsv = Arquivo.novo(nomeArquivo, \'txt\', [encoding: \'UTF-8\', entreAspas: \'N\', delimitador:\';\'])
  arquivoCsv.escrever("id;Sequencial;Exercicio;dataInicioVigencia;dataFimVigencia")
  arquivoCsv.novaLinha()
      valor.each{it->
        if(it.entidade == "CAMARA MUNICIPAL DE LUZERNA"){
          if(converteDataFormatada(it.dataFimVigencia) <= dataEncerramento){
            //dataEnc = it.dataFimVigencia == "01/01/1800"? dataEncerramento : converteDataFormatada(it.dataFimVigencia)
            PostEncerramentoContratacao(it.entidade,it.idContratacao,it.ano,dataEncerramento)  
            arquivoCsv.escrever(it.idContratacao+";"+it.sequencial+";"+it.ano+";"+it.dataInicioVigencia+";"+it.dataFimVigencia)
            arquivoCsv.novaLinha()
          }
        }  	
    } 
  Resultado.arquivo(arquivoCsv, nomeArquivo)
  }		


def converteDataFormatada(NovaData){
	return Datas.data(NovaData[6..9].toInteger(),NovaData[3..4].toInteger(),NovaData[0..1].toInteger())
}

def PostEncerramentoContratacao(entidade,idContratacao,ExercicioContratacao,dataEncerramento){
      obj = [
          id:idContratacao.toInteger(),
          dataEncerramento: dataEncerramento.format("yyyy-MM-dd")
      ]
  	  token = tokens[entidade]
      url = "https://services.contratos.betha.cloud/contratacao-services/api/exercicios/${ExercicioContratacao}/contratacoes/${idContratacao}/encerrar"
      servico = Http.servico(url).chaveIntegracao(token).POST(obj,Http.JSON)
   
}
```

