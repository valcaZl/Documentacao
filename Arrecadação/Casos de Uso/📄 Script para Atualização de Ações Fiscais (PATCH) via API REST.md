# 📄 Script para Atualização de Ações Fiscais (PATCH) via API REST

---

Este script tem como objetivo realizar a atualização em lote de ações fiscais, especificamente o campo `dhCriacaoAcaoFiscal`, utilizando a API REST do sistema de Gestão Fiscal. Ele busca ações fiscais com `dhCriacaoAcaoFiscal` nulo, itera sobre elas e envia requisições PATCH para a API, definindo uma data e hora padrão para o campo.

---

## 🧠 Código Completo

```
fonteAcaoFiscal = Dados.gestaoFiscal.v1.acaoFiscal;

varItem = []

arquivo = Arquivo.novo("Pessoas" + Datas.formatar(Datas.hoje(), "ddMMyyyy")+".txt", "txt", [encoding: "UTF-8", delimitador: ";"]);

filtroAcaoFiscal = "dhCriacaoAcaoFiscal is null"

dadosAcaoFiscal = fonteAcaoFiscal.busca(criterio: filtroAcaoFiscal).take(50)

percorrer (dadosAcaoFiscal) { itemAcaoFiscal ->
  varItem << itemAcaoFiscal.id
}

varItem.each { item ->
  body = Arquivo.novo('body.json', 'json')
  def envio = []
  
  envio << [  
    idIntegracao: "Patch" + item,
    acoesfiscais: [
      idGerado: [
        id: item
      ],       
      dhCriacaoAcaoFiscal: "2026-01-01T09:00:00Z"
    ]
  ]
  
  //-------------------------------------------Parametros-------------------------------------------//
  json = Http.servico("https://gestao-fiscal.betha.cloud/gestao-fiscal/service-layer/api/acoes-fiscais")
  .cabecalho('Authorization','Bearer 8fbec087-7679-4f7b-89fb-c1913f73f77a')
  .cabecalho('Content-Type','application/json')
  .PATCH(envio,Http.JSON);
  
  //-------------------------------------------Retorno-------------------------------------------//
  imprimir json.codigo() + ' - ' + json.conteudo()
  imprimir envio
}
```

---

## 🔍 Explicações das Funções

### 🔄 `FONTES`

As fontes de dados são responsáveis por fornecer as informações necessárias para o script. Neste caso, a fonte `Dados.gestaoFiscal.v1.acaoFiscal` é utilizada para acessar os dados das ações fiscais.

```
fonteAcaoFiscal = Dados.gestaoFiscal.v1.acaoFiscal;
```

### 📝 `VARIÁVEIS E ARQUIVO DE LOG`

São inicializadas variáveis para armazenar os IDs das ações fiscais e um arquivo de log para registrar informações sobre o processo.

```
varItem = []

arquivo = Arquivo.novo("Pessoas" + Datas.formatar(Datas.hoje(), "ddMMyyyy")+".txt", "txt", [encoding: "UTF-8", delimitador: ";"]);
```

### 🔎 `FILTRO E BUSCA DE DADOS`

Um filtro é aplicado para buscar ações fiscais onde o campo `dhCriacaoAcaoFiscal` é nulo. A busca é limitada a 50 registros para processamento em lote.

```
filtroAcaoFiscal = "dhCriacaoAcaoFiscal is null"

dadosAcaoFiscal = fonteAcaoFiscal.busca(criterio: filtroAcaoFiscal).take(50)
```

### 🔄 `PERCORRER E COLETAR IDs`

O script itera sobre os dados das ações fiscais encontradas e coleta os IDs de cada item, armazenando-os na variável `varItem`.

```
percorrer (dadosAcaoFiscal) { itemAcaoFiscal ->
  varItem << itemAcaoFiscal.id
}
```

### 📤 `ENVIO DE REQUISIÇÕES PATCH`

Para cada ID coletado, o script constrói um payload JSON e envia uma requisição PATCH para a API de ações fiscais. O `idIntegracao` é gerado dinamicamente e o campo `dhCriacaoAcaoFiscal` é definido com uma data e hora padrão.

```
varItem.each { item ->
  body = Arquivo.novo('body.json', 'json')
  def envio = []
  
  envio << [  
    idIntegracao: "Patch" + item,
    acoesfiscais: [
      idGerado: [
        id: item
      ],       
      dhCriacaoAcaoFiscal: "2026-01-01T09:00:00Z"
    ]
  ]
  
  //-------------------------------------------Parametros-------------------------------------------//
  json = Http.servico("https://gestao-fiscal.betha.cloud/gestao-fiscal/service-layer/api/acoes-fiscais")
  .cabecalho('Authorization','Bearer 8fbec087-7679-4f7b-89fb-c1913f73f77a')
  .cabecalho('Content-Type','application/json')
  .PATCH(envio,Http.JSON);
  
  //-------------------------------------------Retorno-------------------------------------------//
  imprimir json.codigo() + ' - ' + json.conteudo()
  imprimir envio
}
```

### 📊 `PARÂMETROS DA REQUISIÇÃO`

Os parâmetros da requisição incluem a URL do serviço, o cabeçalho de autorização (Bearer Token) e o tipo de conteúdo (application/json). A requisição é do tipo PATCH.

```
  json = Http.servico("https://gestao-fiscal.betha.cloud/gestao-fiscal/service-layer/api/acoes-fiscais")
  .cabecalho('Authorization','Bearer 8fbec087-7679-4f7b-89fb-c1913f73f77a')
  .cabecalho('Content-Type','application/json')
  .PATCH(envio,Http.JSON);
```

### ↩️ `RETORNO E LOG`

Após o envio da requisição, o script imprime o código de status e o conteúdo da resposta da API, além do payload enviado, para fins de depuração e log.

```
  imprimir json.codigo() + ' - ' + json.conteudo()
  imprimir envio
```
