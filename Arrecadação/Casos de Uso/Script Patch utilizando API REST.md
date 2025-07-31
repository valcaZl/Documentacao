## 📄 Script para utilização de API REST com obgetivo de inserção de informações em lote



---

## 🧠 Código Completo

```groovy
//-------------------------------------------Fontes-------------------------------------------//
fonteNotasFiscais = Dados.notaEletronica.v1.notasFiscais;
filtroNotasFiscais = "id in ()"
dadosNotasFiscais = fonteNotasFiscais.busca(criterio: filtroNotasFiscais,campos: "id")
notas = [];

//-------------------------------------------Percorrer-------------------------------------------//
percorrer (dadosNotasFiscais) { itemNotasFiscais ->
  varItem << itemNotasFiscais.id
}

//-------------------------------------------Layout-------------------------------------------//
varItem.each { item ->
  body = Arquivo.novo('body.json', 'json')
  def envio = []
  
  envio << [  
    idIntegracao: "Patch" + item,
    NomeAPI: [
      idGerado: [
        id: item
      ],       
      DadoAPI: 123456,
      DadoAPI2: "TESTE",
      DadoAPI3: "TESTE"
    ]
  ]
  
  //-------------------------------------------Parametros-------------------------------------------//
  json = Http.servico("URL_API")
  .cabecalho('Authorization','Bearer TOKEN_MUNICIPIO')
  .cabecalho('Content-Type','application/json')
  .PATCH(envio,Http.JSON);
  
  //-------------------------------------------Retorno-------------------------------------------//
  imprimir json.codigo() + ' - ' + json.conteudo()
  imprimir envio
}
---

```
## 🔍 Explicações das Funções

### 🔄 `NomeAPI`

        ➡️ Api a qual deseja realizar a requisição.
  
        ⚠️ Há casos raros onde a API possui - em seu nome, nestes casos dever ser inserido 'api-api'.
  


### 🔄 `FONTES`

        ➡️ Fontes do banco de dados utilizadas para buscar a informação e alimentar a variavel **varItem** com os IDs necessarios para alteração.

  

### 🔄 `URL_API`

        ➡️ URL da API que deseja, consultar Documentação disponibilizada pelo Produto.


### 🔄 `TOKEN_MUNICIPIO`

        ➡️ Token utilizado para identificar qual entidade deseja realizar a requisição, caso não possua o Token, deve ser gerado em plataforma disponivel.
