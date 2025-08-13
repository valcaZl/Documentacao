# Documentação do Script de Encerramento Contábil

Este script Groovy é responsável por realizar o encerramento contábil de um exercício, transferindo saldos de contas específicas para contas de contrapartida, gerando lançamentos contábeis e organizando-os em arquivos CSV para importação. Ele lida com a busca de dados de balancete, mapeamento de contas contábeis e contas correntes, e a criação de arquivos de lançamento, itens de lançamento e contas correntes.

## Explicação Geral do Código

O script automatiza o processo de encerramento contábil, focando na transferência de saldos de contas de resultado para contas de patrimônio líquido ou outras contas de encerramento. Ele utiliza parâmetros de entrada como entidade, exercício e data de lançamento. O script busca contas contábeis e suas configurações, além de dados de balancete para identificar os saldos a serem encerrados. Com base em um roteiro contábil predefinido, ele gera lançamentos de débito e crédito, tratando múltiplos roteiros e a inversão de saldos quando necessário. Finalmente, os lançamentos, seus itens e as contas correntes associadas são organizados e exportados para arquivos CSV separados, que são então compactados em um arquivo ZIP para download, juntamente com um arquivo de metadados JSON.

## Blocos de Código

### Parâmetros e Configurações Iniciais

```groovy
EncerramentoUtil = importar 'bth.contabil.utilitarios.encerramento.inicio'
ArquivoUtil =  importar 'bth.contabil.encerramentoinicio.gerar.arquivo'

def entidade = parametros.entidade.selecionado?.valor
def exercicio = parametros.pDataLanc.valor.formatar('yyyy');
def protocolo = contextoExecucao.idProtocolo
//def idFase = parametros.idFase.valor
def dataLanc = parametros.pDataLanc.valor.formatar('yyyy-MM-dd');
def dataInicial = (exercicio+"-01-01");
def dataFinal = (exercicio+"-01-01");
def idPlanoContas = EncerramentoUtil.getPlanoContas(entidade,exercicio)
def newMapLancto = [:]

def mapContraPartidas = [:] // mapa que irá armazenar os dados das contas que receberão saldo (id,mascara,descrição..)
def final codigoLancamento = 1
def final mascarasEncerradas = ["8211101"] 
def final mascaraContraPartidaAnalitica = ["8211102000000000000"]
def final historicoLancamento = "Início de exercício: Transferência das disponibilidades por destinação de recursos do exercício para exercícios anteriores."
def LancamentosContabeis = [:]
// CONFIGURAÇÃO DA FASE DE ENCERRAMENTO
imprimir "Entidade : ".concat(String.valueOf(entidade)) // subtituir pelo parametro entidade
imprimir "Exercício : ".concat(String.valueOf(exercicio)) // subtituir pelo parametro exercicio
imprimir "idPlanoContas : ".concat(String.valueOf(idPlanoContas))
imprimir "Data Lanc : ".concat(String.valueOf(dataLanc))

// DADOS DO LANCAMENTO
newMapLancto[codigoLancamento] = [
  codigoLancamento : codigoLancamento ,
  historico : historicoLancamento
]
```

Este bloco inicializa variáveis importantes e importa utilitários. Ele define parâmetros de entrada como `entidade`, `exercicio` e `dataLanc`, e busca o `idPlanoContas` usando uma função auxiliar. Também define constantes para o lançamento contábil, como `codigoLancamento`, `mascarasEncerradas` e o `historicoLancamento`.

### Roteiro Contábil e Mapeamento de Contas de Contrapartida

```groovy
def roterioContabil = { roteiro ->
  mascRetorno = ""
  switch(roteiro) {
    case {it.expressao(/^8211101/).encontrouPadrao()} : mascRetorno = mapContraPartidas["8211102000000000000"].dadosConta ; break ;
    default: "" ;
  }
  //    imprimir "$roteiro  >> ".concat(String.valueOf(mascRetorno[0]))
  return mascRetorno
}


if(mascaraContraPartidaAnalitica.size() > 0) {
  def criterioConta = "configuracao.id = $idPlanoContas"
  criterioConta += " and mascara in ("
  isBoolean = false
  for(i = 0; i < mascaraContraPartidaAnalitica.size(); i++){
    criterioConta += "'${mascaraContraPartidaAnalitica[i]}'";
    if(i != (mascaraContraPartidaAnalitica.size() -1) ){ criterioConta += ","}
  }
  criterioConta += ")"
  def fonteConta = Dados.contabilidade.v1.contaContabil
  fonteConta = fonteConta.busca(campos: "mascara,id,mascaraFormatada" , criterio : criterioConta)
  for(conta in fonteConta){
    dadosConta = []
    dadosConta << [idConta : conta.id, mascara : conta.mascara , mascaraFormatada : conta.mascaraFormatada]
    mapContraPartidas[conta.mascara] = [dadosConta : dadosConta]
  }
}else {
  if (mascarasEncerradas.size() > 0) {
    def criterioConta = "configuracao.id = $idPlanoContas and tipo = 'ANALITICO'"
    criterioConta += " and ("
    isBoolean = false
    for (i = 0; i < mascarasEncerradas.size(); i++) {
      criterioConta += "mascara like '${mascarasEncerradas[i]}%'"
      if (i != (mascarasEncerradas.size() - 1)) {
        criterioConta += " or "
      }
    }
    criterioConta += ")"
    def fonteConta = Dados.contabilidade.v1.contaContabil
    fonteConta = fonteConta.busca(campos: "mascara,id,mascaraFormatada", criterio: criterioConta)
    for (conta in fonteConta) {
      dadosConta = []
      dadosConta << [idConta: conta.id, mascara: conta.mascara, mascaraFormatada: conta.mascaraFormatada]
      mapContraPartidas[conta.mascara] = [dadosConta: dadosConta]
    }
  }
}
```

Esta seção define a lógica para o roteiro contábil, que determina a conta de contrapartida para o encerramento. Ele busca contas contábeis com base nas máscaras definidas (`mascarasEncerradas` e `mascaraContraPartidaAnalitica`) e as armazena em `mapContraPartidas`.

### Busca de Dados do Balancete e Geração de Itens de Lançamento

```groovy
def fonteBalancete = Dados.contabilidade.v1.balanceteDinamicoContaCorrenteComSaldo
def param = [
  exercicio : exercicio ,
  entidadeId : entidade ,
  configuracaoPlanoContasId : idPlanoContas,
  dataInicial : dataInicial,
  dataFinal :  dataFinal
]

def criterioFonte = "conta.tipo = 'A' and identificacao.tipo = 'I'"

if(mascarasEncerradas.size() > 0){
  criterioFonte += " and ("
  isBoolean = false
  for(i = 0; i < mascarasEncerradas.size(); i++){
    criterioFonte += "conta.mascara like '${mascarasEncerradas[i]}*'"
    if(i != (mascarasEncerradas.size() -1) ){ criterioFonte += " or "}
  }
  criterioFonte += ")"
}
//imprimir criterioFonte

fonteBalancete = fonteBalancete.busca(campos: "conta(id, mascara, mascaraFormatada), contasCorrentes(contaCorrente(descricao, componentes(posicao, propriedade, valor), lote),saldoAtual),saldoAtual" , criterio : criterioFonte, parametros : param , ordenacao : "conta.mascara asc");
def countPar = 0
def countItem = 0
def newMapItens = [:]
for(fonte in fonteBalancete){
  //    countPar++
  //    countItem++
  //    countDe = countItem
  //    countItem++
  //    countPara = countItem
  valorLancamento = BigDecimal.valueOf(fonte.contasCorrentes.findAll { it.contaCorrente?.lote == 'Gerencial' && it.saldoAtual < 0}.sum { it.saldoAtual }?:0.00)
  if( valorLancamento == 0.00) continue ;
  def roteiro = roterioContabil(fonte.conta.mascara)
  def itens = []
  isMultiploRoteiro = roteiro.size() > 1 ? true : false
  if(isMultiploRoteiro){ // em um roteiro normal temos sempre um par de laçamento sendo feito, porem existem cenários em que podemos ter mais de um duas contas fazendo parte do mesmo 'par' do lançamento
    itens = []
    countPar++ // incrementando o par do lançamento
      
      tipoLancto =  ((valorLancamento > 0) ? "C" : "D")
    // fazendo o lancamento de encerramento da conta que realmente deve ser encerrada
    countItem++
      
      itens << [
        codigoLancto   : codigoLancamento,
        codigoItem     : countItem,
        par            : countPar,
        codigoConta    : fonte.conta.id,
        mascara        : fonte.conta.mascaraFormatada,
        tipo           : tipoLancto,
        valor          : valorLancamento.abs(),
        lanctoItemContaCorrente : [:]
      ]
    // agora vamos fazer um laço de repetição para o multiplo roteiro contabil conforme já foi configurado na
    for(i in 0..(roteiro.size()-1)){
      countItem++
        itens << [
          codigoLancto   : codigoLancamento,
          codigoItem     : countItem,
          par            : countPar,
          codigoConta    : roteiro[i]?.idConta ,
          mascara        : roteiro[i]?.mascaraFormatada,
          tipo           : (roteiro[i]?.saldoInvertido == true) ? EncerramentoUtil.inverteTipoLancto(tipoLancto) : tipoLancto,
          valor          : valorLancamento.abs(),
          lanctoItemContaCorrente : [:]
        ]
    }
  }else{ // em um roteiro normal temos sempre um par de laçamento sendo feito
    
    itens = []
    countPar++ // incrementando o par do lançamento
      for(i in 1..2) {
        countItem++ // incrementando o item do lançamento
          
          tipoLancto =  ((valorLancamento > 0) ? "C" : "D")
        itens << [
          codigoLancto   : codigoLancamento,
          codigoItem     : countItem,
          par            : countPar,
          codigoConta    : (i == 1) ? fonte.conta.id : roteiro[0]?.idConta ,
          mascara        : (i == 1 ) ? fonte.conta.mascaraFormatada : roteiro[0]?.mascaraFormatada,
          tipo           : (i == 1) ? tipoLancto : EncerramentoUtil.inverteTipoLancto(tipoLancto),
          valor          : valorLancamento.abs(),
          lanctoItemContaCorrente : [:]
        ]
      }
  }
  
  if(!newMapItens[fonte.conta.id]) {
    newMapItens[fonte.conta.id] = [lancamentoItem: itens]
  }else {
    itens = newMapItens[fonte.conta.id].itens
    newMapItens[fonte.conta.id] << [lancamentoItem: itens]
  }
}
// atualizando o map de lancamento
newMapLancto[codigoLancamento] << [
  contasAbertura : newMapItens
]
```

Este bloco busca os dados do balancete dinâmico, filtra as contas a serem encerradas e gera os itens de lançamento contábil. Ele calcula o `valorLancamento` com base nos saldos das contas correntes e, para cada conta, cria um ou mais itens de lançamento (débito/crédito) de acordo com o roteiro contábil definido. A lógica trata tanto roteiros simples quanto múltiplos, garantindo a correta inversão de tipos de lançamento quando necessário.

### Configuração e Processamento de Contas Correntes

```groovy
//// buscando as configurações dos contas correntes
def newMapConfigComponente = EncerramentoUtil.getConfigContaCorrenteComponente(entidade,exercicio)
def newMapConfig = EncerramentoUtil.getConfigContaCorrente(entidade,exercicio)

fonteBalancete = Dados.contabilidade.v1.balanceteDinamicoContaCorrente
fonteBalancete = fonteBalancete.busca(campos: "conta(id, mascara, mascaraFormatada), contasCorrentes(contaCorrente(descricao, componentes(posicao, propriedade, valor), lote),saldoAtual)" , criterio : criterioFonte, parametros : param , ordenacao : "conta.mascara asc");
def countContaCorrente = 0
for(fonte in fonteBalancete){
  def idContaEncerrada = fonte.conta.id
  def mapContaCorrente = [:] // mapa dos contas correntes
  for(cc in fonte.contasCorrentes) {
    if(cc.saldoAtual.abs() == 0.00){ continue } // se o conta corrente for zero não gera
    def idConfiguracao = newMapConfig[[lote: cc.contaCorrente.lote, descricao: cc.contaCorrente.descricao]]?.idConfiguracao ?: null // buscando a configuração do conta corrente
    def componentes = []
    for (comp in cc.contaCorrente.componentes.sort { it.posicao }) { // formando os dados do conta corrente
      componentes << [
        codigo: newMapConfigComponente[[lote: cc.contaCorrente.lote, descricao: cc.contaCorrente.descricao, componente: comp.propriedade]]?.idComponente ?: null,
        valor : comp.valor
      ]
    }
    tipoLancto = ((cc.saldoAtual > 0) ? "C" : "D")
    if(tipoLancto == 'C'){continue}
    roteiro = roterioContabil(fonte.conta.mascara)
    isMultiploRoteiro = roteiro.size() > 1 ? true : false
    //sempre teremos dois pares para esta fase, por isso vamos trabalhar com o indice do par para saber o momento de inverter o saldo.
    //        inverter = 0
    for(insert in newMapLancto[codigoLancamento]?.contasAbertura[idContaEncerrada]?.lancamentoItem){
      //            inverter++ // inverter tipo lancameto 1 = Saldo normal do lancamento / 2 = inverter o saldo
      if(isMultiploRoteiro){
        tipoLancto = (insert.codigoConta == fonte.conta.id) ? tipoLancto : ((roteiro.find{it.idConta == insert.codigoConta}.saldoInvertido == true) ? tipoLancto : EncerramentoUtil.inverteTipoLancto(tipoLancto))
      }else{
        tipoLancto = (insert.codigoConta == fonte.conta.id) ? tipoLancto : EncerramentoUtil.inverteTipoLancto(tipoLancto)
      }
      if(insert.lanctoItemContaCorrente[idConfiguracao]){
        countContaCorrente++
          list = insert.lanctoItemContaCorrente[idConfiguracao].contaCorrente
        list << [
          codigo          : countContaCorrente,
          idConfiguracao  : idConfiguracao,
          tipo            : tipoLancto,
          valor           : BigDecimal.valueOf(cc.saldoAtual.abs()),
          componentes : componentes
        ]
        insert.lanctoItemContaCorrente[idConfiguracao] << [ contaCorrente : list ]
      }else{
        countContaCorrente++
          list = []
        list << [
          codigo          : countContaCorrente,
          idConfiguracao  : idConfiguracao,
          tipo            : tipoLancto,
          valor           : BigDecimal.valueOf(cc.saldoAtual.abs()),
          componentes : componentes
        ]
        insert.lanctoItemContaCorrente[idConfiguracao] = [ contaCorrente : list ]
      }
    }
  }
}
```

Este bloco busca as configurações de contas correntes e seus componentes, e então processa os dados do balancete novamente para associar as contas correntes aos itens de lançamento. Ele garante que os saldos das contas correntes sejam corretamente atribuídos aos lançamentos, considerando o tipo de lançamento (débito/crédito) e a inversão de saldos quando aplicável.

### Geração de Arquivos CSV e Metadados

```groovy
metadados = []
arrLancamento = []
// escrevendo arquivo de lançamento
for(lancamento in newMapLancto){
  arrLancamento << [
    codigoLancamento: lancamento.value.codigoLancamento,
    historico: lancamento.value.historico
  ]
}

def countArqLancto = arrLancamento.collate(1000).size() // quantos arquivos de itens teremos
def countRegArqLancto = arrLancamento.size()
count = 0
for(lancto in arrLancamento.collate(1000)){
  count++ // contador de arquivos lancamento
    arqLancto = ArquivoUtil.arquivoLancamento(ArquivoUtil.lancamentoArquivoNome(),count) // criando o arquivo de lancamento
  metadados << [ arquivo : arqLancto.nome, tipo : "LANCAMENTOS"] // alimentando o array de metadados
  ArquivoUtil.cabecalhoLancamento(arqLancto.arquivo) // escrevendo o cabeçalho do arquivos de lancamento
  for(i in lancto) { 
    LancamentosContabeis.historico = i.historico
    // imprimir i // escrevendo o arquivo lancamento - Historico do Lancamento
    ArquivoUtil.escreverArquivo([
      elementos : i ,
      arquivo: arqLancto.arquivo
    ])
  }
  // a cada interação de 1000 registro retorno um arquivo para dentro do zip
  Resultado.arquivo(arqLancto.arquivo)
}


// escrevendo arquivo de itens do lancamento
def arrLancamentoItens = [] // variavel que irá armazenar os registros todos de itens para lancamento a serem gerados.
// interação dentro do map para armazenar os itens que farão parte do meu arquivo
for(lancamento in newMapLancto) {
  for (lanctoItem in lancamento.value.contasAbertura) {
    for(item in lanctoItem.value.lancamentoItem){
      arrLancamentoItens << [
        codigoItem      : item.codigoItem,
        codigoLancto    : item.codigoLancto,
        tipo            : item.tipo,
        valor           : Numeros.arredonda(item.valor, 2),
        par             : item.par,
        codigoConta     : item.codigoConta
      ]
    }
  }
}

mapaCodigoConta = [:]
// TODO : porque guardar e depois interar sobre os dados ?  porque com os dados dentro do array eu consigo configirar com funçõe nativas do groovy para gerenciar o limit de 1000 registros por arquivo, fica mais fácil controlar isso
// interar com o array para geração dos arquivos
def countArqItens = arrLancamentoItens.collate(1000).size() // quantos arquivos de itens teremos
def countRegArqItens = arrLancamentoItens.size()
count = 0 // contador de registro do arquivo
for(itensArq in arrLancamentoItens.collate(1000)){
  // criação do arquivo item
  count++
    arqItem = ArquivoUtil.arquivoItem(ArquivoUtil.itensArquivoNome(),count) // criando o arquivo de lancamento
  ArquivoUtil.cabecalhoItens(arqItem.arquivo) // escrevendo o cabeçalho do arquivos de itens
  metadados << [ arquivo : arqItem.nome, tipo : "ITENS"] // alimentando o array de metadados
  for(item in itensArq) { //valor total dos lancamentos itens1.csv
    chave = item.tipo
    if(!mapaCodigoConta[chave]){
      mapaCodigoConta[chave]=[codigoConta:item.codigoConta]
    }
    ArquivoUtil.escreverArquivo([
      elementos : item,
      arquivo : arqItem.arquivo
    ])
  }
  // a cada interação de 1000 registro retorno um arquivo para dentro do zip
  Resultado.arquivo(arqItem.arquivo)
}


//escrevendo arquivo de contas correntes
arrContaCorrente = []
for(lancamento in newMapLancto) {
  for (lanctoItem in lancamento.value.contasAbertura) {
    for (item in lanctoItem.value.lancamentoItem) {
      for(itemContaCorrente in item.lanctoItemContaCorrente) {
        for(contaCorrente in itemContaCorrente.value.contaCorrente){
          arrContaCorrente << [
            codigo : contaCorrente.codigo,
            codigoItem : item.codigoItem,
            codigoLancto: item.codigoLancto,
            idConfiguracao: contaCorrente.idConfiguracao,
            tipo : contaCorrente.tipo ,
            valor : contaCorrente.valor ,
            componentes : contaCorrente.componentes,
          ]
        }
      }
    }
  }
}


LancamentosContabeis.lancamentos = []
// interar com o array para geração dos arquivos
def countArqContaCorrente = arrContaCorrente.collate(1000).size() // quantos arquivos de itens teremos
def countRegArqContaCorrente = arrContaCorrente.size()
count = 0 // contador de registro do arquivo
for(contaCorrente in arrContaCorrente.sort{it.codigo}.collate(1000)){
  // criação do arquivo conta corrente
  count++
    arqContaCorrente = ArquivoUtil.arquivoContaCorrente(ArquivoUtil.contasCorrentesArquivoNome(),count) // criando o arquivo de conta corrente
  ArquivoUtil.cabecalhoContasCorrentes(arqContaCorrente.arquivo) // escrevendo o cabeçalho do arquivos de contas correntes
  metadados << [ arquivo : arqContaCorrente.nome, tipo : "CONTAS_CORRENTES"] // alimentando o array de metadados
  for(item in contaCorrente) {//aqui há os lancamentos
    LancamentosContabeis.lancamentos << item
    ArquivoUtil.escreverArquivo([
      elementos : item,
      arquivo : arqContaCorrente.arquivo
    ])
  }
  // a cada interação de 1000 registro retorno um arquivo para dentro do zip
  Resultado.arquivo(arqContaCorrente.arquivo)
}



// ESCRITA DO ARQUIVO METADADOS.json
// se a quantidade de arquivos itens for igual a zero, quer dizer que o lancamento não possui contas para lançar, com isso o metadado tem que vir vazio.
if(countArqItens > 0){
  Resultado.arquivo(arqLancto.arquivo)
}else{
  countArqLancto = 0
  metadados = []
}

def ARRAY_ARQUIVOS = []
for(i in metadados) ARRAY_ARQUIVOS.add(["arquivo" : i.arquivo,"tipo" : i.tipo]);

def ARRAY_JSON = [
  "versao" : 1,
  "arquivos" : ARRAY_ARQUIVOS,
  "quantidadeArquivos" : (countArqContaCorrente + countArqItens + countArqLancto)
]

ArquivoUtil.escreverArquivo(
  elementos : JSON.escrever(ARRAY_JSON),
  arquivo : ArquivoUtil.arquivoMetadados()
)

Resultado.arquivo(ArquivoUtil.arquivoMetadados())
```

## Código Completo

```groovy
// Script feito como solução para o chamado BTHSC-149602
// Visa integrar as movimentações do almoxarifado e integra-las ao contabil de forma automatica usando lançamentos mensais.

EncerramentoUtil = importar 'bth.contabil.utilitarios.encerramento.inicio'
ArquivoUtil =  importar 'bth.contabil.encerramentoinicio.gerar.arquivo'

def entidade = parametros.entidade.selecionado?.valor
def exercicio = parametros.pDataLanc.valor.formatar('yyyy');
def protocolo = contextoExecucao.idProtocolo
//def idFase = parametros.idFase.valor
def dataLanc = parametros.pDataLanc.valor.formatar('yyyy-MM-dd');
def dataInicial = (exercicio+"-01-01");
def dataFinal = (exercicio+"-01-01");
def idPlanoContas = EncerramentoUtil.getPlanoContas(entidade,exercicio)
def newMapLancto = [:]

def mapContraPartidas = [:] // mapa que irá armazenar os dados das contas que receberão saldo (id,mascara,descrição..)
def final codigoLancamento = 1
def final mascarasEncerradas = ["8211101"] 
def final mascaraContraPartidaAnalitica = ["8211102000000000000"]
def final historicoLancamento = "Início de exercício: Transferência das disponibilidades por destinação de recursos do exercício para exercícios anteriores."
def LancamentosContabeis = [:]
// CONFIGURAÇÃO DA FASE DE ENCERRAMENTO
imprimir "Entidade : ".concat(String.valueOf(entidade)) // subtituir pelo parametro entidade
imprimir "Exercício : ".concat(String.valueOf(exercicio)) // subtituir pelo parametro exercicio
imprimir "idPlanoContas : ".concat(String.valueOf(idPlanoContas))
imprimir "Data Lanc : ".concat(String.valueOf(dataLanc))

// DADOS DO LANCAMENTO
newMapLancto[codigoLancamento] = [
  codigoLancamento : codigoLancamento ,
  historico : historicoLancamento
]

// função que recebe o roteiro contabil do encerramento a ser feito...
def roterioContabil = { roteiro ->
  mascRetorno = ""
  switch(roteiro) {
    case {it.expressao(/^8211101/).encontrouPadrao()} : mascRetorno = mapContraPartidas["8211102000000000000"].dadosConta ; break ;
    default: "" ;
  }
  //    imprimir "$roteiro  >> ".concat(String.valueOf(mascRetorno[0]))
  return mascRetorno
}


if(mascaraContraPartidaAnalitica.size() > 0) {
  def criterioConta = "configuracao.id = $idPlanoContas"
  criterioConta += " and mascara in ("
  isBoolean = false
  for(i = 0; i < mascaraContraPartidaAnalitica.size(); i++){
    criterioConta += "'${mascaraContraPartidaAnalitica[i]}'";
    if(i != (mascaraContraPartidaAnalitica.size() -1) ){ criterioConta += ","}
  }
  criterioConta += ")"
  def fonteConta = Dados.contabilidade.v1.contaContabil
  fonteConta = fonteConta.busca(campos: "mascara,id,mascaraFormatada" , criterio : criterioConta)
  for(conta in fonteConta){
    dadosConta = []
    dadosConta << [idConta : conta.id, mascara : conta.mascara , mascaraFormatada : conta.mascaraFormatada]
    mapContraPartidas[conta.mascara] = [dadosConta : dadosConta]
  }
}else {
  if (mascarasEncerradas.size() > 0) {
    def criterioConta = "configuracao.id = $idPlanoContas and tipo = 'ANALITICO'"
    criterioConta += " and ("
    isBoolean = false
    for (i = 0; i < mascarasEncerradas.size(); i++) {
      criterioConta += "mascara like '${mascarasEncerradas[i]}%'"
      if (i != (mascarasEncerradas.size() - 1)) {
        criterioConta += " or "
      }
    }
    criterioConta += ")"
    def fonteConta = Dados.contabilidade.v1.contaContabil
    fonteConta = fonteConta.busca(campos: "mascara,id,mascaraFormatada", criterio: criterioConta)
    for (conta in fonteConta) {
      dadosConta = []
      dadosConta << [idConta: conta.id, mascara: conta.mascara, mascaraFormatada: conta.mascaraFormatada]
      mapContraPartidas[conta.mascara] = [dadosConta: dadosConta]
    }
  }
}

def fonteBalancete = Dados.contabilidade.v1.balanceteDinamicoContaCorrenteComSaldo
def param = [
  exercicio : exercicio ,
  entidadeId : entidade ,
  configuracaoPlanoContasId : idPlanoContas,
  dataInicial : dataInicial,
  dataFinal :  dataFinal
]

def criterioFonte = "conta.tipo = 'A' and identificacao.tipo = 'I'"

if(mascarasEncerradas.size() > 0){
  criterioFonte += " and ("
  isBoolean = false
  for(i = 0; i < mascarasEncerradas.size(); i++){
    criterioFonte += "conta.mascara like '${mascarasEncerradas[i]}*'"
    if(i != (mascarasEncerradas.size() -1) ){ criterioFonte += " or "}
  }
  criterioFonte += ")"
}
//imprimir criterioFonte

fonteBalancete = fonteBalancete.busca(campos: "conta(id, mascara, mascaraFormatada), contasCorrentes(contaCorrente(descricao, componentes(posicao, propriedade, valor), lote),saldoAtual),saldoAtual" , criterio : criterioFonte, parametros : param , ordenacao : "conta.mascara asc");
def countPar = 0
def countItem = 0
def newMapItens = [:]
for(fonte in fonteBalancete){
  //    countPar++
  //    countItem++
  //    countDe = countItem
  //    countPara = countItem
  valorLancamento = BigDecimal.valueOf(fonte.contasCorrentes.findAll { it.contaCorrente?.lote == 'Gerencial' && it.saldoAtual < 0}.sum { it.saldoAtual }?:0.00)
  if( valorLancamento == 0.00) continue ;
  def roteiro = roterioContabil(fonte.conta.mascara)
  def itens = []
  isMultiploRoteiro = roteiro.size() > 1 ? true : false
  if(isMultiploRoteiro){ // em um roteiro normal temos sempre um par de laçamento sendo feito, porem existem cenários em que podemos ter mais de um duas contas fazendo parte do mesmo 'par' do lançamento
    itens = []
    countPar++ // incrementando o par do lançamento
      
      tipoLancto =  ((valorLancamento > 0) ? "C" : "D")
    // fazendo o lancamento de encerramento da conta que realmente deve ser encerrada
    countItem++
      
      itens << [
        codigoLancto   : codigoLancamento,
        codigoItem     : countItem,
        par            : countPar,
        codigoConta    : fonte.conta.id,
        mascara        : fonte.conta.mascaraFormatada,
        tipo           : tipoLancto,
        valor          : valorLancamento.abs(),
        lanctoItemContaCorrente : [:]
      ]
    // agora vamos fazer um laço de repetição para o multiplo roteiro contabil conforme já foi configurado na
    for(i in 0..(roteiro.size()-1)){
      countItem++
        itens << [
          codigoLancto   : codigoLancamento,
          codigoItem     : countItem,
          par            : countPar,
          codigoConta    : roteiro[i]?.idConta ,
          mascara        : roteiro[i]?.mascaraFormatada,
          tipo           : (roteiro[i]?.saldoInvertido == true) ? EncerramentoUtil.inverteTipoLancto(tipoLancto) : tipoLancto,
          valor          : valorLancamento.abs(),
          lanctoItemContaCorrente : [:]
        ]
    }
  }else{ // em um roteiro normal temos sempre um par de laçamento sendo feito
    
    itens = []
    countPar++ // incrementando o par do lançamento
      for(i in 1..2) {
        countItem++ // incrementando o item do lançamento
          
          tipoLancto =  ((valorLancamento > 0) ? "C" : "D")
        itens << [
          codigoLancto   : codigoLancamento,
          codigoItem     : countItem,
          par            : countPar,
          codigoConta    : (i == 1) ? fonte.conta.id : roteiro[0]?.idConta ,
          mascara        : (i == 1 ) ? fonte.conta.mascaraFormatada : roteiro[0]?.mascaraFormatada,
          tipo           : (i == 1) ? tipoLancto : EncerramentoUtil.inverteTipoLancto(tipoLancto),
          valor          : valorLancamento.abs(),
          lanctoItemContaCorrente : [:]
        ]
      }
  }
  
  if(!newMapItens[fonte.conta.id]) {
    newMapItens[fonte.conta.id] = [lancamentoItem: itens]
  }else {
    itens = newMapItens[fonte.conta.id].itens
    newMapItens[fonte.conta.id] << [lancamentoItem: itens]
  }
}
// atualizando o map de lancamento
newMapLancto[codigoLancamento] << [
  contasAbertura : newMapItens
]

//// buscando as configurações dos contas correntes
def newMapConfigComponente = EncerramentoUtil.getConfigContaCorrenteComponente(entidade,exercicio)
def newMapConfig = EncerramentoUtil.getConfigContaCorrente(entidade,exercicio)

fonteBalancete = Dados.contabilidade.v1.balanceteDinamicoContaCorrente
fonteBalancete = fonteBalancete.busca(campos: "conta(id, mascara, mascaraFormatada), contasCorrentes(contaCorrente(descricao, componentes(posicao, propriedade, valor), lote),saldoAtual)" , criterio : criterioFonte, parametros : param , ordenacao : "conta.mascara asc");
def countContaCorrente = 0
for(fonte in fonteBalancete){
  def idContaEncerrada = fonte.conta.id
  def mapContaCorrente = [:] // mapa dos contas correntes
  for(cc in fonte.contasCorrentes) {
    if(cc.saldoAtual.abs() == 0.00){ continue } // se o conta corrente for zero não gera
    def idConfiguracao = newMapConfig[[lote: cc.contaCorrente.lote, descricao: cc.contaCorrente.descricao]]?.idConfiguracao ?: null // buscando a configuração do conta corrente
    def componentes = []
    for (comp in cc.contaCorrente.componentes.sort { it.posicao }) { // formando os dados do conta corrente
      componentes << [
        codigo: newMapConfigComponente[[lote: cc.contaCorrente.lote, descricao: cc.contaCorrente.descricao, componente: comp.propriedade]]?.idComponente ?: null,
        valor : comp.valor
      ]
    }
    tipoLancto = ((cc.saldoAtual > 0) ? "C" : "D")
    if(tipoLancto == 'C'){continue}
    roteiro = roterioContabil(fonte.conta.mascara)
    isMultiploRoteiro = roteiro.size() > 1 ? true : false
    //sempre teremos dois pares para esta fase, por isso vamos trabalhar com o indice do par para saber o momento de inverter o saldo.
    //        inverter = 0
    for(insert in newMapLancto[codigoLancamento]?.contasAbertura[idContaEncerrada]?.lancamentoItem){
      //            inverter++ // inverter tipo lancameto 1 = Saldo normal do lancamento / 2 = inverter o saldo
      if(isMultiploRoteiro){
        tipoLancto = (insert.codigoConta == fonte.conta.id) ? tipoLancto : ((roteiro.find{it.idConta == insert.codigoConta}.saldoInvertido == true) ? tipoLancto : EncerramentoUtil.inverteTipoLancto(tipoLancto))
      }else{
        tipoLancto = (insert.codigoConta == fonte.conta.id) ? tipoLancto : EncerramentoUtil.inverteTipoLancto(tipoLancto)
      }
      if(insert.lanctoItemContaCorrente[idConfiguracao]){
        countContaCorrente++
          list = insert.lanctoItemContaCorrente[idConfiguracao].contaCorrente
        list << [
          codigo          : countContaCorrente,
          idConfiguracao  : idConfiguracao,
          tipo            : tipoLancto,
          valor           : BigDecimal.valueOf(cc.saldoAtual.abs()),
          componentes : componentes
        ]
        insert.lanctoItemContaCorrente[idConfiguracao] << [ contaCorrente : list ]
      }else{
        countContaCorrente++
          list = []
        list << [
          codigo          : countContaCorrente,
          idConfiguracao  : idConfiguracao,
          tipo            : tipoLancto,
          valor           : BigDecimal.valueOf(cc.saldoAtual.abs()),
          componentes : componentes
        ]
        insert.lanctoItemContaCorrente[idConfiguracao] = [ contaCorrente : list ]
      }
    }
  }
}


metadados = []
arrLancamento = []
// escrevendo arquivo de lançamento
for(lancamento in newMapLancto){
  arrLancamento << [
    codigoLancamento: lancamento.value.codigoLancamento,
    historico: lancamento.value.historico
  ]
}

def countArqLancto = arrLancamento.collate(1000).size() // quantos arquivos de itens teremos
def countRegArqLancto = arrLancamento.size()
count = 0
for(lancto in arrLancamento.collate(1000)){
  count++ // contador de arquivos lancamento
    arqLancto = ArquivoUtil.arquivoLancamento(ArquivoUtil.lancamentoArquivoNome(),count) // criando o arquivo de lancamento
  metadados << [ arquivo : arqLancto.nome, tipo : "LANCAMENTOS"] // alimentando o array de metadados
  ArquivoUtil.cabecalhoLancamento(arqLancto.arquivo) // escrevendo o cabeçalho do arquivos de lancamento
  for(i in lancto) { 
    LancamentosContabeis.historico = i.historico
    // imprimir i // escrevendo o arquivo lancamento - Historico do Lancamento
    ArquivoUtil.escreverArquivo([
      elementos : i ,
      arquivo: arqLancto.arquivo
    ])
  }
  // a cada interação de 1000 registro retorno um arquivo para dentro do zip
  Resultado.arquivo(arqLancto.arquivo)
}


// escrevendo arquivo de itens do lancamento
def arrLancamentoItens = [] // variavel que irá armazenar os registros todos de itens para lancamento a serem gerados.
// interação dentro do map para armazenar os itens que farão parte do meu arquivo
for(lancamento in newMapLancto) {
  for (lanctoItem in lancamento.value.contasAbertura) {
    for(item in lanctoItem.value.lancamentoItem){
      arrLancamentoItens << [
        codigoItem      : item.codigoItem,
        codigoLancto    : item.codigoLancto,
        tipo            : item.tipo,
        valor           : Numeros.arredonda(item.valor, 2),
        par             : item.par,
        codigoConta     : item.codigoConta
      ]
    }
  }
}

mapaCodigoConta = [:]
// TODO : porque guardar e depois interar sobre os dados ?  porque com os dados dentro do array eu consigo configirar com funçõe nativas do groovy para gerenciar o limit de 1000 registros por arquivo, fica mais fácil controlar isso
// interar com o array para geração dos arquivos
def countArqItens = arrLancamentoItens.collate(1000).size() // quantos arquivos de itens teremos
def countRegArqItens = arrLancamentoItens.size()
count = 0 // contador de registro do arquivo
for(itensArq in arrLancamentoItens.collate(1000)){
  // criação do arquivo item
  count++
    arqItem = ArquivoUtil.arquivoItem(ArquivoUtil.itensArquivoNome(),count) // criando o arquivo de lancamento
  ArquivoUtil.cabecalhoItens(arqItem.arquivo) // escrevendo o cabeçalho do arquivos de itens
  metadados << [ arquivo : arqItem.nome, tipo : "ITENS"] // alimentando o array de metadados
  for(item in itensArq) { //valor total dos lancamentos itens1.csv
    chave = item.tipo
    if(!mapaCodigoConta[chave]){
      mapaCodigoConta[chave]=[codigoConta:item.codigoConta]
    }
    ArquivoUtil.escreverArquivo([
      elementos : item,
      arquivo : arqItem.arquivo
    ])
  }
  // a cada interação de 1000 registro retorno um arquivo para dentro do zip
  Resultado.arquivo(arqItem.arquivo)
}


//escrevendo arquivo de contas correntes
arrContaCorrente = []
for(lancamento in newMapLancto) {
  for (lanctoItem in lancamento.value.contasAbertura) {
    for (item in lanctoItem.value.lancamentoItem) {
      for(itemContaCorrente in item.lanctoItemContaCorrente) {
        for(contaCorrente in itemContaCorrente.value.contaCorrente){
          arrContaCorrente << [
            codigo : contaCorrente.codigo,
            codigoItem : item.codigoItem,
            codigoLancto: item.codigoLancto,
            idConfiguracao: contaCorrente.idConfiguracao,
            tipo : contaCorrente.tipo ,
            valor : contaCorrente.valor ,
            componentes : contaCorrente.componentes,
          ]
        }
      }
    }
  }
}


LancamentosContabeis.lancamentos = []
// interar com o array para geração dos arquivos
def countArqContaCorrente = arrContaCorrente.collate(1000).size() // quantos arquivos de itens teremos
def countRegArqContaCorrente = arrContaCorrente.size()
count = 0 // contador de registro do arquivo
for(contaCorrente in arrContaCorrente.sort{it.codigo}.collate(1000)){
  // criação do arquivo conta corrente
  count++
    arqContaCorrente = ArquivoUtil.arquivoContaCorrente(ArquivoUtil.contasCorrentesArquivoNome(),count) // criando o arquivo de conta corrente
  ArquivoUtil.cabecalhoContasCorrentes(arqContaCorrente.arquivo) // escrevendo o cabeçalho do arquivos de contas correntes
  metadados << [ arquivo : arqContaCorrente.nome, tipo : "CONTAS_CORRENTES"] // alimentando o array de metadados
  for(item in contaCorrente) {//aqui há os lancamentos
    LancamentosContabeis.lancamentos << item
    ArquivoUtil.escreverArquivo([
      elementos : item,
      arquivo : arqContaCorrente.arquivo
    ])
  }
  // a cada interação de 1000 registro retorno um arquivo para dentro do zip
  Resultado.arquivo(arqContaCorrente.arquivo)
}



// ESCRITA DO ARQUIVO METADADOS.json
// se a quantidade de arquivos itens for igual a zero, quer dizer que o lancamento não possui contas para lançar, com isso o metadado tem que vir vazio.
if(countArqItens > 0){
  Resultado.arquivo(arqLancto.arquivo)
}else{
  countArqLancto = 0
  metadados = []
}

def ARRAY_ARQUIVOS = []
for(i in metadados) ARRAY_ARQUIVOS.add(["arquivo" : i.arquivo,"tipo" : i.tipo]);

def ARRAY_JSON = [
  "versao" : 1,
  "arquivos" : ARRAY_ARQUIVOS,
  "quantidadeArquivos" : (countArqContaCorrente + countArqItens + countArqLancto)
]

ArquivoUtil.escreverArquivo(
  elementos : JSON.escrever(ARRAY_JSON),
  arquivo : ArquivoUtil.arquivoMetadados()
)

Resultado.arquivo(ArquivoUtil.arquivoMetadados())
```



