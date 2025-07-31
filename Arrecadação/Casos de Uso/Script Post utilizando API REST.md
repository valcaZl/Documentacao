## 📄 Script para utilização de API REST com obgetivo de inserção de informações em lote

  📥 Similar ao Patch, porem, com uma alteração na estrutura de envio.

  💡 Neste Script em especifico, são utilizadas duas fontes, para fazer o comparativo entre as duas e alimentar a variavel **lista** com somente a diferença entre as duas.



---

## 🧠 Código Completo

```groovy
//-------------------------------------------Fontes-------------------------------------------//
fonteEnderecos = Dados.tributos.v2.contribuintes.enderecos.busca(campos: "idContribuinte")
fonteContribuintes = Dados.tributos.v2.contribuintes.busca(campos: "id")
listaContribuintes = []
listaEndereco = []

//-------------------------------------------Percorrer-------------------------------------------//
percorrer (fonteContribuintes) { itemContribuintes ->
  listaContribuintes << itemContribuintes.id
}

percorrer (fonteEnderecos) { itemEnderecos ->
  listaEndereco << itemEnderecos.idContribuinte
}

lista = listaContribuintes.unique()-listaEndereco.unique()

//-------------------------------------------Layout-------------------------------------------//
lista.each{ item ->
  codigos = [];
  codigos << [
    idIntegracao: 'POST' + item,
    NomeAPI: [
      idPessoa: item,
      idLogradouro: 12182482,
      idBairro: 3065004,
      idMunicipio: 2595,
      cep: '36010001',
      numero: 'S/N',
      principal: 'SIM',
      ordem: 1
    ]
  ]

 //-------------------------------------------Parametros-------------------------------------------//
  json = Http.servico("URL_API")
  .cabecalho('Authorization','Bearer TOKEN_MUNICIPIO')
  .cabecalho('Content-Type','application/json')
  .POST(codigos,Http.JSON);

//-------------------------------------------Retorno-------------------------------------------//
  imprimir json.codigo() + ' - ' + json.conteudo()
  imprimir codigos
}
---

```
## 🔍 Explicações das Funções

### 🔄 `NomeAPI`

        ➡️ Api a qual deseja realizar a requisição.
  
        ⚠️ Há casos raros onde a API possui - em seu nome, nestes casos dever ser inserido 'api-api'.
  


### 🔄 `FONTES`

        ➡️ Fontes do banco de dados utilizadas para buscar a informação e alimentar ambas listas para comparação.
      

### 🔄 `URL_API`

        ➡️ URL da API que deseja, consultar Documentação disponibilizada pelo Produto.


### 🔄 `TOKEN_MUNICIPIO`

        ➡️ Token utilizado para identificar qual entidade deseja realizar a requisição, caso não possua o Token, deve ser gerado em plataforma disponivel.
