## 📄 Script para alteração da Data de Lancamento de um Débito


---

## 🧠 Código Completo

```groovy
//-------------------------------------------Fontes-------------------------------------------//
fonteDebitos = Dados.tributos.v2.debitos;
filtroDebitos = "nroParcela = ${parametros.NumeroParcela.valor} and idLancamento = ${parametros.NumeroLancamento.valor} and situacao = 'ABERTO'"
novadata = parametros.DataDelancamento.valor
Datas.ano(novadata)
dadosDebitos = fonteDebitos.busca(criterio: filtroDebitos,campos: "id, idContribuinte")

//-------------------------------------------Percorrer-------------------------------------------//
percorrer (dadosDebitos) { itemDebitos ->

//-------------------------------------------Layout-------------------------------------------//
  contribuinte = item.idContribuinte
  iddebito = item.id
  envio = [];
  envio << [  
    idIntegracao: "Post "+iddebito,
    guias: [
      idGerado: [
        id: iddebito
      ],
      idPessoas:contribuinte,
      idPessoaAtual:contribuinte,
      dataCredito: novadata.format('yyyy-MM-dd'),
    ]
    
  ]
}

//-------------------------------------------Parametros-------------------------------------------//
envio =  JSON.escrever(envio)    
json = Http.servico("NomeAPI")
.cabecalho('Authorization','Bearer TOKEN_MUNICIPIO')
.cabecalho('Content-Type','application/json')
.POST(envio,Http.JSON);

//-------------------------------------------Retorno-------------------------------------------//
imprimir json.codigo() + ' - ' + json.conteudo()
imprimir envio
---

```
## 🔍 Explicações das Funções

### 🔄 `URL_API`

        ➡️ Criar os parametros NumeroLancamento(Numero), NumeroParcela(Numero) e novadata(Data)        
        ⚠️ utilizar /guias com o URL disponibilizado em documentação
  
### 🔄 `NomeAPI`

        ➡️ Api a qual deseja realizar a requisição.  
        ⚠️ Há casos raros onde a API possui - em seu nome, nestes casos dever ser inserido 'api-api'.
  


### 🔄 `FONTES`

        ➡️ Fontes do banco de dados utilizadas para buscar a informação e alimentar a variavel iddebito


### 🔄 `TOKEN_MUNICIPIO`

        ➡️ Token utilizado para identificar qual entidade deseja realizar a requisição, caso não possua o Token, deve ser gerado em plataforma disponivel.
