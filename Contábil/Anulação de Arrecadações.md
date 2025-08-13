# Documentação do Script de Anulação de Arrecadações

Este script Groovy é projetado para automatizar o processo de anulação de arrecadações orçamentárias, com base em um conjunto de parâmetros de entrada. Ele busca arrecadações orçamentárias e extraorçamentárias, agrupa-as por banco e dia, e gera um payload JSON para anulação, que é então enviado para uma API. O script também lida com deduções de receita e recursos associados, ajustando os valores de anulação de acordo.

## Explicação Geral do Código

O script começa coletando parâmetros de entrada, como exercício, datas de início e fim, e receitas orçamentárias e extraorçamentárias a serem consideradas. Ele busca todas as arrecadações orçamentárias e extraorçamentárias dentro do período especificado e as agrupa em um mapa (`MapArrecadacoes`) com uma chave composta pelo banco e dia da arrecadação. Para cada arrecadação orçamentária, ele constrói um objeto de anulação com detalhes como exercício, data de lançamento, valor e motivo. O script também busca e inclui as deduções de receita e seus recursos associados, ajustando o valor da anulação. Finalmente, ele agrupa as anulações em lotes de 50 e as envia para a API de anulação de arrecadações orçamentárias via POST.

## Blocos de Código

### 1. Coleta de Parâmetros e Filtro de Receitas

```groovy
p_exercicio = parametros.p_exercicio.valor
p_dataIni = parametros.p_dataIni.valor.format("yyyy-MM-dd")
p_dataFim = parametros.p_dataFim.valor.format("yyyy-MM-dd")
p_receitaOrcamentarias = parametros?.p_receitaOrcamentarias?.selecionados?:nulo
ReceitasExtrasPermitidas = parametros.p_receitasExtraOrcamentarias?.selecionados?:nulo
ReceitasExtrasPermitidas = nulo
p_especificacao = nulo
p_dataParaLancamento = parametros.p_dataParaLancamento.valor.format("yyyy-MM-dd")


ReceitasOrcamentariasPermitidas = []


if(p_receitaOrcamentarias){
  ReceitasOrcamentariasPermitidas = Dados.contabilidade.v1.receitas.arrecadacoesOrcamentarias.busca(criterio: "entidade.id = ${contextoExecucao.idEntidade} and exercicio.ano = ${p_exercicio} and receitaOrcamentaria.numero in (${p_receitaOrcamentarias.join(",")})",campos: "receitaOrcamentaria(natureza(numero))").collect{it.receitaOrcamentaria.natureza.numero}
  if(!ReceitasOrcamentariasPermitidas.isEmpty()){
    ReceitasOrcamentariasPermitidas = ReceitasOrcamentariasPermitidas.unique()
  }
}
```

Este bloco inicial coleta os parâmetros de entrada, como exercício, datas e receitas. Ele formata as datas e, se houver receitas orçamentárias especificadas, busca os números de natureza correspondentes para usar como filtro. As receitas extraorçamentárias e especificações são inicializadas como nulas.

### 2. Busca e Mapeamento de Arrecadações Orçamentárias

```groovy
MapArrecadacoes = [:]

criterioArrecadacoesOrcamentarias = "entidade.id = ${contextoExecucao.idEntidade} and exercicio.ano = ${p_exercicio} and arrecadacao.data >= ${p_dataIni} and arrecadacao.data <= ${p_dataFim}"

if(ReceitasOrcamentariasPermitidas){
  criterioArrecadacoesOrcamentarias+= " and receitaOrcamentaria.natureza.numero in (${ReceitasOrcamentariasPermitidas.join(",")})"
}

criterioArrecadacoesExtraOrcamentarias =  "entidade.id = ${contextoExecucao.idEntidade} and exercicio.ano = ${p_exercicio} and arrecadacao.data >= ${p_dataIni} and arrecadacao.data <= ${p_dataFim}"

imprimir criterioArrecadacoesOrcamentarias

count = 0
Dados.contabilidade.v1.receitas.arrecadacoesOrcamentarias.busca(criterio:criterioArrecadacoesOrcamentarias,campos: "receitaOrcamentaria(id,natureza(numero,descricao),numero),exercicio(ano), entidade(id), valor, arrecadacao(id, valor, especificacao, contaBancariaEntidade(conta(banco(nome), agencia(numeroAgencia, digitoAgencia, nome), numero,digito,tipo)), data, exercicio(ano), entidade(nome))").each{ it ->

  if(!ReceitasOrcamentariasPermitidas && ReceitasExtrasPermitidas){
    return 
  }
  
  if(p_especificacao){
    if(!it.arrecadacao.especificacao in p_especificacao){
       return 
    }
  }
  
  banco = it.arrecadacao.contaBancariaEntidade.conta.banco.nome+" "+
    it.arrecadacao.contaBancariaEntidade.conta.agencia.numeroAgencia+"-"+
    it.arrecadacao.contaBancariaEntidade.conta.agencia.digitoAgencia+" "+
    it.arrecadacao.contaBancariaEntidade.conta.numero+"-"+
    it.arrecadacao.contaBancariaEntidade.conta.digito
  
  dia = it.arrecadacao.data.format("dd/MM/yyyy") 
  chave = [banco,dia]
  if(!MapArrecadacoes[chave]){
    MapArrecadacoes[chave] = [
      total:it.valor,
      totalExtras: 0,
      totalOrcamentarias:0,
      receitasExtraOrcamentarias:[],
      receitasOrcamentarias:[[
        idIntegracao: count.toString(),
        content:[
        	exercicio:p_exercicio,
            validaSaldo:true,
            arrecadacao:[
              id:it.arrecadacao.id
            ],
          data: p_dataParaLancamento,
          valor: it.valor,
          motivo:"Ajuste de receita orçamentaria",
          receitas:[[
         	receitaArrecadacao:[
            	id:it.receitaOrcamentaria.id
            ],
			valor:it.valor,
         	recursos: Dados.contabilidade.v1.recursos.receitas.arrecadacoes.busca(criterio: "entidade.id = ${contextoExecucao.idEntidade} and receitaArrecadacao.receitaOrcamentaria.id = ${it.receitaOrcamentaria.id} and receitaArrecadacao.arrecadacao.id = ${it.arrecadacao.id}",campos: "receitaArrecadacao(receitaOrcamentaria(id)), recurso(numero, id), valor, id").collect{[recursoArrecadacao:[id:it.recurso.id],valor:it.valor]}
         ]]
        ]
      ]
    ]]
  }else{
  	MapArrecadacoes[chave][\receitasOrcamentarias\\]<<[
        idIntegracao: count.toString(),
        content:[
        	exercicio:p_exercicio,
            validaSaldo:true,
            arrecadacao:[
              id:it.arrecadacao.id
            ],
          data: p_dataParaLancamento,
          valor: it.valor,
          motivo:"Ajuste de receita orçamentaria",
          receitas:[[
         	receitaArrecadacao:[
            	id:it.receitaOrcamentaria.id
            ],
			valor:it.valor,
         	recursos: Dados.contabilidade.v1.recursos.receitas.arrecadacoes.busca(criterio: "entidade.id = ${contextoExecucao.idEntidade} and receitaArrecadacao.receitaOrcamentaria.id = ${it.receitaOrcamentaria.id} and receitaArrecadacao.arrecadacao.id = ${it.arrecadacao.id}",campos: "receitaArrecadacao(receitaOrcamentaria(id)), recurso(numero, id), valor, id").collect{[recursoArrecadacao:[id:it.recurso.id],valor:it.valor]}
         ]]
        ]
      ]
  }
  count++
}
```

Este bloco constrói o critério de busca para as arrecadações orçamentárias e as busca no sistema. Para cada arrecadação encontrada, ele extrai as informações do banco e a data para criar uma chave de agrupamento. As arrecadações são então adicionadas ao `MapArrecadacoes`, com um objeto de anulação contendo todos os detalhes necessários, incluindo os recursos associados.

### 3. Busca e Mapeamento de Arrecadações Extraorçamentárias

```groovy
Dados.contabilidade.v1.receitas.arrecadacoesExtraorcamentarias.busca(criterio: criterioArrecadacoesExtraOrcamentarias,campos: "valor, receitaExtraExercicio(receitaExtra(descricao)), arrecadacao(id, valor, especificacao, contaBancariaEntidade(conta(banco(nome), agencia(numeroAgencia, digitoAgencia, nome), numero,digito,tipo)), data, exercicio(ano), entidade(nome))").each { it ->
  

  if(ReceitasOrcamentariasPermitidas && !ReceitasExtrasPermitidas){
    return
  }
  
  if(ReceitasOrcamentariasPermitidas && ReceitasExtrasPermitidas){
    if(!it.receitaExtraExercicio.receitaExtra.descricao in ReceitasExtrasPermitidas){
    	    return
    }
  }
    if(p_especificacao){
    if(!it.arrecadacao.especificacao in p_especificacao){
       return 
    }
  }
  
  banco = it.arrecadacao.contaBancariaEntidade.conta.banco.nome + " " +
    it.arrecadacao.contaBancariaEntidade.conta.agencia.numeroAgencia + "-" +
    it.arrecadacao.contaBancariaEntidade.conta.agencia.digitoAgencia + " " +
    it.arrecadacao.contaBancariaEntidade.conta.numero + "-" +
    it.arrecadacao.contaBancariaEntidade.conta.digito
  
  dia = it.arrecadacao.data.format("dd/MM/yyyy")
  
  chave = [banco, dia]
  
  if(!ReceitasOrcamentariasPermitidas && ReceitasExtrasPermitidas){
    if(!MapArrecadacoes[chave]){
      MapArrecadacoes[chave] = [
        total:it.valor,
        totalExtras: 0,
        totalOrcamentarias:0,
        receitasExtraOrcamentarias:[],
        receitasOrcamentarias:[]
      ]
    }
  }
  
  if(MapArrecadacoes[chave]) {
    existe = MapArrecadacoes[chave][\receitasExtraOrcamentarias\\]find{r-> r.descricao == it.receitaExtraExercicio.receitaExtra.descricao}
    if(existe){
      existe.valor+=it.valor
    }else{
      MapArrecadacoes[chave][\receitasExtraOrcamentarias\\]<<[
        descricao: it.receitaExtraExercicio.receitaExtra.descricao,
        valor: it.valor
      ]
    }
    
    MapArrecadacoes[chave][\total\\] += it.valor
  } 
  
}
```

Este bloco busca as arrecadações extraorçamentárias e as adiciona ao `MapArrecadacoes`. Ele verifica se a receita extraorçamentária já existe no mapa para o mesmo banco e dia e, em caso afirmativo, atualiza o valor. Caso contrário, adiciona uma nova entrada. O valor total da arrecadação no mapa também é atualizado.

### 4. Geração do Quadro Resumo

```groovy
MapaResumo = [:]

MapArrecadacoes.each { chave, valor ->
  chaveResumo = chave[0]
  if (!MapaResumo[chaveResumo]) {
    MapaResumo[chaveResumo] = [
      totalOrcamentarias: valor.totalOrcamentarias ?: 0,
      totalExtras: valor.totalExtras ?: 0
    ]
  } else {
    MapaResumo[chaveResumo].totalOrcamentarias += valor.totalOrcamentarias ?: 0
    MapaResumo[chaveResumo].totalExtras += valor.totalExtras ?: 0
  }
}

quadroResumo = MapaResumo.collect{chave,valor-> [banco:chave,
                                                 totalExtras:valor.totalExtras,
                                                 totalOrcamentarias:valor.totalOrcamentarias,
                                                 totalGeralExtras:0,
                                                 totalGeralOrcamentarias:0,
                                                 totalGeral:0
                                                ]}

totalGeralExtras = quadroResumo.sum{it.totalExtras}
totalGeralOrcamentarias = quadroResumo.sum{it.totalOrcamentarias}
totalGeral = totalGeralExtras+totalGeralOrcamentarias
listaArrecadacoes = MapArrecadacoes.collect{chave,valor-> [banco:chave[0]?:"",
                                                           diaArrecadacao:chave[1]?:"",
                                                           total:valor.total?:0,
                                                           totalExtras:valor.totalExtras?:0,
                                                           totalOrcamentarias:valor.totalOrcamentarias?:0,
                                                           totalGeralExtras:0,
                                                           totalGeralOrcamentarias:0,
                                                           totalGeral:0,
                                                           receitasExtraOrcamentarias:valor.receitasExtraOrcamentarias?:[],
                                                           receitasOrcamentarias:valor.receitasOrcamentarias?:[],
                                                           quadroResumos:[]
                                                          ]}
```

Este bloco cria um `MapaResumo` para consolidar os totais de arrecadações orçamentárias e extraorçamentárias por banco. Ele então gera um `quadroResumo` com os totais por banco e calcula os totais gerais. A `listaArrecadacoes` é criada para formatar os dados para a saída final.

### 5. Busca de Deduções e Ajuste de Valores

```groovy
listaPost = []


listaArrecadacoes.each{receitasOrcamentarias->
 
  receitasOrcamentarias.receitasOrcamentarias.each{anulacao->
    
    anulacao.content.receitas.each{receita->
      deducoesReceita = []
      
      Dados.contabilidade.v1.deducao.arrecadacaoOrcamentaria.busca(criterio:" entidade.id = ${contextoExecucao.idEntidade} and exercicio.ano = ${p_exercicio} and receitaArrecadacao.receitaOrcamentaria.id = ${receita.receitaArrecadacao.id} and receitaArrecadacao.arrecadacao.id = ${anulacao.content.arrecadacao.id}",campos: "valor, exercicio(ano), entidade(id), receitaArrecadacao(receitaOrcamentaria(natureza(numero, id), id, numero)), id,deducaoReceitaExercicio.id,deducaoReceitaExercicio.deducaoReceita.id").each{it ->
        
        idDeducao = it.id
        idDeducao2 = it.deducaoReceitaExercicio.deducaoReceita.id
        valorDeducao = it.valor
        recursosDeducao = []
        Dados.contabilidade.v1.recurso.deducao.arrecadacaoOrcamentaria.busca(criterio: "deducaoArrecadacao.id = ${idDeducao}",campos: "recurso(id), id, deducaoArrecadacao(id),valor").each{ itemArrecadacaoOrcamentaria ->
          idRecurso = itemArrecadacaoOrcamentaria.recurso.id
          valorRecurso = itemArrecadacaoOrcamentaria.valor
          recursosDeducao<<[
            recursoDeducao:[
              id:idRecurso
            ],
            valor: valorRecurso
          ]
        }
        deducoesReceita<<[
          deducaoArrecadacao:[
            id:idDeducao2
          ],
          valor: valorDeducao,
          recursos:recursosDeducao
        ]
      }
    
      if(deducoesReceita){
        receita.deducoes = deducoesReceita
        valorDeduzido = deducoesReceita.sum{it.valor}
        anulacao.content.valor -= valorDeduzido
        deducoesReceita = []
      }
    }
    listaPost<<anulacao
  }
}
```

Este bloco percorre a `listaArrecadacoes` e, para cada anulação, busca as deduções de receita associadas. Ele coleta os detalhes de cada dedução, incluindo os recursos, e os adiciona ao objeto da receita. O valor da anulação é então ajustado subtraindo o valor total das deduções. Os objetos de anulação ajustados são adicionados à `listaPost`.

### 6. Envio para a API

```groovy
imprimir JSON.escrever(listaPost)

listaPost.collate(50).each{receitasOrcamentarias ->
	url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/anulacoes-arrecadacoes-orcamentarias"
    servico = Http.servico(url).chaveIntegracao(Variavel.CHAVE_INTEGRACAO).POST(receitasOrcamentarias,Http.JSON)
    resposta = servico.json()
    imprimir JSON.escrever(resposta)
}
```

Este bloco final agrupa a `listaPost` em lotes de 50 e envia cada lote para a API de anulação de arrecadações orçamentárias via POST. A resposta da API é impressa para fins de log e depuração.

## Código Completo

```groovy
p_exercicio = parametros.p_exercicio.valor
p_dataIni = parametros.p_dataIni.valor.format("yyyy-MM-dd")
p_dataFim = parametros.p_dataFim.valor.format("yyyy-MM-dd")
p_receitaOrcamentarias = parametros?.p_receitaOrcamentarias?.selecionados?:nulo
ReceitasExtrasPermitidas = parametros.p_receitasExtraOrcamentarias?.selecionados?:nulo
ReceitasExtrasPermitidas = nulo
p_especificacao = nulo
p_dataParaLancamento = parametros.p_dataParaLancamento.valor.format("yyyy-MM-dd")


ReceitasOrcamentariasPermitidas = []


if(p_receitaOrcamentarias){
  ReceitasOrcamentariasPermitidas = Dados.contabilidade.v1.receitas.arrecadacoesOrcamentarias.busca(criterio: "entidade.id = ${contextoExecucao.idEntidade} and exercicio.ano = ${p_exercicio} and receitaOrcamentaria.numero in (${p_receitaOrcamentarias.join(",")})",campos: "receitaOrcamentaria(natureza(numero))").collect{it.receitaOrcamentaria.natureza.numero}
  if(!ReceitasOrcamentariasPermitidas.isEmpty()){
    ReceitasOrcamentariasPermitidas = ReceitasOrcamentariasPermitidas.unique()
  }
}


MapArrecadacoes = [:]

criterioArrecadacoesOrcamentarias = "entidade.id = ${contextoExecucao.idEntidade} and exercicio.ano = ${p_exercicio} and arrecadacao.data >= ${p_dataIni} and arrecadacao.data <= ${p_dataFim}"

if(ReceitasOrcamentariasPermitidas){
  criterioArrecadacoesOrcamentarias+= " and receitaOrcamentaria.natureza.numero in (${ReceitasOrcamentariasPermitidas.join(",")})"
}

criterioArrecadacoesExtraOrcamentarias =  "entidade.id = ${contextoExecucao.idEntidade} and exercicio.ano = ${p_exercicio} and arrecadacao.data >= ${p_dataIni} and arrecadacao.data <= ${p_dataFim}"

imprimir criterioArrecadacoesOrcamentarias

count = 0
Dados.contabilidade.v1.receitas.arrecadacoesOrcamentarias.busca(criterio:criterioArrecadacoesOrcamentarias,campos: "receitaOrcamentaria(id,natureza(numero,descricao),numero),exercicio(ano), entidade(id), valor, arrecadacao(id, valor, especificacao, contaBancariaEntidade(conta(banco(nome), agencia(numeroAgencia, digitoAgencia, nome), numero,digito,tipo)), data, exercicio(ano), entidade(nome))").each{ it ->

  if(!ReceitasOrcamentariasPermitidas && ReceitasExtrasPermitidas){
    return 
  }
  
  if(p_especificacao){
    if(!it.arrecadacao.especificacao in p_especificacao){
       return 
    }
  }
  
  banco = it.arrecadacao.contaBancariaEntidade.conta.banco.nome+" "+
    it.arrecadacao.contaBancariaEntidade.conta.agencia.numeroAgencia+"-"+
    it.arrecadacao.contaBancariaEntidade.conta.agencia.digitoAgencia+" "+
    it.arrecadacao.contaBancariaEntidade.conta.numero+"-"+
    it.arrecadacao.contaBancariaEntidade.conta.digito
  
  dia = it.arrecadacao.data.format("dd/MM/yyyy") 
  chave = [banco,dia]
  if(!MapArrecadacoes[chave]){
    MapArrecadacoes[chave] = [
      total:it.valor,
      totalExtras: 0,
      totalOrcamentarias:0,
      receitasExtraOrcamentarias:[],
      receitasOrcamentarias:[[
        idIntegracao: count.toString(),
        content:[
        	exercicio:p_exercicio,
            validaSaldo:true,
            arrecadacao:[
              id:it.arrecadacao.id
            ],
          data: p_dataParaLancamento,
          valor: it.valor,
          motivo:"Ajuste de receita orçamentaria",
          receitas:[[
         	receitaArrecadacao:[
            	id:it.receitaOrcamentaria.id
            ],
			valor:it.valor,
         	recursos: Dados.contabilidade.v1.recursos.receitas.arrecadacoes.busca(criterio: "entidade.id = ${contextoExecucao.idEntidade} and receitaArrecadacao.receitaOrcamentaria.id = ${it.receitaOrcamentaria.id} and receitaArrecadacao.arrecadacao.id = ${it.arrecadacao.id}",campos: "receitaArrecadacao(receitaOrcamentaria(id)), recurso(numero, id), valor, id").collect{[recursoArrecadacao:[id:it.recurso.id],valor:it.valor]}
         ]]
        ]
      ]
    ]]
  }else{
  	MapArrecadacoes[chave][\receitasOrcamentarias\\]<<[
        idIntegracao: count.toString(),
        content:[
        	exercicio:p_exercicio,
            validaSaldo:true,
            arrecadacao:[
              id:it.arrecadacao.id
            ],
          data: p_dataParaLancamento,
          valor: it.valor,
          motivo:"Ajuste de receita orçamentaria",
          receitas:[[
         	receitaArrecadacao:[
            	id:it.receitaOrcamentaria.id
            ],
			valor:it.valor,
         	recursos: Dados.contabilidade.v1.recursos.receitas.arrecadacoes.busca(criterio: "entidade.id = ${contextoExecucao.idEntidade} and receitaArrecadacao.receitaOrcamentaria.id = ${it.receitaOrcamentaria.id} and receitaArrecadacao.arrecadacao.id = ${it.arrecadacao.id}",campos: "receitaArrecadacao(receitaOrcamentaria(id)), recurso(numero, id), valor, id").collect{[recursoArrecadacao:[id:it.recurso.id],valor:it.valor]}
         ]]
        ]
      ]
  }
  count++
}

Dados.contabilidade.v1.receitas.arrecadacoesExtraorcamentarias.busca(criterio: criterioArrecadacoesExtraOrcamentarias,campos: "valor, receitaExtraExercicio(receitaExtra(descricao)), arrecadacao(id, valor, especificacao, contaBancariaEntidade(conta(banco(nome), agencia(numeroAgencia, digitoAgencia, nome), numero,digito,tipo)), data, exercicio(ano), entidade(nome))").each { it ->
  

  if(ReceitasOrcamentariasPermitidas && !ReceitasExtrasPermitidas){
    return
  }
  
  if(ReceitasOrcamentariasPermitidas && ReceitasExtrasPermitidas){
    if(!it.receitaExtraExercicio.receitaExtra.descricao in ReceitasExtrasPermitidas){
    	    return
    }
  }
    if(p_especificacao){
    if(!it.arrecadacao.especificacao in p_especificacao){
       return 
    }
  }
  
  banco = it.arrecadacao.contaBancariaEntidade.conta.banco.nome + " " +
    it.arrecadacao.contaBancariaEntidade.conta.agencia.numeroAgencia + "-" +
    it.arrecadacao.contaBancariaEntidade.conta.agencia.digitoAgencia + " " +
    it.arrecadacao.contaBancariaEntidade.conta.numero + "-" +
    it.arrecadacao.contaBancariaEntidade.conta.digito
  
  dia = it.arrecadacao.data.format("dd/MM/yyyy")
  
  chave = [banco, dia]
  
  if(!ReceitasOrcamentariasPermitidas && ReceitasExtrasPermitidas){
    if(!MapArrecadacoes[chave]){
      MapArrecadacoes[chave] = [
        total:it.valor,
        totalExtras: 0,
        totalOrcamentarias:0,
        receitasExtraOrcamentarias:[],
        receitasOrcamentarias:[]
      ]
    }
  }
  
  if(MapArrecadacoes[chave]) {
    existe = MapArrecadacoes[chave][\receitasExtraOrcamentarias\\]find{r-> r.descricao == it.receitaExtraExercicio.receitaExtra.descricao}
    if(existe){
      existe.valor+=it.valor
    }else{
      MapArrecadacoes[chave][\receitasExtraOrcamentarias\\]<<[
        descricao: it.receitaExtraExercicio.receitaExtra.descricao,
        valor: it.valor
      ]
    }
    
    MapArrecadacoes[chave][\total\\] += it.valor
  } 
  
}


MapaResumo = [:]

MapArrecadacoes.each { chave, valor ->
  chaveResumo = chave[0]
  if (!MapaResumo[chaveResumo]) {
    MapaResumo[chaveResumo] = [
      totalOrcamentarias: valor.totalOrcamentarias ?: 0,
      totalExtras: valor.totalExtras ?: 0
    ]
  } else {
    MapaResumo[chaveResumo].totalOrcamentarias += valor.totalOrcamentarias ?: 0
    MapaResumo[chaveResumo].totalExtras += valor.totalExtras ?: 0
  }
}

quadroResumo = MapaResumo.collect{chave,valor-> [banco:chave,
                                                 totalExtras:valor.totalExtras,
                                                 totalOrcamentarias:valor.totalOrcamentarias,
                                                 totalGeralExtras:0,
                                                 totalGeralOrcamentarias:0,
                                                 totalGeral:0
                                                ]}

totalGeralExtras = quadroResumo.sum{it.totalExtras}
totalGeralOrcamentarias = quadroResumo.sum{it.totalOrcamentarias}
totalGeral = totalGeralExtras+totalGeralOrcamentarias
listaArrecadacoes = MapArrecadacoes.collect{chave,valor-> [banco:chave[0]?:"",
                                                           diaArrecadacao:chave[1]?:"",
                                                           total:valor.total?:0,
                                                           totalExtras:valor.totalExtras?:0,
                                                           totalOrcamentarias:valor.totalOrcamentarias?:0,
                                                           totalGeralExtras:0,
                                                           totalGeralOrcamentarias:0,
                                                           totalGeral:0,
                                                           receitasExtraOrcamentarias:valor.receitasExtraOrcamentarias?:[],
                                                           receitasOrcamentarias:valor.receitasOrcamentarias?:[],
                                                           quadroResumos:[]
                                                          ]}


listaPost = []


listaArrecadacoes.each{receitasOrcamentarias->
 
  receitasOrcamentarias.receitasOrcamentarias.each{anulacao->
    
    anulacao.content.receitas.each{receita->
      deducoesReceita = []
      
      Dados.contabilidade.v1.deducao.arrecadacaoOrcamentaria.busca(criterio:" entidade.id = ${contextoExecucao.idEntidade} and exercicio.ano = ${p_exercicio} and receitaArrecadacao.receitaOrcamentaria.id = ${receita.receitaArrecadacao.id} and receitaArrecadacao.arrecadacao.id = ${anulacao.content.arrecadacao.id}",campos: "valor, exercicio(ano), entidade(id), receitaArrecadacao(receitaOrcamentaria(natureza(numero, id), id, numero)), id,deducaoReceitaExercicio.id,deducaoReceitaExercicio.deducaoReceita.id").each{it ->
        
        idDeducao = it.id
        idDeducao2 = it.deducaoReceitaExercicio.deducaoReceita.id
        valorDeducao = it.valor
        recursosDeducao = []
        Dados.contabilidade.v1.recurso.deducao.arrecadacaoOrcamentaria.busca(criterio: "deducaoArrecadacao.id = ${idDeducao}",campos: "recurso(id), id, deducaoArrecadacao(id),valor").each{ itemArrecadacaoOrcamentaria ->
          idRecurso = itemArrecadacaoOrcamentaria.recurso.id
          valorRecurso = itemArrecadacaoOrcamentaria.valor
          recursosDeducao<<[
            recursoDeducao:[
              id:idRecurso
            ],
            valor: valorRecurso
          ]
        }
        deducoesReceita<<[
          deducaoArrecadacao:[
            id:idDeducao2
          ],
          valor: valorDeducao,
          recursos:recursosDeducao
        ]
      }
    
      if(deducoesReceita){
        receita.deducoes = deducoesReceita
        valorDeduzido = deducoesReceita.sum{it.valor}
        anulacao.content.valor -= valorDeduzido
        deducoesReceita = []
      }
    }
    listaPost<<anulacao
  }
}

imprimir JSON.escrever(listaPost)

listaPost.collate(50).each{receitasOrcamentarias ->
	url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/anulacoes-arrecadacoes-orcamentarias"
    servico = Http.servico(url).chaveIntegracao(Variavel.CHAVE_INTEGRACAO).POST(receitasOrcamentarias,Http.JSON)
    resposta = servico.json()
    imprimir JSON.escrever(resposta)
}
```

