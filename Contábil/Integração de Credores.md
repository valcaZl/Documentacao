# Documentação do Script de Integração de Credores

Este script Groovy é responsável por automatizar a integração de dados de credores, incluindo agências bancárias e contas correntes, a partir de um arquivo CSV. Ele realiza a validação de CPF/CNPJ, busca por agências e credores já cadastrados no sistema e, se necessário, cadastra novas agências e credores via chamadas de API. Por fim, associa e cadastra as contas bancárias aos respectivos credores.

## Explicação Geral do Código

O script lê um arquivo CSV contendo informações de credores (nome, CPF/CNPJ, banco, agência e conta corrente). Ele pré-carrega um mapa de agências bancárias existentes no sistema para otimizar as buscas. Para cada linha do CSV, o script extrai e valida o CPF/CNPJ, determina o tipo de pessoa (física ou jurídica) e busca o ID do banco correspondente. Em seguida, verifica se a agência bancária já está cadastrada. Caso não esteja, a agência é cadastrada via API. O script então busca o ID do credor no sistema e, se o credor não existir, ele é cadastrado. Finalmente, as contas bancárias são associadas e cadastradas para cada credor, com tratamento para múltiplas contas e atualização de contas existentes. As operações de cadastro e atualização são realizadas em lotes via chamadas de API para otimizar o desempenho.

## Blocos de Código

### 1. Mapeamento de Agências Bancárias e Definição de Regex

```groovy
//busca todas agencias bancarias cadastradas no cloud e retorna um mapa com o numero e digito como chave (123-3) e o id como valor
mapAgenciasBancarias = Dados.contabilidade.v1.agenciasBancaria.busca(campos: "nome, numeroAgencia, digitoAgencia, numeroEndereco,banco.id").collectEntries{[
  ([
    agencia:it.numeroAgencia.concat(it.digitoAgencia?"-"+it.digitoAgencia:""),
    idBanco:it.banco.id
  ]):[id:it.id]
]
                                                                                                                                                          }
regexCNPJ = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/
regexCPF  = /^\d{3}\.\d{3}\.\d{3}-\d{2}$/
```

Este bloco inicializa um mapa (`mapAgenciasBancarias`) com todas as agências bancárias cadastradas no sistema, usando uma chave composta pelo número da agência (com dígito, se houver) e o ID do banco. Isso permite uma busca rápida por agências existentes. Também define expressões regulares (`regexCNPJ` e `regexCPF`) para validar e formatar números de CPF e CNPJ.

### 2. Leitura do CSV e Processamento Inicial dos Credores

```groovy
p_arquivo = parametros.p_arquivo.valor
arquivo = Arquivo.ler(p_arquivo, \'csv\');

credores = []

percorrer(enquanto: {arquivo.contemProximaLinha()}) {
  linha = arquivo.lerLinha()
  campos = linha.split(\

  if(!(campos.size()<5)){
    idBanco = BuscaIdBancoFebraban(campos[2])
    cpfCnpj = campos[1]
    
    if(cpfCnpj.contains(" ")){
          cpfCnpj = cpfCnpj.split(" ")[0]
    }

    if(cpfCnpj ==~ regexCPF){
      tipoPessoa = "FISICA"
      cpfCnpj = cpfCnpj.replaceAll(/[-.\/]/, "")
    }else if(cpfCnpj ==~ regexCNPJ){
      tipoPessoa = "JURIDICA"
      cpfCnpj = cpfCnpj.replaceAll(/[-.\/]/, "")
    }
	
    credores<< [
      nome: campos[0],
      cpfCnpj:cpfCnpj,
      tipoPessoa:tipoPessoa,
      banco:idBanco,
      idCredor:null,
      agencia:campos[3],
      agenciaCadastrada: mapAgenciasBancarias[[agencia:campos[3],idBanco:idBanco]]?true:false,
      contaCorrente: campos[4]
    ]
  }
}


credores = credores.unique()
```

Este bloco lê o arquivo CSV linha por linha. Para cada linha, ele extrai os campos relevantes (nome, CPF/CNPJ, banco, agência, conta corrente), valida e formata o CPF/CNPJ, e determina o tipo de pessoa. Ele também utiliza a função `BuscaIdBancoFebraban` para obter o ID do banco e verifica se a agência já está cadastrada no `mapAgenciasBancarias`. Os dados de cada credor são armazenados em uma lista (`credores`), que é então deduplicada.

### 3. Cadastro de Agências Bancárias Não Cadastradas

```groovy
agenciasNaoCadastradas = credores.findAll{!it.agenciaCadastrada}

if(agenciasNaoCadastradas){
  cadastrarAgencias(agenciasNaoCadastradas)
}else{
  //habilitar caso execução continua 
  /*
mapAgenciasBancarias = Dados.contabilidade.v1.agenciasBancaria.busca(campos: "nome, numeroAgencia, digitoAgencia, numeroEndereco,banco.id").collectEntries{[
([
agencia:it.numeroAgencia.concat(it.digitoAgencia?"-"+it.digitoAgencia:""),
idBanco:it.banco.id
]):[id:it.id]
]
*/
}
```

Este bloco filtra os credores para identificar aqueles com agências bancárias não cadastradas. Se houver agências não cadastradas, a função `cadastrarAgencias` é chamada para registrá-las no sistema via API. Um trecho de código comentado sugere a possibilidade de re-carregar o mapa de agências após o cadastro, caso o script seja executado de forma contínua.

### 4. Busca e Cadastro de Credores

```groovy
imprimir JSON.escrever(credores)

credores = buscarIdCredores(credores)
credoresSemCadastro = credores.findAll{it.idCredor == 0}
if(credoresSemCadastro){
  cadastrarCredor(credoresSemCadastro)
}
```

Após o processamento das agências, este bloco busca os IDs dos credores já existentes no sistema usando a função `buscarIdCredores`. Credores que não são encontrados (com `idCredor == 0`) são identificados e passados para a função `cadastrarCredor`, que os registra no sistema via API.

### 5. Cadastro de Contas Bancárias

```groovy
credores.each{it->
  it.agencia = mapAgenciasBancarias[[agencia: it.agencia,idBanco:it.banco]].id
}

credores = credores.groupBy{it.idCredor}


cadastrarContas(credores)
```

Este bloco prepara os dados dos credores para o cadastro das contas bancárias. Ele atualiza o campo `agencia` de cada credor com o ID da agência cadastrada (obtido do `mapAgenciasBancarias`). Em seguida, agrupa os credores pelo `idCredor` para processar todas as contas de um mesmo credor de uma vez. A função `cadastrarContas` é então chamada para realizar o cadastro das contas.

### 6. Funções Auxiliares

#### `cadastrarContas(credoresAgrupados)`

```groovy
def cadastrarContas(credoresAgrupados){
  listaPut = []
  i= 0
  credoresAgrupados.each{chave,valor->
    
    infoContaCredor = valor.first()
    contasBancarias = []
    valor.eachWithIndex{conta,index->
      contasBancarias<<contasToJson(conta,index)
    }
    
    credor = buscaCredorById(chave)// instancia pelo id do credor o retorno do get em formato mapa
    credor.idIntegracao = i.toString()
    //ver uma lógica para inalterar credores que ja tem uma conta

    if(credor.content.contasBancarias){
       credor.content.contasBancarias = credor.content.contasBancarias.collect{it->
          conta = [:]
          if(it.id) conta.id = it.id
          if(it.padrao) conta.padrao = it.padrao
          if(it.digitoConta) conta.digito = it.digitoConta
          if(it.numeroConta)conta.numero = it.numeroConta
          if(it.situacao) conta.situacao = it.situacao
          if(it.agencia.agenciaId) conta.agencia = [id: it.agencia.agenciaId]
          if(it.agencia.banco) conta.banco = [id: it.agencia.banco.bancoId]
          if(it.conta?.tipo){
            conta.tipo = it.conta.tipo
          }else{
              conta.tipo = "CORRENTE"
          }
          
          return conta
      }
      credor.content.contasBancarias.addAll(contasBancarias)
      
    }else{
      contasBancarias[0].padrao = true
      credor.content.contasBancarias = contasBancarias
    }
   	
    credor.content.contasBancarias = credor.content.contasBancarias.unique()
    
    credor.content.tipo = infoContaCredor.tipoPessoa
    credor.content.remove(\'cpfCnpj\')
    credor.content.remove(\'id\')
    
    if(!credor.content.enderecos){
      credor.content.remove(\'enderecos\')
    }else{
      credor.content.enderecos = credor.content.enderecos.collect{it->
        
        endereco =[:]
        
        if(it.principal) endereco.principal = it.principal
        if(it.estado) endereco.estado = [nome:it.estado.nome,id:it.estado.id]
        if(it.complemento) endereco.complemento = it.complemento
        if(it.numero) endereco.numero = it.numero
        if(it.municipio) endereco.municipio = [id:it.municipio.id]
        if(it.bairro) endereco.bairro = [id:it.bairro.id]
        if(it.logradouro) endereco.logradouro =[id:it.logradouro.id]
        if(it.id) endereco.id = it.id
        if(it.cep) endereco.cep = it.cep
        
        return endereco
      }
    }
    
    if(credor.content.credorReinf?.origemNaturezaRendimento){
      credor.content.credorReinf?.origemNaturezaRendimento = credor.content.credorReinf?.origemNaturezaRendimento?.value
    }
  
    if(credor.content.tipo == "JURIDICA"){
		
      if(credor.content.juridica?.natureza){
      	credor.content.juridica.natureza.remove(\'descricao\')
      }
      
       if (credor.content.juridica.socios.isEmpty()) {
       
              credor.content.juridica?.remove(\'socios\')
          }
    }
   	
    if(!credor.content.telefones){
      credor.content.remove(\'telefones\')
    }else{
      credor.content.telefones = credor.content.telefones.collect{it->
        [
          numero: buscarTelefone(it.id),
          principal: it.principal.present,
          tipo: it.tipo,
          id: it.id
        ]
      }
    }
    
    if(!credor.content.emails){
      credor.content.remove(\'emails\')
    }else{
      credor.content.emails = credor.content.emails.collect{it->
        e_mail = [:]
        
        if(it.principal) e_mail.principal = it.principal.present
        if(it.id) e_mail.id = it.id
        if(it.email) e_mail.email = it.email
        if(it.descricao) e_mail.descricao = it.descricao
        
        return e_mail
      }
    }
    
    listaPut<<credor
    i++
  
  }
  
  listaPut.collate(50).each{credores->
	imprimir"ListaPutContasCredores: "+JSON.escrever(credores)
    url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/credores"
    servico = Http.servico(url).chaveIntegracao(Variavel.BTH_CONTABIL_CHAVE)
    resposta = servico.PUT(JSON.escrever(credores),Http.JSON)
    imprimir "LoteListaPutContasCredores: "+JSON.escrever(resposta.json())

  }

}
```

Esta função é a mais complexa, responsável por buscar os dados completos do credor (incluindo informações existentes de contas bancárias, endereços, telefones e e-mails), formatar as novas contas bancárias a serem adicionadas (usando `contasToJson`), e mesclar as informações. Ela garante que as contas bancárias sejam únicas e que a primeira conta seja definida como padrão, se necessário. Antes de enviar os dados via PUT para a API de credores, a função remove campos desnecessários ou formata outros para o padrão da API. As chamadas PUT são realizadas em lotes de 50 credores.

#### `buscarIdCredores(credores)`

```groovy
def buscarIdCredores(credores){
  
  credores.each{it->
    
    criterio = ""
    if(it.tipoPessoa == "FISICA"){
      criterio = "credorFisica.pessoaFisica.cpf = \'${it.cpfCnpj}\'"
    }
    if(it.tipoPessoa == "JURIDICA"){
      criterio = "credorJuridica.pessoaJuridica.cnpj = \'${it.cpfCnpj}\'"
    }
    
    idCredor = Dados.contabilidade.v1.credores.busca(criterio: criterio,campos: "id").collect{it.id}
    it.idCredor = !idCredor.isEmpty()?idCredor.first():0
  }
  return credores
}
```

Esta função recebe uma lista de credores e, para cada um, constrói um critério de busca baseado no CPF ou CNPJ. Ela então busca o ID do credor no sistema e atribui esse ID ao campo `idCredor` do objeto do credor. Se o credor não for encontrado, `idCredor` é definido como 0.

#### `cadastrarCredor(credoresSemCadastro)`

```groovy
def cadastrarCredor(credoresSemCadastro){
  
  listaPost =[]
  
  credoresSemCadastro.eachWithIndex{it,index->
    obj = []
    obj=[
      idIntegracao:"${index}",
      content:[
        nome: it.nome,
        dataInclusao: Datas.hoje().format("yyyy-MM-dd")
      ]
    ]
    
    if(it.tipoPessoa == "FISICA"){
      obj.content.tipo = "FISICA"
      obj.content.fisica = [cpf: it.cpfCnpj]
    }
    if(it.tipoPessoa == "JURIDICA"){
      obj.content.tipo = "JURIDICA"
      obj.content.juridica = [cnpj: it.cpfCnpj]
    }
    listaPost<<obj
  }
  
  listaPost.collate(50).each{credores->
    imprimir"Credores: "+JSON.escrever(credores)
    url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/credores"
    servico = Http.servico(url).chaveIntegracao(Variavel.BTH_CONTABIL_CHAVE)
    resposta = servico.POST(JSON.escrever(credores),Http.JSON)
    imprimir "LoteCredores: "+JSON.escrever(resposta.json())
  }
}
```

Esta função recebe uma lista de credores que ainda não estão cadastrados no sistema. Para cada credor, ela monta um objeto JSON com os dados básicos (nome, data de inclusão, tipo de pessoa e CPF/CNPJ) e os envia para a API de cadastro de credores via POST. As chamadas POST são realizadas em lotes de 50 credores.

#### `cadastrarAgencias(credoresAgencias)`

```groovy
def cadastrarAgencias(credoresAgencias){
  
  listaPost = []
  i=0
  credoresAgencias.each{credor->
    
    if(credor.agencia.find("-")){
      agencia = credor.agencia.split("-")
      numero = agencia[0]
      digito = agencia[1]
      nome =  "Agencia "+numero+"-"+digito
    }else{
      numero = credor.agencia
      digito = null
      nome =  "Agencia "+numero
    }       
    obj=[
      content: [
        nome: nome,
        banco: [
          id: credor.banco
        ],
        numero: numero
      ]
    ]
    
    if(digito){
      obj.content.digito = digito
    }
    
    listaPost<<obj
    i++
   }
  
  listaPost = listaPost.unique()
  listaPost.eachWithIndex{agencia,index->
    agencia.idIntegracao = "${index}"
  }
  
  listaPost.collate(50).each{agencias->
    imprimir "Agencias: "+JSON.escrever(agencias)
    url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/agencias-bancarias"
    servico = Http.servico(url).chaveIntegracao(Variavel.BTH_CONTABIL_CHAVE)
    resposta = servico.POST(JSON.escrever(agencias),Http.JSON)
    imprimir "LotesAgencia: "+JSON.escrever(resposta.json())
  }
}
```

Esta função recebe uma lista de credores com agências não cadastradas. Ela formata os dados da agência (número, dígito, nome) e monta um objeto JSON para cada agência. As agências são então enviadas para a API de cadastro de agências bancárias via POST, também em lotes de 50.

#### `buscaCredorById(idCredor)`

```groovy
def buscaCredorById(idCredor){
  url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/credores/${idCredor}"
  servico = Http.servico(url).chaveIntegracao(Variavel.BTH_CONTABIL_CHAVE).GET()
  return servico.json()
  
}
```

Esta função realiza uma chamada GET à API de credores para obter os dados completos de um credor específico, dado o seu ID.

#### `buscarTelefone(idTelefone)`

```groovy
def buscarTelefone(idTelefone){
  numero = Dados.contabilidade.v1.telefones.busca(criterio: "id = ${idTelefone}",campos: "numero").collect{ it.numero }	
  if(numero.size()>0){
    return numero.first().toString()
  }
}
```

Esta função busca o número de telefone de um registro de telefone específico, dado o seu ID.

#### `contasToJson(conta,index)`

```groovy
def contasToJson(conta,index){ //monta o json das contas colocando a primeira como principal 
  
    if(conta.contaCorrente.find("-")){
      numeroContaCorrente = conta.contaCorrente.split("-")[0]
      digitoContaCorrente = conta.contaCorrente.split("-")[1]
    }else{
      numeroContaCorrente = conta.contaCorrente
      digitoContaCorrente = null
    }
    
    obj = [
    	id:0,
      	banco:[
          id:conta.banco
              ],
      	agencia:[
          id:conta.agencia
        ],
      numero:numeroContaCorrente,
      tipo:"CORRENTE",
      dataAbertura: Datas.hoje().format("yyyy-MM-dd"),
      situacao:"ABERTA"
    ]
    
    if(digitoContaCorrente){
    obj.digito = digitoContaCorrente
    }
  
    obj.padrao = false
 
  return obj
}
```

Esta função auxiliar formata os dados de uma conta corrente para o formato JSON esperado pela API. Ela extrai o número e o dígito da conta, define o tipo como 


CORRENTE, a data de abertura como a data atual e a situação como ABERTA. O campo `padrao` é definido como `false` por padrão.

#### `BuscaIdBancoFebraban(numeroBanco)`

```groovy
def BuscaIdBancoFebraban(numeroBanco){
  MapBancos = [:]
  MapBancos["001"] =[idBanco:137,    descricao:"Banco do Brasil S.A.                                                  "]
  MapBancos["002"] =[idBanco:625,    descricao:"BANCO CENTRAL DO BRASIL                                               "]
  MapBancos["003"] =[idBanco:130,    descricao:"Banco da Amazônia S.A.                                                "]
  MapBancos["004"] =[idBanco:142,    descricao:"Banco do Nordeste do Brasil S.A.                                      "]
  MapBancos["006"] =[idBanco:671,    descricao:"BANCO BNCC S.A.                                                       "]
  MapBancos["007"] =[idBanco:641,    descricao:"Banco Nacional de Desenvolvimento Econômico e Social BNDES            "]
  MapBancos["008"] =[idBanco:556,    descricao:"Banco Meridional do Brasil S.A.                                       "]
  MapBancos["010"] =[idBanco:662,    descricao:"Credicoamo Crédito Rural Cooperativa                                  "]
  MapBancos["012"] =[idBanco:119,    descricao:"Banco Standard de Investimentos S.A.                                  "]
  MapBancos["014"] =[idBanco:168,    descricao:"Natixis Brasil S.A. Banco Múltiplo                                    "]
  MapBancos["017"] =[idBanco:9  ,    descricao:"BNY Mellon Banco S.A.                                                 "]
  MapBancos["018"] =[idBanco:123,    descricao:"Banco Tricury S.A.                                                    "]
  MapBancos["019"] =[idBanco:18 ,    descricao:"Banco Azteca do Brasil S.A.                                           "]
  MapBancos["020"] =[idBanco:607,    descricao:"BANCO DO ESTADO DE ALAGOAS S.A.                                       "]
  MapBancos["021"] =[idBanco:4  ,    descricao:"BANESTES S.A. Banco do Estado do Espírito Santo                       "]
  MapBancos["022"] =[idBanco:525,    descricao:"BANCO DE CREDITO REAL DE MINAS GERAIS S.A.                            "]
  MapBancos["023"] =[idBanco:526,    descricao:"BANCO DE DESENVOLVIMENTO DE MINAS GERAIS S.A.                         "]
  MapBancos["024"] =[idBanco:19 ,    descricao:"Banco BANDEPE S.A.                                                    "]
  MapBancos["025"] =[idBanco:15 ,    descricao:"Banco Alfa S.A.                                                       "]
  MapBancos["026"] =[idBanco:536,    descricao:"BANCO DO ESTADO DO ACRE S.A.                                          "]
  MapBancos["027"] =[idBanco:1  ,    descricao:"BANCO DO ESTADO DE SANTA CATARINA S.A.                                "]
  MapBancos["028"] =[idBanco:530,    descricao:"BANCO DO ESTADO DA BAHIA S.A.                                         "]
  MapBancos["029"] =[idBanco:26 ,    descricao:"Banco Banerj S.A.                                                     "]
  MapBancos["030"] =[idBanco:531,    descricao:"BANCO DO ESTADO DA PARAIBA S.A.                                       "]
  MapBancos["031"] =[idBanco:28 ,    descricao:"Banco Beg S.A.                                                        "]
  MapBancos["032"] =[idBanco:532,    descricao:"BANCO DO ESTADO DE MATO GROSSO S.A.                                   "]
  MapBancos["033"] =[idBanco:114,    descricao:"Banco Santander (Brasil) S.A.                                         "]
  MapBancos["034"] =[idBanco:537,    descricao:"BANCO DO ESTADO DO AMAZONAS S.A.                                      "]
  MapBancos["035"] =[idBanco:538,    descricao:"BANCO DO ESTADO DO CEARA S.A.                                         "]
  MapBancos["036"] =[idBanco:32 ,    descricao:"Banco Bradesco BBI S.A.                                               "]
  MapBancos["037"] =[idBanco:139,    descricao:"Banco do Estado do Pará S.A.                                          "]
  MapBancos["038"] =[idBanco:2  ,    descricao:"BANCO DO ESTADO DO PARANA S.A.                                        "]
  MapBancos["039"] =[idBanco:140,    descricao:"Banco do Estado do Piauí S.A. - BEP                                   "]
  MapBancos["040"] =[idBanco:42 ,    descricao:"Banco Cargill S.A.                                                    "]
  MapBancos["041"] =[idBanco:141,    descricao:"Banco do Estado do Rio Grande do Sul S.A.                             "]
  MapBancos["044"] =[idBanco:25 ,    descricao:"Banco BVA S.A.                                                        "]
  MapBancos["045"] =[idBanco:92 ,    descricao:"Banco Opportunity S.A.                                                "]
  MapBancos["046"] =[idBanco:564,    descricao:"BANCO REGIONAL DE DESENVOLVIMENTO DO EXTREMO SUL                      "]
  MapBancos["047"] =[idBanco:138,    descricao:"Banco do Estado de Sergipe S.A.                                       "]
  MapBancos["048"] =[idBanco:533,    descricao:"BANCO DO ESTADO DE MINAS GERAIS S.A.                                  "]
  MapBancos["048"] =[idBanco:599,    descricao:"Banco do Estado de Minas Gerais S.A                                   "]
  MapBancos["049"] =[idBanco:528,    descricao:"BANCO DE DESENVOLVIMENTO DO ESTADO DA BAHIA S.A.                      "]
  MapBancos["051"] =[idBanco:527,    descricao:"BANCO DE DESENVOLVIMENTO DO ESPIRITO SANTO S.A.                       "]
  MapBancos["057"] =[idBanco:529,    descricao:"BANCO DE DESENVOLVIMENTO DO ESTADO DE SANTA CATARI                    "]
  MapBancos["059"] =[idBanco:534,    descricao:"BANCO DO ESTADO DE RONDONIA S.A.                                      "]
  MapBancos["062"] =[idBanco:162,    descricao:"Hipercard Banco Múltiplo S.A.                                         "]
  MapBancos["063"] =[idBanco:69 ,    descricao:"Banco Ibi S.A. Banco Múltiplo                                         "]
  MapBancos["064"] =[idBanco:159,    descricao:"Goldman Sachs do Brasil Banco Múltiplo S.A.                           "]
  MapBancos["065"] =[idBanco:31 ,    descricao:"Banco Bracce S.A.                                                     "]
  MapBancos["066"] =[idBanco:90 ,    descricao:"Banco de Crédito e Varejo S.A.                                        "]
  MapBancos["069"] =[idBanco:35 ,    descricao:"Banco Crefisa S.A.                                                    "]
  MapBancos["070"] =[idBanco:143,    descricao:"BRB - Banco de Brasília S.A.                                          "]
  MapBancos["072"] =[idBanco:145,    descricao:"Banco J. Safra S.A.                                                   "]
  MapBancos["073"] =[idBanco:20 ,    descricao:"BB Banco Popular do Brasil S.A.                                       "]
  MapBancos["074"] =[idBanco:146,    descricao:"Banco J. Safra S.A.                                                   "]
  MapBancos["075"] =[idBanco:147,    descricao:"Banco CR2 S.A.                                                        "]
  MapBancos["076"] =[idBanco:148,    descricao:"Banco KDB S.A.                                                        "]
  MapBancos["077"] =[idBanco:149,    descricao:"Banco Intermedium S.A.                                                "]
  MapBancos["078"] =[idBanco:150,    descricao:"BES Investimento do Brasil S.A. - Banco de Investimento               "]
  MapBancos["079"] =[idBanco:151,    descricao:"JBS Banco S.A.                                                        "]
  MapBancos["081"] =[idBanco:152,    descricao:"Concórdia Banco S.A.                                                 "]
  MapBancos["082"] =[idBanco:153,    descricao:"Banco Topázio S.A.                                                    "]
  MapBancos["083"] =[idBanco:154,    descricao:"Banco da China Brasil S.A.                                            "]
  MapBancos["084"] =[idBanco:155,    descricao:"Unicred Norte do Paraná                                               "]
  MapBancos["085"] =[idBanco:156,    descricao:"Cooperativa Central de Crédito Urbano-CECRED                          "]
  MapBancos["086"] =[idBanco:157,    descricao:"OBOE Crédito Financiamento e Investimento S.A.                        "]
  MapBancos["087"] =[idBanco:158,    descricao:"Cooperativa de Crédito Rural da Região de Mogiana                     "]
  MapBancos["089"] =[idBanco:160,    descricao:"Cooperativa de Crédito Rural da Região da Alta Mogiana                "]
  MapBancos["090"] =[idBanco:161,    descricao:"Cooperativa Central de Economia e Crédito Mutuo das Unicreds            "]
  MapBancos["091"] =[idBanco:163,    descricao:"Unicred Central do Rio Grande do Sul                                  "]
  MapBancos["092"] =[idBanco:164,    descricao:"Brickell S.A. Crédito, financiamento e Investimento                   "]
  MapBancos["093"] =[idBanco:165,    descricao:"Pólocred S.A. - Crédito, Financiamento e Investimento                 "]
  MapBancos["094"] =[idBanco:166,    descricao:"Banco Petra S.A.                                                      "]
  MapBancos["095"] =[idBanco:167,    descricao:"Banco Confidence de Câmbio S.A.                                       "]
  MapBancos["096"] =[idBanco:169,    descricao:"Banco BM&FBOVESPA de Serviços de Liquidação e Custódia S.A            "]
  MapBancos["097"] =[idBanco:170,    descricao:"Cooperativa Central de Crédito Noroeste Brasileiro Ltda.              "]
  MapBancos["098"] =[idBanco:171,    descricao:"Credicorol Cooperativa de Crédito Rural                               "]
  MapBancos["099"] =[idBanco:172,    descricao:"Cooperativa de Crédito Rural de Primavera do Leste                      "]
  MapBancos["100"] =[idBanco:173,    descricao:"Planner Corretora de Valores S.A.                                     "]
  MapBancos["101"] =[idBanco:174,    descricao:"Renascença Distribuidora de Títulos e Valores Mobiliários Ltda        "]
  MapBancos["102"] =[idBanco:175,    descricao:"XP Investimentos Corretora de Câmbio, Títulos e Valores Mobiliários S.A"]
  MapBancos["104"] =[idBanco:136,    descricao:"Caixa Econômica Federal                                                 "]
  MapBancos["105"] =[idBanco:176,    descricao:"Lecca Crédito, Financiamento e Investimento S/A                       "]
  MapBancos["107"] =[idBanco:177,    descricao:"Banco BBM S.A.                                                        "]
  MapBancos["111"] =[idBanco:178,    descricao:"Oliveira Trust Distribuidora de Títulos e Valores Mobiliários S.A     "]
  MapBancos["113"] =[idBanco:179,    descricao:"Magliano S.A. Corretora de Câmbio e Valores Mobiliários               "]
  MapBancos["114"] =[idBanco:180,    descricao:"Central Cooperativa de Crédito no Estado do Espírito Santo            "]
  MapBancos["117"] =[idBanco:181,    descricao:"Advanced Corretora de Câmbio Ltda.                                    "]
  MapBancos["118"] =[idBanco:182,    descricao:"Standard Chartered Bank (Brasil) S/A–Bco Invest.                      "]
  MapBancos["119"] =[idBanco:183,    descricao:"Banco Western Union do Brasil S.A.                                    "]
  MapBancos["120"] =[idBanco:184,    descricao:"Banco Rodobens S.A.                                                   "]
  MapBancos["121"] =[idBanco:185,    descricao:"Banco Agiplan S.A.                                                    "]
  MapBancos["122"] =[idBanco:186,    descricao:"Banco Bradesco BERJ S.A.                                              "]
  MapBancos["124"] =[idBanco:187,    descricao:"Banco Woori Bank do Brasil S.A.                                       "]
  MapBancos["125"] =[idBanco:188,    descricao:"Brasil Plural S.A. - Banco Múltiplo                                   "]
  MapBancos["126"] =[idBanco:189,    descricao:"BR Partners Banco de Investimento S.A.                                "]
  MapBancos["127"] =[idBanco:190,    descricao:"Codepe Corretora de Valores e Câmbio S.A.                             "]
  MapBancos["128"] =[idBanco:191,    descricao:"MS Bank S.A. Banco de Câmbio                                          "]
  MapBancos["129"] =[idBanco:192,    descricao:"UBS Brasil Banco de Investimento S.A.                                 "]
  MapBancos["130"] =[idBanco:193,    descricao:"Caruana S.A. - Sociedade de Crédito, Financiamento e Investimento     "]
  MapBancos["131"] =[idBanco:194,    descricao:"Tullett Prebon Brasil Corretora de Valores e Câmbio Ltda              "]
  MapBancos["132"] =[idBanco:195,    descricao:"ICBC do Brasil Banco Múltiplo S.A.                                    "]
  MapBancos["133"] =[idBanco:196,    descricao:"Confederacao Nacional das Cooperativas Centrais de Credito e Economia Familiar e Solidario - CRESOL"]
  MapBancos["134"] =[idBanco:197,    descricao:"BGC Liquidez Distribuidora de Títulos e Valores Mobiliários Ltda      "]
  MapBancos["135"] =[idBanco:198,    descricao:"Gradual Corretora de Câmbio, Títulos e Valores Mobiliários S.A.       "]
  MapBancos["136"] =[idBanco:199,    descricao:"Confederação Nacional das Cooperativas Centrais Unicred do Brasil – Unicred do Brasil"]
  MapBancos["137"] =[idBanco:200,    descricao:"Multimoney Corretora de Câmbio Ltda                                   "]
  MapBancos["138"] =[idBanco:201,    descricao:"Get Money Corretora de Câmbio S.A.                                    "]
  MapBancos["139"] =[idBanco:202,    descricao:"Intesa Sanpaolo Brasil S.A. - Banco Múltiplo                          "]
  MapBancos["140"] =[idBanco:203,    descricao:"Easynvest - Título Corretora de Valores SA                            "]
  MapBancos["142"] =[idBanco:204,    descricao:"Broker Brasil Corretora de Câmbio Ltda.                               "]
  MapBancos["143"] =[idBanco:205,    descricao:"Treviso Corretora de Câmbio S.A.                                      "]
  MapBancos["144"] =[idBanco:206,    descricao:"Bexs Banco de Câmbio S.A.                                             "]
  MapBancos["145"] =[idBanco:207,    descricao:"Levycam - Corretora de Câmbio e Valores Ltda.                         "]
  MapBancos["146"] =[idBanco:208,    descricao:"Guitta Corretora de Câmbio Ltda.                                      "]
  MapBancos["147"] =[idBanco:209,    descricao:"Facta Financeira S.A. - Crédito Financiamento e Investimento          "]
  MapBancos["149"] =[idBanco:210,    descricao:"Banco IBM S.A.                                                        "]
  MapBancos["157"] =[idBanco:211,    descricao:"ICAP do Brasil Corretora de Títulos e Valores Mobiliários Ltda.       "]
  MapBancos["159"] =[idBanco:212,    descricao:"Casa do Crédito S.A. - Sociedade de Crédito ao Microempreendedor      "]
  MapBancos["163"] =[idBanco:213,    descricao:"Commerzbank Brasil S.A. - Banco Múltiplo                              "]
  MapBancos["169"] =[idBanco:214,    descricao:"Banco Olé Bonsucesso Consignado S.A.                                  "]
  MapBancos["172"] =[idBanco:215,    descricao:"Albatross Corretora de Câmbio e Valores S.A                           "]
  MapBancos["173"] =[idBanco:216,    descricao:"BRL Trust Distribuidora de Títulos e Valores Mobiliários S.A.         "]
  MapBancos["174"] =[idBanco:217,    descricao:"Pernambucanas Financiera S.A. - Crédito, Financiamento e Investimento   "]
  MapBancos["177"] =[idBanco:218,    descricao:"Guide Investimentos S.A. Corretora de Valores                         "]
  MapBancos["180"] =[idBanco:219,    descricao:"CM Capital Markets Corretora de Câmbio, Títulos e Valores Mobiliários Ltda"]
  MapBancos["182"] =[idBanco:220,    descricao:"Dacasa Financeira S/A - Sociedade de Crédito, Financiamento e Investimento"]
  MapBancos["183"] =[idBanco:221,    descricao:"Socred S.A. - Sociedade de Crédito ao Microempreendedor               "]
  MapBancos["184"] =[idBanco:222,    descricao:"Banco Itaú BBA S.A.                                                   "]
  MapBancos["188"] =[idBanco:223,    descricao:"Ativa Investimentos S.A. Corretora de Títulos, Câmbio e Valores       "]
  MapBancos["189"] =[idBanco:224,    descricao:"HS Financeira S/A Crédito, Financiamento e Investimentos              "]
  MapBancos["190"] =[idBanco:225,    descricao:"Cooperativa de Economia e Crédito Mútuo dos Servidores Públicos       "]
  MapBancos["191"] =[idBanco:226,    descricao:"Nova Futura Corretora de Títulos e Valores Mobiliários Ltda.          "]
  MapBancos["194"] =[idBanco:227,    descricao:"Parmetal Distribuidora de Títulos e Valores Mobiliários Ltda          "]
  MapBancos["196"] =[idBanco:228,    descricao:"Fair Corretora de Câmbio S.A.                                         "]
  MapBancos["197"] =[idBanco:229,    descricao:"Stone Pagamentos S.A.                                                 "]
  MapBancos["204"] =[idBanco:36 ,    descricao:"Banco Bradesco Cartões S.A.                                           "]
  MapBancos["208"] =[idBanco:37 ,    descricao:"Banco BTG Pactual S.A.                                                "]
  MapBancos["212"] =[idBanco:38 ,    descricao:"Banco Original S.A.                                                   "]
  MapBancos["213"] =[idBanco:39 ,    descricao:"Banco Arbi S.A.                                                       "]
  MapBancos["214"] =[idBanco:40 ,    descricao:"Banco Dibens S.A.                                                     "]
  MapBancos["215"] =[idBanco:41 ,    descricao:"Banco Comercial e de Investimento Sudameris S.A.                      "]
  MapBancos["217"] =[idBanco:43 ,    descricao:"Banco John Deere S.A.                                                 "]
  MapBancos["218"] =[idBanco:44 ,    descricao:"Banco Bonsucesso S.A.                                                 "]
  MapBancos["222"] =[idBanco:45 ,    descricao:"Banco Credit Agricole Brasil S.A.                                     "]
  MapBancos["224"] =[idBanco:46 ,    descricao:"Banco Fibra S.A.                                                      "]
  MapBancos["225"] =[idBanco:47 ,    descricao:"Banco Brascan S.A.                                                    "]
  MapBancos["229"] =[idBanco:48 ,    descricao:"Banco Cruzeiro do Sul S.A.                                            "]
  MapBancos["230"] =[idBanco:49 ,    descricao:"Unicard Banco Múltiplo S.A.                                           "]
  MapBancos["233"] =[idBanco:50 ,    descricao:"Banco GE Capital S.A.                                                 "]
  MapBancos["237"] =[idBanco:51 ,    descricao:"Banco Bradesco S.A.                                                   "]
  MapBancos["241"] =[idBanco:52 ,    descricao:"Banco Clássico S.A.                                                   "]
  MapBancos["243"] =[idBanco:53 ,    descricao:"Banco Máxima S.A.                                                     "]
  MapBancos["246"] =[idBanco:54 ,    descricao:"Banco ABC Brasil S.A.                                                 "]
  MapBancos["248"] =[idBanco:55 ,    descricao:"Banco Boavista Interatlântico S.A.                                    "]
  MapBancos["249"] =[idBanco:56 ,    descricao:"Banco Investcred Unibanco S.A.                                        "]
  MapBancos["250"] =[idBanco:57 ,    descricao:"BCV - Banco de Crédito e Varejo S.A.                                  "]
  MapBancos["252"] =[idBanco:58 ,    descricao:"Fininvest S.A. - Banco Múltiplo                                       "]
  MapBancos["254"] =[idBanco:59 ,    descricao:"Paraná Banco S.A.                                                     "]
  MapBancos["260"] =[idBanco:60 ,    descricao:"Nu Pagamentos S.A.                                                    "]
  MapBancos["263"] =[idBanco:61 ,    descricao:"Banco Cacique S.A.                                                    "]
  MapBancos["265"] =[idBanco:62 ,    descricao:"Banco Fator S.A.                                                      "]
  MapBancos["266"] =[idBanco:63 ,    descricao:"Banco Cédula S.A.                                                     "]
  MapBancos["300"] =[idBanco:64 ,    descricao:"Banco de La Nacion Argentina                                          "]
  MapBancos["318"] =[idBanco:65 ,    descricao:"Banco BMG S.A.                                                        "]
  MapBancos["320"] =[idBanco:66 ,    descricao:"Banco Industrial e Comercial S.A.                                     "]
  MapBancos["341"] =[idBanco:67 ,    descricao:"Itaú Unibanco S.A.                                                    "]
  MapBancos["356"] =[idBanco:68 ,    descricao:"Banco Real S.A.                                                       "]
  MapBancos["366"] =[idBanco:70 ,    descricao:"Banco Société Générale Brasil S.A.                                    "]
  MapBancos["370"] =[idBanco:71 ,    descricao:"Banco Mizuho do Brasil S.A.                                           "]
  MapBancos["376"] =[idBanco:72 ,    descricao:"Banco J. P. Morgan S.A.                                               "]
  MapBancos["389"] =[idBanco:73 ,    descricao:"Banco Mercantil do Brasil S.A.                                        "]
  MapBancos["394"] =[idBanco:74 ,    descricao:"Banco Finasa BMC S.A.                                                 "]
  MapBancos["399"] =[idBanco:75 ,    descricao:"HSBC Bank Brasil S.A. - Banco Múltiplo                                "]
  MapBancos["409"] =[idBanco:76 ,    descricao:"UNIBANCO - União de Bancos Brasileiros S.A.                           "]
  MapBancos["412"] =[idBanco:77 ,    descricao:"Banco Capital S.A.                                                    "]
  MapBancos["422"] =[idBanco:78 ,    descricao:"Banco Safra S.A.                                                      "]
  MapBancos["453"] =[idBanco:79 ,    descricao:"Banco Rural S.A.                                                      "]
  MapBancos["456"] =[idBanco:80 ,    descricao:"Banco de Tokyo-Mitsubishi UFJ Brasil S.A.                             "]
  MapBancos["464"] =[idBanco:81 ,    descricao:"Banco Sumitomo Mitsui Brasileiro S.A.                                 "]
  MapBancos["473"] =[idBanco:82 ,    descricao:"Banco Caixa Geral - Brasil S.A.                                       "]
  MapBancos["477"] =[idBanco:83 ,    descricao:"Citibank N.A.                                                         "]
  MapBancos["479"] =[idBanco:84 ,    descricao:"Banco ItauBank S.A.                                                   "]
  MapBancos["487"] =[idBanco:85 ,    descricao:"Deutsche Bank S.A. - Banco Alemão                                     "]
  MapBancos["488"] =[idBanco:86 ,    descricao:"JPMorgan Chase Bank, National Association                             "]
  MapBancos["492"] =[idBanco:87 ,    descricao:"ING Bank N.V.                                                         "]
  MapBancos["494"] =[idBanco:88 ,    descricao:"Banco de La Republica Oriental del Uruguay                            "]
  MapBancos["495"] =[idBanco:89 ,    descricao:"Banco de La Provincia de Buenos Aires                                 "]
  MapBancos["505"] =[idBanco:91 ,    descricao:"Banco Credit Suisse (Brasil) S.A.                                     "]
  MapBancos["600"] =[idBanco:93 ,    descricao:"Banco Luso Brasileiro S.A.                                            "]
  MapBancos["604"] =[idBanco:94 ,    descricao:"Banco Industrial do Brasil S.A.                                       "]
  MapBancos["610"] =[idBanco:95 ,    descricao:"Banco VR S.A.                                                         "]
  MapBancos["611"] =[idBanco:96 ,    descricao:"Banco Paulista S.A.                                                   "]
  MapBancos["612"] =[idBanco:97 ,    descricao:"Banco Guanabara S.A.                                                  "]
  MapBancos["613"] =[idBanco:98 ,    descricao:"Banco Pecúnia S.A.                                                    "]
  MapBancos["623"] =[idBanco:99 ,    descricao:"Banco PAN S.A.                                                        "]
  MapBancos["626"] =[idBanco:100,    descricao:"Banco Ficsa S.A.                                                      "]
  MapBancos["630"] =[idBanco:101,    descricao:"Banco Intercap S.A.                                                   "]
  MapBancos["633"] =[idBanco:102,    descricao:"Banco Rendimento S.A.                                                 "]
  MapBancos["634"] =[idBanco:103,    descricao:"Banco Triângulo S.A.                                                  "]
  MapBancos["637"] =[idBanco:104,    descricao:"Banco Sofisa S.A.                                                     "]
  MapBancos["638"] =[idBanco:105,    descricao:"Banco Prosper S.A.                                                    "]
  MapBancos["641"] =[idBanco:106,    descricao:"Banco Alvorada S.A.                                                   "]
  MapBancos["643"] =[idBanco:107,    descricao:"Banco Pine S.A.                                                       "]
  MapBancos["652"] =[idBanco:108,    descricao:"Itaú Unibanco Holding S.A.                                            "]
  MapBancos["653"] =[idBanco:109,    descricao:"Banco Indusval S.A.                                                   "]
  MapBancos["654"] =[idBanco:110,    descricao:"Banco A.J.Renner S.A.                                                 "]
  MapBancos["655"] =[idBanco:111,    descricao:"Banco Votorantim S.A.                                                 "]
  MapBancos["658"] =[idBanco:112,    descricao:"Banco Porto Real S.A.                                                 "]
  MapBancos["707"] =[idBanco:113,    descricao:"Banco Daycoval S.A.                                                   "]
  MapBancos["719"] =[idBanco:115,    descricao:"Banif-Banco Internacional do Funchal (Brasil),S.A.                    "]
  MapBancos["721"] =[idBanco:116,    descricao:"Banco Credibel S.A.                                                   "]
  MapBancos["734"] =[idBanco:117,    descricao:"Banco Gerdau S.A.                                                     "]
  MapBancos["735"] =[idBanco:118,    descricao:"Banco Pottencial S.A.                                                 "]
  MapBancos["738"] =[idBanco:120,    descricao:"Banco Morada S.A.                                                     "]
  MapBancos["739"] =[idBanco:121,    descricao:"Banco BGN S.A.                                                        "]
  MapBancos["740"] =[idBanco:122,    descricao:"Banco Barclays S.A.                                                   "]
  MapBancos["741"] =[idBanco:124,    descricao:"Banco Ribeirão Preto S.A.                                             "]
  MapBancos["743"] =[idBanco:125,    descricao:"Banco Semear S.A.                                                     "]
  MapBancos["745"] =[idBanco:126,    descricao:"Banco Citibank S.A.                                                   "]
  MapBancos["746"] =[idBanco:127,    descricao:"Banco Modal S.A.                                                      "]
  MapBancos["747"] =[idBanco:128,    descricao:"Banco Rabobank International Brasil S.A.                              "]
  MapBancos["748"] =[idBanco:129,    descricao:"Banco Cooperativo Sicredi S.A.                                        "]
  MapBancos["749"] =[idBanco:131,    descricao:"Banco Simples S.A.                                                    "]
  MapBancos["751"] =[idBanco:132,    descricao:"Scotiabank Brasil S.A. Banco Múltiplo                                 "]
  MapBancos["752"] =[idBanco:133,    descricao:"Banco BNP Paribas Brasil S.A.                                         "]
  MapBancos["753"] =[idBanco:134,    descricao:"NBC Bank Brasil S.A. - Banco Múltiplo                                 "]
  MapBancos["755"] =[idBanco:135,    descricao:"Bank of America Merrill Lynch Banco Múltiplo S.A.                     "]
  MapBancos["756"] =[idBanco:144,    descricao:"Banco Cooperativo do Brasil S.A. - BANCOOB                            "]
  MapBancos["757"] =[idBanco:16 ,    descricao:"Banco KEB DO BRASIL S.A.                                              "]
  return MapBancos[numeroBanco].idBanco
}
```

Esta função auxiliar é um grande mapa que associa o número do banco (código FEBRABAN) ao ID interno do banco no sistema. Ela é usada para obter o ID do banco a partir do número fornecido no arquivo CSV.

## Código Completo

```groovy
//busca todas agencias bancarias cadastradas no cloud e retorna um mapa com o numero e digito como chave (123-3) e o id como valor
mapAgenciasBancarias = Dados.contabilidade.v1.agenciasBancaria.busca(campos: "nome, numeroAgencia, digitoAgencia, numeroEndereco,banco.id").collectEntries{[
  ([
    agencia:it.numeroAgencia.concat(it.digitoAgencia?"-"+it.digitoAgencia:""),
    idBanco:it.banco.id
  ]):[id:it.id]
]
                                                                                                                                                          }
regexCNPJ = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/
regexCPF  = /^\d{3}\.\d{3}\.\d{3}-\d{2}$/

p_arquivo = parametros.p_arquivo.valor
arquivo = Arquivo.ler(p_arquivo, \'csv\');

credores = []

percorrer(enquanto: {arquivo.contemProximaLinha()}) {
  linha = arquivo.lerLinha()
  campos = linha.split(\

  if(!(campos.size()<5)){
    idBanco = BuscaIdBancoFebraban(campos[2])
    cpfCnpj = campos[1]
    
    if(cpfCnpj.contains(" ")){
          cpfCnpj = cpfCnpj.split(" ")[0]
    }

    if(cpfCnpj ==~ regexCPF){
      tipoPessoa = "FISICA"
      cpfCnpj = cpfCnpj.replaceAll(/[-.\/]/, "")
    }else if(cpfCnpj ==~ regexCNPJ){
      tipoPessoa = "JURIDICA"
      cpfCnpj = cpfCnpj.replaceAll(/[-.\/]/, "")
    }
	
    credores<< [
      nome: campos[0],
      cpfCnpj:cpfCnpj,
      tipoPessoa:tipoPessoa,
      banco:idBanco,
      idCredor:null,
      agencia:campos[3],
      agenciaCadastrada: mapAgenciasBancarias[[agencia:campos[3],idBanco:idBanco]]?true:false,
      contaCorrente: campos[4]
    ]
  }
}


credores = credores.unique()

agenciasNaoCadastradas = credores.findAll{!it.agenciaCadastrada}

if(agenciasNaoCadastradas){
  cadastrarAgencias(agenciasNaoCadastradas)
}else{
  //habilitar caso execução continua 
  /*
mapAgenciasBancarias = Dados.contabilidade.v1.agenciasBancaria.busca(campos: "nome, numeroAgencia, digitoAgencia, numeroEndereco,banco.id").collectEntries{[
([
agencia:it.numeroAgencia.concat(it.digitoAgencia?"-"+it.digitoAgencia:""),
idBanco:it.banco.id
]):[id:it.id]
]
*/
}

imprimir JSON.escrever(credores)

credores = buscarIdCredores(credores)
credoresSemCadastro = credores.findAll{it.idCredor == 0}
if(credoresSemCadastro){
  cadastrarCredor(credoresSemCadastro)
}


/*
esperar 1.minuto
esperar 1.minuto
esperar 1.minuto
*/

credores.each{it->
  it.agencia = mapAgenciasBancarias[[agencia: it.agencia,idBanco:it.banco]].id
}

credores = credores.groupBy{it.idCredor}


cadastrarContas(credores)


def cadastrarContas(credoresAgrupados){
  listaPut = []
  i= 0
  credoresAgrupados.each{chave,valor->
    
    infoContaCredor = valor.first()
    contasBancarias = []
    valor.eachWithIndex{conta,index->
      contasBancarias<<contasToJson(conta,index)
    }
    
    credor = buscaCredorById(chave)// instancia pelo id do credor o retorno do get em formato mapa
    credor.idIntegracao = i.toString()
    //ver uma lógica para inalterar credores que ja tem uma conta

    if(credor.content.contasBancarias){
       credor.content.contasBancarias = credor.content.contasBancarias.collect{it->
          conta = [:]
          if(it.id) conta.id = it.id
          if(it.padrao) conta.padrao = it.padrao
          if(it.digitoConta) conta.digito = it.digitoConta
          if(it.numeroConta)conta.numero = it.numeroConta
          if(it.situacao) conta.situacao = it.situacao
          if(it.agencia.agenciaId) conta.agencia = [id: it.agencia.agenciaId]
          if(it.agencia.banco) conta.banco = [id: it.agencia.banco.bancoId]
          if(it.conta?.tipo){
            conta.tipo = it.conta.tipo
          }else{
              conta.tipo = "CORRENTE"
          }
          
          return conta
      }
      credor.content.contasBancarias.addAll(contasBancarias)
      
    }else{
      contasBancarias[0].padrao = true
      credor.content.contasBancarias = contasBancarias
    }
   	
    credor.content.contasBancarias = credor.content.contasBancarias.unique()
    
    credor.content.tipo = infoContaCredor.tipoPessoa
    credor.content.remove(\'cpfCnpj\')
    credor.content.remove(\'id\')
    
    if(!credor.content.enderecos){
      credor.content.remove(\'enderecos\')
    }else{
      credor.content.enderecos = credor.content.enderecos.collect{it->
        
        endereco =[:]
        
        if(it.principal) endereco.principal = it.principal
        if(it.estado) endereco.estado = [nome:it.estado.nome,id:it.estado.id]
        if(it.complemento) endereco.complemento = it.complemento
        if(it.numero) endereco.numero = it.numero
        if(it.municipio) endereco.municipio = [id:it.municipio.id]
        if(it.bairro) endereco.bairro = [id:it.bairro.id]
        if(it.logradouro) endereco.logradouro =[id:it.logradouro.id]
        if(it.id) endereco.id = it.id
        if(it.cep) endereco.cep = it.cep
        
        return endereco
      }
    }
    
    if(credor.content.credorReinf?.origemNaturezaRendimento){
      credor.content.credorReinf?.origemNaturezaRendimento = credor.content.credorReinf?.origemNaturezaRendimento?.value
    }
  
    if(credor.content.tipo == "JURIDICA"){
		
      if(credor.content.juridica?.natureza){
      	credor.content.juridica.natureza.remove(\'descricao\')
      }
      
       if (credor.content.juridica.socios.isEmpty()) {
       
              credor.content.juridica?.remove(\'socios\')
          }
    }
   	
    if(!credor.content.telefones){
      credor.content.remove(\'telefones\')
    }else{
      credor.content.telefones = credor.content.telefones.collect{it->
        [
          numero: buscarTelefone(it.id),
          principal: it.principal.present,
          tipo: it.tipo,
          id: it.id
        ]
      }
    }
    
    if(!credor.content.emails){
      credor.content.remove(\'emails\')
    }else{
      credor.content.emails = credor.content.emails.collect{it->
        e_mail = [:]
        
        if(it.principal) e_mail.principal = it.principal.present
        if(it.id) e_mail.id = it.id
        if(it.email) e_mail.email = it.email
        if(it.descricao) e_mail.descricao = it.descricao
        
        return e_mail
      }
    }
    
    listaPut<<credor
    i++
  
  }
  
  listaPut.collate(50).each{credores->
	imprimir"ListaPutContasCredores: "+JSON.escrever(credores)
    url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/credores"
    servico = Http.servico(url).chaveIntegracao(Variavel.BTH_CONTABIL_CHAVE)
    resposta = servico.PUT(JSON.escrever(credores),Http.JSON)
    imprimir "LoteListaPutContasCredores: "+JSON.escrever(resposta.json())

  }

}



def buscarIdCredores(credores){
  
  credores.each{it->
    
    criterio = ""
    if(it.tipoPessoa == "FISICA"){
      criterio = "credorFisica.pessoaFisica.cpf = \'${it.cpfCnpj}\'"
    }
    if(it.tipoPessoa == "JURIDICA"){
      criterio = "credorJuridica.pessoaJuridica.cnpj = \'${it.cpfCnpj}\'"
    }
    
    idCredor = Dados.contabilidade.v1.credores.busca(criterio: criterio,campos: "id").collect{it.id}
    it.idCredor = !idCredor.isEmpty()?idCredor.first():0
  }
  return credores
}


def cadastrarCredor(credoresSemCadastro){
  
  listaPost =[]
  
  credoresSemCadastro.eachWithIndex{it,index->
    obj = []
    obj=[
      idIntegracao:"${index}",
      content:[
        nome: it.nome,
        dataInclusao: Datas.hoje().format("yyyy-MM-dd")
      ]
    ]
    
    if(it.tipoPessoa == "FISICA"){
      obj.content.tipo = "FISICA"
      obj.content.fisica = [cpf: it.cpfCnpj]
    }
    if(it.tipoPessoa == "JURIDICA"){
      obj.content.tipo = "JURIDICA"
      obj.content.juridica = [cnpj: it.cpfCnpj]
    }
    listaPost<<obj
  }
  
  listaPost.collate(50).each{credores->
    imprimir"Credores: "+JSON.escrever(credores)
    url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/credores"
    servico = Http.servico(url).chaveIntegracao(Variavel.BTH_CONTABIL_CHAVE)
    resposta = servico.POST(JSON.escrever(credores),Http.JSON)
    imprimir "LoteCredores: "+JSON.escrever(resposta.json())
  }
}



def cadastrarAgencias(credoresAgencias){
  
  listaPost = []
  i=0
  credoresAgencias.each{credor->
    
    if(credor.agencia.find("-")){
      agencia = credor.agencia.split("-")
      numero = agencia[0]
      digito = agencia[1]
      nome =  "Agencia "+numero+"-"+digito
    }else{
      numero = credor.agencia
      digito = null
      nome =  "Agencia "+numero
    }       
    obj=[
      content: [
        nome: nome,
        banco: [
          id: credor.banco
        ],
        numero: numero
      ]
    ]
    
    if(digito){
      obj.content.digito = digito
    }
    
    listaPost<<obj
    i++
   }
  
  listaPost = listaPost.unique()
  listaPost.eachWithIndex{agencia,index->
    agencia.idIntegracao = "${index}"
  }
  
  listaPost.collate(50).each{agencias->
    imprimir "Agencias: "+JSON.escrever(agencias)
    url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/agencias-bancarias"
    servico = Http.servico(url).chaveIntegracao(Variavel.BTH_CONTABIL_CHAVE)
    resposta = servico.POST(JSON.escrever(agencias),Http.JSON)
    imprimir "LotesAgencia: "+JSON.escrever(resposta.json())
  }
}


def buscaCredorById(idCredor){
  url = "https://con-sl-rest.betha.cloud/contabil/service-layer/v2/api/credores/${idCredor}"
  servico = Http.servico(url).chaveIntegracao(Variavel.BTH_CONTABIL_CHAVE).GET()
  return servico.json()
  
}


def buscarTelefone(idTelefone){
  numero = Dados.contabilidade.v1.telefones.busca(criterio: "id = ${idTelefone}",campos: "numero").collect{ it.numero }	
  if(numero.size()>0){
    return numero.first().toString()
  }
}

def contasToJson(conta,index){ //monta o json das contas colocando a primeira como principal 
  
    if(conta.contaCorrente.find("-")){
      numeroContaCorrente = conta.contaCorrente.split("-")[0]
      digitoContaCorrente = conta.contaCorrente.split("-")[1]
    }else{
      numeroContaCorrente = conta.contaCorrente
      digitoContaCorrente = null
    }
    
    obj = [
    	id:0,
      	banco:[
          id:conta.banco
              ],
      	agencia:[
          id:conta.agencia
        ],
      numero:numeroContaCorrente,
      tipo:"CORRENTE",
      dataAbertura: Datas.hoje().format("yyyy-MM-dd"),
      situacao:"ABERTA"
    ]
    
    if(digitoContaCorrente){
    obj.digito = digitoContaCorrente
    }
  
    obj.padrao = false
 
  return obj
}



def BuscaIdBancoFebraban(numeroBanco){
  MapBancos = [:]
  MapBancos["001"] =[idBanco:137,    descricao:"Banco do Brasil S.A.                                                  "]
  MapBancos["002"] =[idBanco:625,    descricao:"BANCO CENTRAL DO BRASIL                                               "]
  MapBancos["003"] =[idBanco:130,    descricao:"Banco da Amazônia S.A.                                                "]
  MapBancos["004"] =[idBanco:142,    descricao:"Banco do Nordeste do Brasil S.A.                                      "]
  MapBancos["006"] =[idBanco:671,    descricao:"BANCO BNCC S.A.                                                       "]
  MapBancos["007"] =[idBanco:641,    descricao:"Banco Nacional de Desenvolvimento Econômico e Social BNDES            "]
  MapBancos["008"] =[idBanco:556,    descricao:"Banco Meridional do Brasil S.A.                                       "]
  MapBancos["010"] =[idBanco:662,    descricao:"Credicoamo Crédito Rural Cooperativa                                  "]
  MapBancos["012"] =[idBanco:119,    descricao:"Banco Standard de Investimentos S.A.                                  "]
  MapBancos["014"] =[idBanco:168,    descricao:"Natixis Brasil S.A. Banco Múltiplo                                    "]
  MapBancos["017"] =[idBanco:9  ,    descricao:"BNY Mellon Banco S.A.                                                 "]
  MapBancos["018"] =[idBanco:123,    descricao:"Banco Tricury S.A.                                                    "]
  MapBancos["019"] =[idBanco:18 ,    descricao:"Banco Azteca do Brasil S.A.                                           "]
  MapBancos["020"] =[idBanco:607,    descricao:"BANCO DO ESTADO DE ALAGOAS S.A.                                       "]
  MapBancos["021"] =[idBanco:4  ,    descricao:"BANESTES S.A. Banco do Estado do Espírito Santo                       "]
  MapBancos["022"] =[idBanco:525,    descricao:"BANCO DE CREDITO REAL DE MINAS GERAIS S.A.                            "]
  MapBancos["023"] =[idBanco:526,    descricao:"BANCO DE DESENVOLVIMENTO DE MINAS GERAIS S.A.                         "]
  MapBancos["024"] =[idBanco:19 ,    descricao:"Banco BANDEPE S.A.                                                    "]
  MapBancos["025"] =[idBanco:15 ,    descricao:"Banco Alfa S.A.                                                       "]
  MapBancos["026"] =[idBanco:536,    descricao:"BANCO DO ESTADO DO ACRE S.A.                                          "]
  MapBancos["027"] =[idBanco:1  ,    descricao:"BANCO DO ESTADO DE SANTA CATARINA S.A.                                "]
  MapBancos["028"] =[idBanco:530,    descricao:"BANCO DO ESTADO DA BAHIA S.A.                                         "]
  MapBancos["029"] =[idBanco:26 ,    descricao:"Banco Banerj S.A.                                                     "]
  MapBancos["030"] =[idBanco:531,    descricao:"BANCO DO ESTADO DA PARAIBA S.A.                                       "]
  MapBancos["031"] =[idBanco:28 ,    descricao:"Banco Beg S.A.                                                        "]
  MapBancos["032"] =[idBanco:532,    descricao:"BANCO DO ESTADO DE MATO GROSSO S.A.                                   "]
  MapBancos["033"] =[idBanco:114,    descricao:"Banco Santander (Brasil) S.A.                                         "]
  MapBancos["034"] =[idBanco:537,    descricao:"BANCO DO ESTADO DO AMAZONAS S.A.                                      "]
  MapBancos["035"] =[idBanco:538,    descricao:"BANCO DO ESTADO DO CEARA S.A.                                         "]
  MapBancos["036"] =[idBanco:32 ,    descricao:"Banco Bradesco BBI S.A.                                               "]
  MapBancos["037"] =[idBanco:139,    descricao:"Banco do Estado do Pará S.A.                                          "]
  MapBancos["038"] =[idBanco:2  ,    descricao:"BANCO DO ESTADO DO PARANA S.A.                                        "]
  MapBancos["039"] =[idBanco:140,    descricao:"Banco do Estado do Piauí S.A. - BEP                                   "]
  MapBancos["040"] =[idBanco:42 ,    descricao:"Banco Cargill S.A.                                                    "]
  MapBancos["041"] =[idBanco:141,    descricao:"Banco do Estado do Rio Grande do Sul S.A.                             "]
  MapBancos["044"] =[idBanco:25 ,    descricao:"Banco BVA S.A.                                                        "]
  MapBancos["045"] =[idBanco:92 ,    descricao:"Banco Opportunity S.A.                                                "]
  MapBancos["046"] =[idBanco:564,    descricao:"BANCO REGIONAL DE DESENVOLVIMENTO DO EXTREMO SUL                      "]
  MapBancos["047"] =[idBanco:138,    descricao:"Banco do Estado de Sergipe S.A.                                       "]
  MapBancos["048"] =[idBanco:533,    descricao:"BANCO DO ESTADO DE MINAS GERAIS S.A.                                  "]
  MapBancos["048"] =[idBanco:599,    descricao:"Banco do Estado de Minas Gerais S.A                                   "]
  MapBancos["049"] =[idBanco:528,    descricao:"BANCO DE DESENVOLVIMENTO DO ESTADO DA BAHIA S.A.                      "]
  MapBancos["051"] =[idBanco:527,    descricao:"BANCO DE DESENVOLVIMENTO DO ESPIRITO SANTO S.A.                       "]
  MapBancos["057"] =[idBanco:529,    descricao:"BANCO DE DESENVOLVIMENTO DO ESTADO DE SANTA CATARI                    "]
  MapBancos["059"] =[idBanco:534,    descricao:"BANCO DO ESTADO DE RONDONIA S.A.                                      "]
  MapBancos["062"] =[idBanco:162,    descricao:"Hipercard Banco Múltiplo S.A.                                         "]
  MapBancos["063"] =[idBanco:69 ,    descricao:"Banco Ibi S.A. Banco Múltiplo                                         "]
  MapBancos["064"] =[idBanco:159,    descricao:"Goldman Sachs do Brasil Banco Múltiplo S.A.                           "]
  MapBancos["065"] =[idBanco:31 ,    descricao:"Banco Bracce S.A.                                                     "]
  MapBancos["066"] =[idBanco:90 ,    descricao:"Banco de Crédito e Varejo S.A.                                        "]
  MapBancos["069"] =[idBanco:35 ,    descricao:"Banco Crefisa S.A.                                                    "]
  MapBancos["070"] =[idBanco:143,    descricao:"BRB - Banco de Brasília S.A.                                          "]
  MapBancos["072"] =[idBanco:145,    descricao:"Banco J. Safra S.A.                                                   "]
  MapBancos["073"] =[idBanco:20 ,    descricao:"BB Banco Popular do Brasil S.A.                                       "]
  MapBancos["074"] =[idBanco:146,    descricao:"Banco J. Safra S.A.                                                   "]
  MapBancos["075"] =[idBanco:147,    descricao:"Banco CR2 S.A.                                                        "]
  MapBancos["076"] =[idBanco:148,    descricao:"Banco KDB S.A.                                                        "]
  MapBancos["077"] =[idBanco:149,    descricao:"Banco Intermedium S.A.                                                "]
  MapBancos["078"] =[idBanco:150,    descricao:"BES Investimento do Brasil S.A. - Banco de Investimento               "]
  MapBancos["079"] =[idBanco:151,    descricao:"JBS Banco S.A.                                                        "]
  MapBancos["081"] =[idBanco:152,    descricao:"Concórdia Banco S.A.                                                 "]
  MapBancos["082"] =[idBanco:153,    descricao:"Banco Topázio S.A.                                                    "]
  MapBancos["083"] =[idBanco:154,    descricao:"Banco da China Brasil S.A.                                            "]
  MapBancos["084"] =[idBanco:155,    descricao:"Unicred Norte do Paraná                                               "]
  MapBancos["085"] =[idBanco:156,    descricao:"Cooperativa Central de Crédito Urbano-CECRED                          "]
  MapBancos["086"] =[idBanco:157,    descricao:"OBOE Crédito Financiamento e Investimento S.A.                        "]
  MapBancos["087"] =[idBanco:158,    descricao:"Cooperativa de Crédito Rural da Região de Mogiana                     "]
  MapBancos["089"] =[idBanco:160,    descricao:"Cooperativa de Crédito Rural da Região da Alta Mogiana                "]
  MapBancos["090"] =[idBanco:161,    descricao:"Cooperativa Central de Economia e Crédito Mutuo das Unicreds            "]
  MapBancos["091"] =[idBanco:163,    descricao:"Unicred Central do Rio Grande do Sul                                  "]
  MapBancos["092"] =[idBanco:164,    descricao:"Brickell S.A. Crédito, financiamento e Investimento                   "]
  MapBancos["093"] =[idBanco:165,    descricao:"Pólocred S.A. - Crédito, Financiamento e Investimento                 "]
  MapBancos["094"] =[idBanco:166,    descricao:"Banco Petra S.A.                                                      "]
  MapBancos["095"] =[idBanco:167,    descricao:"Banco Confidence de Câmbio S.A.                                       "]
  MapBancos["096"] =[idBanco:169,    descricao:"Banco BM&FBOVESPA de Serviços de Liquidação e Custódia S.A            "]
  MapBancos["097"] =[idBanco:170,    descricao:"Cooperativa Central de Crédito Noroeste Brasileiro Ltda.              "]
  MapBancos["098"] =[idBanco:171,    descricao:"Credicorol Cooperativa de Crédito Rural                               "]
  MapBancos["099"] =[idBanco:172,    descricao:"Cooperativa de Crédito Rural de Primavera do Leste                      "]
  MapBancos["100"] =[idBanco:173,    descricao:"Planner Corretora de Valores S.A.                                     "]
  MapBancos["101"] =[idBanco:174,    descricao:"Renascença Distribuidora de Títulos e Valores Mobiliários Ltda        "]
  MapBancos["102"] =[idBanco:175,    descricao:"XP Investimentos Corretora de Câmbio, Títulos e Valores Mobiliários S.A"]
  MapBancos["104"] =[idBanco:136,    descricao:"Caixa Econômica Federal                                                 "]
  MapBancos["105"] =[idBanco:176,    descricao:"Lecca Crédito, Financiamento e Investimento S/A                       "]
  MapBancos["107"] =[idBanco:177,    descricao:"Banco BBM S.A.                                                        "]
  MapBancos["111"] =[idBanco:178,    descricao:"Oliveira Trust Distribuidora de Títulos e Valores Mobiliários S.A     "]
  MapBancos["113"] =[idBanco:179,    descricao:"Magliano S.A. Corretora de Câmbio e Valores Mobiliários               "]
  MapBancos["114"] =[idBanco:180,    descricao:"Central Cooperativa de Crédito no Estado do Espírito Santo            "]
  MapBancos["117"] =[idBanco:181,    descricao:"Advanced Corretora de Câmbio Ltda.                                    "]
  MapBancos["118"] =[idBanco:182,    descricao:"Standard Chartered Bank (Brasil) S/A–Bco Invest.                      "]
  MapBancos["119"] =[idBanco:183,    descricao:"Banco Western Union do Brasil S.A.                                    "]
  MapBancos["120"] =[idBanco:184,    descricao:"Banco Rodobens S.A.                                                   "]
  MapBancos["121"] =[idBanco:185,    descricao:"Banco Agiplan S.A.                                                    "]
  MapBancos["122"] =[idBanco:186,    descricao:"Banco Bradesco BERJ S.A.                                              "]
  MapBancos["124"] =[idBanco:187,    descricao:"Banco Woori Bank do Brasil S.A.                                       "]
  MapBancos["125"] =[idBanco:188,    descricao:"Brasil Plural S.A. - Banco Múltiplo                                   "]
  MapBancos["126"] =[idBanco:189,    descricao:"BR Partners Banco de Investimento S.A.                                "]
  MapBancos["127"] =[idBanco:190,    descricao:"Codepe Corretora de Valores e Câmbio S.A.                             "]
  MapBancos["128"] =[idBanco:191,    descricao:"MS Bank S.A. Banco de Câmbio                                          "]
  MapBancos["129"] =[idBanco:192,    descricao:"UBS Brasil Banco de Investimento S.A.                                 "]
  MapBancos["130"] =[idBanco:193,    descricao:"Caruana S.A. - Sociedade de Crédito, Financiamento e Investimento     "]
  MapBancos["131"] =[idBanco:194,    descricao:"Tullett Prebon Brasil Corretora de Valores e Câmbio Ltda              "]
  MapBancos["132"] =[idBanco:195,    descricao:"ICBC do Brasil Banco Múltiplo S.A.                                    "]
  MapBancos["133"] =[idBanco:196,    descricao:"Confederacao Nacional das Cooperativas Centrais de Credito e Economia Familiar e Solidario - CRESOL"]
  MapBancos["134"] =[idBanco:197,    descricao:"BGC Liquidez Distribuidora de Títulos e Valores Mobiliários Ltda      "]
  MapBancos["135"] =[idBanco:198,    descricao:"Gradual Corretora de Câmbio, Títulos e Valores Mobiliários S.A.       "]
  MapBancos["136"] =[idBanco:199,    descricao:"Confederação Nacional das Cooperativas Centrais Unicred do Brasil – Unicred do Brasil"]
  MapBancos["137"] =[idBanco:200,    descricao:"Multimoney Corretora de Câmbio Ltda                                   "]
  MapBancos["138"] =[idBanco:201,    descricao:"Get Money Corretora de Câmbio S.A.                                    "]
  MapBancos["139"] =[idBanco:202,    descricao:"Intesa Sanpaolo Brasil S.A. - Banco Múltiplo                          "]
  MapBancos["140"] =[idBanco:203,    descricao:"Easynvest - Título Corretora de Valores SA                            "]
  MapBancos["142"] =[idBanco:204,    descricao:"Broker Brasil Corretora de Câmbio Ltda.                               "]
  MapBancos["143"] =[idBanco:205,    descricao:"Treviso Corretora de Câmbio S.A.                                      "]
  MapBancos["144"] =[idBanco:206,    descricao:"Bexs Banco de Câmbio S.A.                                             "]
  MapBancos["145"] =[idBanco:207,    descricao:"Levycam - Corretora de Câmbio e Valores Ltda.                         "]
  MapBancos["146"] =[idBanco:208,    descricao:"Guitta Corretora de Câmbio Ltda.                                      "]
  MapBancos["147"] =[idBanco:209,    descricao:"Facta Financeira S.A. - Crédito Financiamento e Investimento          "]
  MapBancos["149"] =[idBanco:210,    descricao:"Banco IBM S.A.                                                        "]
  MapBancos["157"] =[idBanco:211,    descricao:"ICAP do Brasil Corretora de Títulos e Valores Mobiliários Ltda.       "]
  MapBancos["159"] =[idBanco:212,    descricao:"Casa do Crédito S.A. - Sociedade de Crédito ao Microempreendedor      "]
  MapBancos["163"] =[idBanco:213,    descricao:"Commerzbank Brasil S.A. - Banco Múltiplo                              "]
  MapBancos["169"] =[idBanco:214,    descricao:"Banco Olé Bonsucesso Consignado S.A.                                  "]
  MapBancos["172"] =[idBanco:215,    descricao:"Albatross Corretora de Câmbio e Valores S.A                           "]
  MapBancos["173"] =[idBanco:216,    descricao:"BRL Trust Distribuidora de Títulos e Valores Mobiliários S.A.         "]
  MapBancos["174"] =[idBanco:217,    descricao:"Pernambucanas Financiera S.A. - Crédito, Financiamento e Investimento   "]
  MapBancos["177"] =[idBanco:218,    descricao:"Guide Investimentos S.A. Corretora de Valores                         "]
  MapBancos["180"] =[idBanco:219,    descricao:"CM Capital Markets Corretora de Câmbio, Títulos e Valores Mobiliários Ltda"]
  MapBancos["182"] =[idBanco:220,    descricao:"Dacasa Financeira S/A - Sociedade de Crédito, Financiamento e Investimento"]
  MapBancos["183"] =[idBanco:221,    descricao:"Socred S.A. - Sociedade de Crédito ao Microempreendedor               "]
  MapBancos["184"] =[idBanco:222,    descricao:"Banco Itaú BBA S.A.                                                   "]
  MapBancos["188"] =[idBanco:223,    descricao:"Ativa Investimentos S.A. Corretora de Títulos, Câmbio e Valores       "]
  MapBancos["189"] =[idBanco:224,    descricao:"HS Financeira S/A Crédito, Financiamento e Investimentos              "]
  MapBancos["190"] =[idBanco:225,    descricao:"Cooperativa de Economia e Crédito Mútuo dos Servidores Públicos       "]
  MapBancos["191"] =[idBanco:226,    descricao:"Nova Futura Corretora de Títulos e Valores Mobiliários Ltda.          "]
  MapBancos["194"] =[idBanco:227,    descricao:"Parmetal Distribuidora de Títulos e Valores Mobiliários Ltda          "]
  MapBancos["196"] =[idBanco:228,    descricao:"Fair Corretora de Câmbio S.A.                                         "]
  MapBancos["197"] =[idBanco:229,    descricao:"Stone Pagamentos S.A.                                                 "]
  MapBancos["204"] =[idBanco:36 ,    descricao:"Banco Bradesco Cartões S.A.                                           "]
  MapBancos["208"] =[idBanco:37 ,    descricao:"Banco BTG Pactual S.A.                                                "]
  MapBancos["212"] =[idBanco:38 ,    descricao:"Banco Original S.A.                                                   "]
  MapBancos["213"] =[idBanco:39 ,    descricao:"Banco Arbi S.A.                                                       "]
  MapBancos["214"] =[idBanco:40 ,    descricao:"Banco Dibens S.A.                                                     "]
  MapBancos["215"] =[idBanco:41 ,    descricao:"Banco Comercial e de Investimento Sudameris S.A.                      "]
  MapBancos["217"] =[idBanco:43 ,    descricao:"Banco John Deere S.A.                                                 "]
  MapBancos["218"] =[idBanco:44 ,    descricao:"Banco Bonsucesso S.A.                                                 "]
  MapBancos["222"] =[idBanco:45 ,    descricao:"Banco Credit Agricole Brasil S.A.                                     "]
  MapBancos["224"] =[idBanco:46 ,    descricao:"Banco Fibra S.A.                                                      "]
  MapBancos["225"] =[idBanco:47 ,    descricao:"Banco Brascan S.A.                                                    "]
  MapBancos["229"] =[idBanco:48 ,    descricao:"Banco Cruzeiro do Sul S.A.                                            "]
  MapBancos["230"] =[idBanco:49 ,    descricao:"Unicard Banco Múltiplo S.A.                                           "]
  MapBancos["233"] =[idBanco:50 ,    descricao:"Banco GE Capital S.A.                                                 "]
  MapBancos["237"] =[idBanco:51 ,    descricao:"Banco Bradesco S.A.                                                   "]
  MapBancos["241"] =[idBanco:52 ,    descricao:"Banco Clássico S.A.                                                   "]
  MapBancos["243"] =[idBanco:53 ,    descricao:"Banco Máxima S.A.                                                     "]
  MapBancos["246"] =[idBanco:54 ,    descricao:"Banco ABC Brasil S.A.                                                 "]
  MapBancos["248"] =[idBanco:55 ,    descricao:"Banco Boavista Interatlântico S.A.                                    "]
  MapBancos["249"] =[idBanco:56 ,    descricao:"Banco Investcred Unibanco S.A.                                        "]
  MapBancos["250"] =[idBanco:57 ,    descricao:"BCV - Banco de Crédito e Varejo S.A.                                  "]
  MapBancos["252"] =[idBanco:58 ,    descricao:"Fininvest S.A. - Banco Múltiplo                                       "]
  MapBancos["254"] =[idBanco:59 ,    descricao:"Paraná Banco S.A.                                                     "]
  MapBancos["260"] =[idBanco:60 ,    descricao:"Nu Pagamentos S.A.                                                    "]
  MapBancos["263"] =[idBanco:61 ,    descricao:"Banco Cacique S.A.                                                    "]
  MapBancos["265"] =[idBanco:62 ,    descricao:"Banco Fator S.A.                                                      "]
  MapBancos["266"] =[idBanco:63 ,    descricao:"Banco Cédula S.A.                                                     "]
  MapBancos["300"] =[idBanco:64 ,    descricao:"Banco de La Nacion Argentina                                          "]
  MapBancos["318"] =[idBanco:65 ,    descricao:"Banco BMG S.A.                                                        "]
  MapBancos["320"] =[idBanco:66 ,    descricao:"Banco Industrial e Comercial S.A.                                     "]
  MapBancos["341"] =[idBanco:67 ,    descricao:"Itaú Unibanco S.A.                                                    "]
  MapBancos["356"] =[idBanco:68 ,    descricao:"Banco Real S.A.                                                       "]
  MapBancos["366"] =[idBanco:70 ,    descricao:"Banco Société Générale Brasil S.A.                                    "]
  MapBancos["370"] =[idBanco:71 ,    descricao:"Banco Mizuho do Brasil S.A.                                           "]
  MapBancos["376"] =[idBanco:72 ,    descricao:"Banco J. P. Morgan S.A.                                               "]
  MapBancos["389"] =[idBanco:73 ,    descricao:"Banco Mercantil do Brasil S.A.                                        "]
  MapBancos["394"] =[idBanco:74 ,    descricao:"Banco Finasa BMC S.A.                                                 "]
  MapBancos["399"] =[idBanco:75 ,    descricao:"HSBC Bank Brasil S.A. - Banco Múltiplo                                "]
  MapBancos["409"] =[idBanco:76 ,    descricao:"UNIBANCO - União de Bancos Brasileiros S.A.                           "]
  MapBancos["412"] =[idBanco:77 ,    descricao:"Banco Capital S.A.                                                    "]
  MapBancos["422"] =[idBanco:78 ,    descricao:"Banco Safra S.A.                                                      "]
  MapBancos["453"] =[idBanco:79 ,    descricao:"Banco Rural S.A.                                                      "]
  MapBancos["456"] =[idBanco:80 ,    descricao:"Banco de Tokyo-Mitsubishi UFJ Brasil S.A.                             "]
  MapBancos["464"] =[idBanco:81 ,    descricao:"Banco Sumitomo Mitsui Brasileiro S.A.                                 "]
  MapBancos["473"] =[idBanco:82 ,    descricao:"Banco Caixa Geral - Brasil S.A.                                       "]
  MapBancos["477"] =[idBanco:83 ,    descricao:"Citibank N.A.                                                         "]
  MapBancos["479"] =[idBanco:84 ,    descricao:"Banco ItauBank S.A.                                                   "]
  MapBancos["487"] =[idBanco:85 ,    descricao:"Deutsche Bank S.A. - Banco Alemão                                     "]
  MapBancos["488"] =[idBanco:86 ,    descricao:"JPMorgan Chase Bank, National Association                             "]
  MapBancos["492"] =[idBanco:87 ,    descricao:"ING Bank N.V.                                                         "]
  MapBancos["494"] =[idBanco:88 ,    descricao:"Banco de La Republica Oriental del Uruguay                            "]
  MapBancos["495"] =[idBanco:89 ,    descricao:"Banco de La Provincia de Buenos Aires                                 "]
  MapBancos["505"] =[idBanco:91 ,    descricao:"Banco Credit Suisse (Brasil) S.A.                                     "]
  MapBancos["600"] =[idBanco:93 ,    descricao:"Banco Luso Brasileiro S.A.                                            "]
  MapBancos["604"] =[idBanco:94 ,    descricao:"Banco Industrial do Brasil S.A.                                       "]
  MapBancos["610"] =[idBanco:95 ,    descricao:"Banco VR S.A.                                                         "]
  MapBancos["611"] =[idBanco:96 ,    descricao:"Banco Paulista S.A.                                                   "]
  MapBancos["612"] =[idBanco:97 ,    descricao:"Banco Guanabara S.A.                                                  "]
  MapBancos["613"] =[idBanco:98 ,    descricao:"Banco Pecúnia S.A.                                                    "]
  MapBancos["623"] =[idBanco:99 ,    descricao:"Banco PAN S.A.                                                        "]
  MapBancos["626"] =[idBanco:100,    descricao:"Banco Ficsa S.A.                                                      "]
  MapBancos["630"] =[idBanco:101,    descricao:"Banco Intercap S.A.                                                   "]
  MapBancos["633"] =[idBanco:102,    descricao:"Banco Rendimento S.A.                                                 "]
  MapBancos["634"] =[idBanco:103,    descricao:"Banco Triângulo S.A.                                                  "]
  MapBancos["637"] =[idBanco:104,    descricao:"Banco Sofisa S.A.                                                     "]
  MapBancos["638"] =[idBanco:105,    descricao:"Banco Prosper S.A.                                                    "]
  MapBancos["641"] =[idBanco:106,    descricao:"Banco Alvorada S.A.                                                   "]
  MapBancos["643"] =[idBanco:107,    descricao:"Banco Pine S.A.                                                       "]
  MapBancos["652"] =[idBanco:108,    descricao:"Itaú Unibanco Holding S.A.                                            "]
  MapBancos["653"] =[idBanco:109,    descricao:"Banco Indusval S.A.                                                   "]
  MapBancos["654"] =[idBanco:110,    descricao:"Banco A.J.Renner S.A.                                                 "]
  MapBancos["655"] =[idBanco:111,    descricao:"Banco Votorantim S.A.                                                 "]
  MapBancos["658"] =[idBanco:112,    descricao:"Banco Porto Real S.A.                                                 "]
  MapBancos["707"] =[idBanco:113,    descricao:"Banco Daycoval S.A.                                                   "]
  MapBancos["719"] =[idBanco:115,    descricao:"Banif-Banco Internacional do Funchal (Brasil),S.A.                    "]
  MapBancos["721"] =[idBanco:116,    descricao:"Banco Credibel S.A.                                                   "]
  MapBancos["734"] =[idBanco:117,    descricao:"Banco Gerdau S.A.                                                     "]
  MapBancos["735"] =[idBanco:118,    descricao:"Banco Pottencial S.A.                                                 "]
  MapBancos["738"] =[idBanco:120,    descricao:"Banco Morada S.A.                                                     "]
  MapBancos["739"] =[idBanco:121,    descricao:"Banco BGN S.A.                                                        "]
  MapBancos["740"] =[idBanco:122,    descricao:"Banco Barclays S.A.                                                   "]
  MapBancos["741"] =[idBanco:124,    descricao:"Banco Ribeirão Preto S.A.                                             "]
  MapBancos["743"] =[idBanco:125,    descricao:"Banco Semear S.A.                                                     "]
  MapBancos["745"] =[idBanco:126,    descricao:"Banco Citibank S.A.                                                   "]
  MapBancos["746"] =[idBanco:127,    descricao:"Banco Modal S.A.                                                      "]
  MapBancos["747"] =[idBanco:128,    descricao:"Banco Rabobank International Brasil S.A.                              "]
  MapBancos["748"] =[idBanco:129,    descricao:"Banco Cooperativo Sicredi S.A.                                        "]
  MapBancos["749"] =[idBanco:131,    descricao:"Banco Simples S.A.                                                    "]
  MapBancos["751"] =[idBanco:132,    descricao:"Scotiabank Brasil S.A. Banco Múltiplo                                 "]
  MapBancos["752"] =[idBanco:133,    descricao:"Banco BNP Paribas Brasil S.A.                                         "]
  MapBancos["753"] =[idBanco:134,    descricao:"NBC Bank Brasil S.A. - Banco Múltiplo                                 "]
  MapBancos["755"] =[idBanco:135,    descricao:"Bank of America Merrill Lynch Banco Múltiplo S.A.                     "]
  MapBancos["756"] =[idBanco:144,    descricao:"Banco Cooperativo do Brasil S.A. - BANCOOB                            "]
  MapBancos["757"] =[idBanco:16 ,    descricao:"Banco KEB DO BRASIL S.A.                                              "]
  return MapBancos[numeroBanco].idBanco
}
```

