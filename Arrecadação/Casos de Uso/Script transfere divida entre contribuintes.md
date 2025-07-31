## 📄 Script para transferencia de dividas entre contribuintes


---

## 🧠 Código Completo

```groovy
//-------------------------------------------FONTES------------------------------------------------//
FONTE_TRIBUTOS = Dados.tributos.v2;
fonteContribuinte = FONTE_TRIBUTOS.contribuintes;
fonteImoveis = FONTE_TRIBUTOS.imoveis;
fonteDividas = FONTE_TRIBUTOS.dividas;

//-------------------------------------------PARAMETROS-------------------------------------------//
token = parametros.p_token.valor; 																	
contrDe = fonteContribuinte.busca(criterio: "id = " + parametros.p_contrDe.selecionado, primeiro: true) 
contrPara = fonteContribuinte.busca(criterio: "id = " + parametros.p_contrPara.selecionado, primeiro: true)
ano = parametros.p_ano.valor 
imovel = fonteImoveis.busca(criterio: "id = " + parametros.p_imovel.selecionado, primeiro: true) 


//-------------------------------------------LAYOUT----------------------------------------------//
idLotes = [];
urlBase = "https://tributos.betha.cloud/service-layer-tributos/api";
token = "bearer " + parametros.p_token.valor;
json = [];
MAX = 10; 																										//Quantidade de registros enviado em um lote
qtdLotes = 1;
idLancamentos = [];

enviar = { servico, conteudo ->  
  urlServico = urlBase + "/" + servico;
  servico = Http.servico(urlServico);
  servico.cabecalho('Content-Type', 'application/json');
  servico.cabecalho("Authorization", token).aceitarTipoMidia('application/json');
  resposta = servico.PATCH(conteudo, Http.JSON);
  imprimir '--> Lote Enviado' 
  
  sucesso = false;
  conteudo = '';
  idLote = ''; 
  
  
//-------------------------------------------RESPOSTA--------------------------------------------//  
  se (resposta.ehJson()) {
    json = resposta.json();
    idLote = json.idLote;
    sucesso = resposta.sucesso();
    conteudo = resposta.conteudo();
  }
  servico.close ();
  return [
    sucesso : sucesso,
    idLote  : idLote,
    conteudo: conteudo
  ]; 
}


//-------------------------------------------REENVIO--------------------------------------------//  
//Reenvia até que a mensagem de status seja PROCESSADO;

consultar = { servico, idLote ->
  statusLote = 'NAO_PROCESSADO';
  json = [];
  countP = 0;
  percorrer(enquanto: {statusLote != 'PROCESSADO'}) {
    if(countP == 0){
      imprimir "--> Consultando Lote: $idLote";
      countP++;
    }
    respostaGet = Http.servico( urlBase + "/${servico}/${idLote}")
    .cabecalho("Authorization", token)
    .cabecalho("Content-Type", "application/json")
    .aceitarTipoMidia('application/json')
    .GET();
    
    imprimir "## Conteúdo: ${respostaGet.conteudo()}"
    resp = respostaGet.json();
    statusLote = resp.statusLote;
    esperar 15.segundo;
    if (statusLote == 'PROCESSADO') {
      resp.retorno.each{ j ->
        if(j?.status != 'ERRO'){
          json << [
            idIntegracao: j.idIntegracao,
            idGerado: j.idGerado.id
          ];
        } else {
          json << [
            erro: j.status,
            mensagem: j.mensagem
          ];
        }
      }
    }
    if(statusLote == 'PROCESSADO_COM_ERRO'){
      suspender "Erro no envio do JSON"
    }
  }
  return json;
}

//-------------------------------------------Fontes------------------------------------------------//

dadosDividas = fonteDividas.busca(criterio: "contribuinte.id = $contrDe.id and ano in ($ano) and idImovel = $imovel.id and situacao = 'ABERTO'");
qtdRegistros = dadosDividas.size();
imprimir "Serão enviado(s): " + qtdRegistros + " registro(s)"
dadosDividas.eachWithIndex{ itemDividas, index ->


//-------------------------------------------Layout----------------------------------------------//
  dadosRequisicao = [
    "idIntegracao": "TransferenciaDivida", 
    "dividas": [
      "idGerado": [ 
        "id": itemDividas.id 
      ],
      "idPessoa": contrPara.id
    ]
  ];
  json << dadosRequisicao;


//-------------------------------------------Envio-------------------------------------------//  
  se ((index > 0 && index % MAX == 0) || qtdRegistros <= index + 1) {
    imprimir '--> Enviando Lote: ' + qtdLotes +' com ' + json.size() +' Registro(s)';
    

    resposta = enviar('dividas',json);
    
    se (!resposta.sucesso) {
      imprimir '--> Tentando reenviar os dados em 10 segundos';
      esperar 10000;
      resposta = enviar('dividas',json);
    }
    se (!resposta.sucesso) {
      suspender '--> Resposta: ' + resposta.conteudo;
    } senao {
      idLotes << resposta.idLote;
      imprimir '--> Zerando Lote ...';
      json = [];
      qtdLotes ++;
    }
  }
}

//-------------------------------------------Retorno-------------------------------------------//
esperar 5.segundo;
imprimir '--> Fim do envio de dados, iniciando processo de consulta dos lotes...'
imprimir 'Lotes: ' + idLotes

idLotes.each{ lotes ->
  consultar('dividas',lotes);
}
imprimir '--> Fim da consulta dos dados...';
imprimir "-";
---

```
## 🔍 Explicações das Funções

### 🔄 `PARAMETROS`

        💡 p_contrDe : Contribuinte Origem
            lista simples (Dinâmica)
            Categoria da fonte: Geral
            Fonte: Listagem de contribuintes(v2)
            Valor: ID
            Descrição: Codigo,Nome,cpfCnpj
            Filtro: Codigo,Nome,cpfCnpj
            
        💡 p_contrPara : Contribuinte Destino
            lista simples (Dinâmica)
            Categoria da fonte: Geral
            Fonte: Listagem de contribuintes(v2)
            Valor: ID
            Descrição: Codigo,Nome,cpfCnpj
            Filtro: Codigo,Nome,cpfCnpj

        💡 p_ano : Anos das dívidas
            Tipo do dado: Caracter
            Obrigatório: Sim
            
        💡 p_imovel : Imóvel
            lista simples (Dinâmica)
            Categoria da fonte: Referentes
            Fonte: Listagem de imoveis (v2)
            Valor: ID
            Descrição: Codigo,Responsavel.nome,InscricaoImobiliariaFormatada
            Filtro: Codigo,Responsavel.nome,InscricaoImobiliariaFormatada

        💡 p_token : Token
            Tipo do dado: Caracter
            Valor padrão: TOKEN DA ENTIDADE
