# Certidão de divida ativa V2

Este documento descreve o script desenvolvido para a plataforma **Betha Sistemas** que monta a fonte dinâmica utilizada na emissão da **Certidão de Dívida Ativa (CDA)**, consolidando em uma única linha os dados cadastrais do devedor, o detalhamento das dívidas inscritas, o demonstrativo de débitos com acréscimos legais calculados em tempo real e os textos jurídicos variáveis por tipo de crédito.

## 📄 Descrição

A partir do documento de dívida informado por parâmetro (ID, tipo e ano), o script percorre as dívidas vinculadas, correlaciona cada uma delas entre os módulos de **Procuradoria** e **Tributos** e calcula juros, multa e correção monetária posição a posição. Em seguida, complementa a certidão com as informações do bem ou da atividade que originou o débito (imóvel ou econômico), com os dados do representante legal quando houver inventariante e com a relação de proprietários dos imóveis em dívida por IPTU.

Os parágrafos jurídicos e a natureza do crédito não são fixos no código: vêm da **tabela auxiliar 22**, o que permite adequar o texto da certidão a cada crédito sem alterar o script.

## 🛠️ Requisitos e Contexto

* **Módulos:** Procuradoria (v1 e v2) e Tributos (v2).
* **Plataforma:** BFC-Script, com fonte dinâmica `Dados.dinamico.v2`.
* **Finalidade:** Alimentar o relatório de Certidão de Dívida Ativa com os dados do devedor, o demonstrativo de débitos e os textos legais.
* **Parâmetros de entrada:**
  * `idDocumento` — identificador do documento de dívida.
  * `tipoDocumento` — tipo do documento de dívida.
  * `anoDocumento` — ano do documento de dívida.
* **Pré-requisito:** tabela auxiliar de código **22** cadastrada no módulo de Tributos (leiaute na seção [Tabela auxiliar 22](#-tabela-auxiliar-22)).

---

## 🔍 Funcionalidades Principais

* **Cálculo de acréscimos em tempo real**: para cada dívida, localiza o registro correspondente em Tributos pelo `idUnico` e acumula juros, multa e correção através de `Dados.tributos.v2.acrescimos.dividas.calcula`.
* **Detalhamento da inscrição em dívida ativa**: monta a lista de dívidas com período, vencimento, data de inscrição, número da inscrição, livro e folha.
* **Textos jurídicos parametrizáveis**: busca parágrafos e natureza do crédito na tabela auxiliar 22, cruzando o crédito da dívida com a abreviatura da receita, e recorre a um cadastro genérico quando não há registro específico para a receita.
* **Identificação do referente**: conforme o tipo, traz quadra, lote e inscrição imobiliária (imóvel) ou a atividade principal (econômico), além do CPF/CNPJ do responsável.
* **Tratamento de espólio**: identifica o representante legal do contribuinte e preenche o campo de inventariante, inclusive no caso de representante não identificado.
* **Relação de proprietários**: lista nome, CPF/CNPJ e percentual de participação dos proprietários dos imóveis em dívida por IPTU.
* **Formatação de documentos**: aplica máscara de CPF (11 dígitos) e CNPJ (14 dígitos) nos campos do devedor, do responsável e dos proprietários.

---

## 🧩 Estrutura da Fonte Dinâmica

### Campos simples

| Campo | Tipo | Conteúdo |
|---|---|---|
| `idDocumento` / `tipoDocumento` / `anoDocumento` | caracter | Parâmetros de entrada, repetidos na linha |
| `idPessoa` | caracter | Identificador do contribuinte |
| `pessoaNomeContri` | caracter | Nome do contribuinte |
| `pessoaNomeFantasia` | caracter | Nome fantasia |
| `pessoaCpfCnpj` | caracter | CPF/CNPJ do contribuinte, já formatado |
| `responsavelNome` | caracter | Nome do responsável |
| `responsavelCpf` | caracter | CPF/CNPJ do responsável, já formatado |
| `referenteCodigo` | caracter | Código do imóvel ou do econômico |
| `referenteTipo` | caracter | `I` para imóvel, `E` para econômico |
| `referenteQuadra` / `referenteLote` / `referenteInscImob` | caracter | Preenchidos somente quando o referente é imóvel |
| `referenteAtividade` | caracter | Preenchido somente quando o referente é econômico |
| `referenteRua` / `referenteNumero` / `referenteBairro` / `referenteCidade` | caracter | Endereço do referente |
| `pessoaRua` / `pessoaNumero` / `pessoaBairro` / `pessoaCidade` | caracter | Endereço do contribuinte |
| `anosDivida` | caracter | Anos abrangidos pela dívida |
| `listaOrigem` | caracter | Créditos distintos do documento, em caixa alta, separados por vírgula |
| `texto` | caracter | Texto livre do documento de dívida |
| `valorTotal` | numero | Soma do campo `total` da lista de débitos |
| `paragrafo1` / `paragrafo2` | caracter | Textos jurídicos vindos da tabela auxiliar 22 |
| `naturezaCredito` | caracter | Natureza vinda da tabela auxiliar 22; assume `Tributária` quando não há cadastro |
| `inventariante` | caracter | Representante legal do contribuinte, quando houver |
| `dataCorrecaoMonetaria` | caracter | Data base da correção, no formato `dd 'de' MMMM 'de' yyyy` |

### Listas

**`dividas`** — uma entrada por dívida inscrita vinculada ao documento:

| Campo | Tipo | Conteúdo |
|---|---|---|
| `periodo` | caracter | Ano da dívida |
| `dtvencimento` | caracter | Vencimento (`dd/MM/yyyy`) |
| `dtInscricao` | caracter | Data da inscrição em dívida ativa (`dd/MM/yyyy`) |
| `inscricao` | caracter | Número da inscrição |
| `livro` / `folha` | caracter | Livro e folha do registro |

**`debitos`** — demonstrativo financeiro, uma entrada por dívida:

| Campo | Tipo | Conteúdo |
|---|---|---|
| `ano` | caracter | Ano da dívida |
| `credito` | caracter | Crédito tributário |
| `original` | numero | Valor original do tributo |
| `atual` | numero | Saldo atual |
| `correcao` / `juros` / `multa` | numero | Acréscimos calculados |
| `total` | numero | `correção + juros + multa + valor do tributo` |

**`propImoveis`** — proprietários dos imóveis em dívida por IPTU:

| Campo | Tipo | Conteúdo |
|---|---|---|
| `nome` | caracter | Nome e CPF/CNPJ do proprietário |
| `percentual` | caracter | Percentual de participação |

---

## 🔄 Fluxo de Execução

1. **Leitura dos parâmetros** `idDocumento`, `tipoDocumento` e `anoDocumento`.
2. **Busca do documento de dívida** em `Dados.procuradoria.v1.documentosDivida`, percorrendo cada dívida vinculada.
3. **Para cada dívida**:
   * monta a entrada da lista `dividas`;
   * localiza a dívida em `Dados.procuradoria.v2.dividas` pelo `idDivida`;
   * usa o `idUnico` para encontrar a dívida equivalente em `Dados.tributos.v2.dividas`;
   * calcula os acréscimos com `Dados.tributos.v2.acrescimos.dividas.calcula`, acumulando juros, multa e correção;
   * monta a entrada da lista `debitos` e guarda a abreviatura do crédito.
4. **Descrição e abreviatura das receitas**: `documentosDividaReceitas` fornece o nome do crédito e `Dados.procuradoria.v1.receitas` a abreviatura correspondente.
5. **Textos da certidão**: busca na tabela auxiliar 22 o registro que combine o crédito (`campo1`) com a abreviatura da receita (`campo5`); não havendo, usa o registro do crédito com `campo5` vazio.
6. **Dados do referente**: conforme `referenteTipo`, consulta imóveis ou econômicos para preencher quadra, lote, inscrição imobiliária ou atividade principal, além do CPF/CNPJ do responsável.
7. **Inventariante**: consulta o contribuinte pelo CPF/CNPJ e, havendo representante legal, monta a descrição com nome e documento.
8. **Proprietários**: filtra os itens do documento com crédito `IPTU` e referente do tipo imóvel e busca os proprietários desses imóveis.
9. **Montagem e retorno**: monta a linha, insere na fonte dinâmica e retorna a fonte.

---

## 🗂️ Tabela auxiliar 22

O script espera a tabela auxiliar de código **22** com o seguinte uso dos campos:

| Campo | Conteúdo esperado |
|---|---|
| `campo1` | Abreviatura do crédito da dívida (ex.: `IPTU`, `ISS`) |
| `campo2` | Primeiro parágrafo jurídico da certidão |
| `campo3` | Segundo parágrafo jurídico da certidão |
| `campo4` | Natureza do crédito |
| `campo5` | Abreviatura da receita; deixar **vazio** no registro genérico do crédito |

O registro com `campo5` vazio funciona como texto padrão: ele é utilizado quando nenhum registro específico da receita é encontrado.

---

## ⚠️ Pontos de Atenção

* **Proprietários de um único imóvel**: em `getProprietariosImov`, a busca de imóveis usa `primeiro: true`. Quando o documento reúne IPTU de mais de um imóvel, somente os proprietários do primeiro são listados. Para contemplar todos, a busca precisa percorrer os imóveis retornados em vez de tomar apenas o primeiro.
* **Referente sem tratamento**: quando `referenteTipo` não é `I` nem `E`, o bloco `else` fica vazio e os campos de quadra, lote, atividade, inscrição imobiliária e CPF do responsável permanecem nulos.
* **Natureza padrão**: sem registro na tabela auxiliar 22, a natureza assume `Tributária` e os parágrafos ficam em branco na certidão.
* **Comandos `imprimir`**: as saídas de depuração presentes no código ajudam na homologação e podem ser removidas na versão definitiva.
* **Função duplicada**: o script carrega sua própria `formatarCpfCnpj`. A mesma formatação está documentada de forma reutilizável em [`Funções/formatarCpfCnpj.md`](../../Fun%C3%A7%C3%B5es/formatarCpfCnpj.md).

---

## 🧠 Código Completo para Importação

```groovy
esquema = [
  idDocumento			: Esquema.caracter,
  tipoDocumento			: Esquema.caracter,
  anoDocumento			: Esquema.caracter,
  idPessoa 				: Esquema.caracter,
  pessoaNomeContri		: Esquema.caracter,
  pessoaNomeFantasia	: Esquema.caracter,
  pessoaCpfCnpj			: Esquema.caracter,
  responsavelNome		: Esquema.caracter,
  responsavelCpf		: Esquema.caracter,
  referenteCodigo		: Esquema.caracter,
  referenteTipo			: Esquema.caracter,
  referenteQuadra		: Esquema.caracter,
  referenteLote			: Esquema.caracter,
  referenteAtividade	: Esquema.caracter,
  referenteInscImob		: Esquema.caracter,
  referenteRua			: Esquema.caracter,
  referenteNumero		: Esquema.caracter,
  referenteBairro		: Esquema.caracter,
  referenteCidade		: Esquema.caracter,
  pessoaRua				: Esquema.caracter,
  pessoaNumero			: Esquema.caracter,
  pessoaBairro			: Esquema.caracter,
  pessoaCidade			: Esquema.caracter,
  anosDivida			: Esquema.caracter,
  listaOrigem			: Esquema.caracter,
  texto					: Esquema.caracter,
  valorTotal			: Esquema.numero,
  paragrafo1			: Esquema.caracter,
  paragrafo2			: Esquema.caracter,
  inventariante 		: Esquema.caracter,
  dataCorrecaoMonetaria	: Esquema.caracter,
  naturezaCredito		: Esquema.caracter,
  dividas				: Esquema.lista(
    Esquema.objeto([
      periodo     	: Esquema.caracter,
      dtvencimento  : Esquema.caracter,
      dtInscricao 	: Esquema.caracter,
      inscricao    	: Esquema.caracter, 
      livro			: Esquema.caracter,
      folha			: Esquema.caracter,
    ])
  ),
  debitos				: Esquema.lista(
    Esquema.objeto([
      ano     		: Esquema.caracter,
      credito  		: Esquema.caracter,
      original 		: Esquema.numero,
      atual    		: Esquema.numero, 
      correcao		: Esquema.numero, 
      juros			: Esquema.numero, 
      multa			: Esquema.numero, 
      total			: Esquema.numero, 
    ])
  ),
  propImoveis			: Esquema.lista(
    Esquema.objeto([
      nome     		: Esquema.caracter,
      percentual	: Esquema.caracter,
    ])),
  
]

fonte = Dados.dinamico.v2.novo(esquema);

idDocumento = parametros?.idDocumento?.valor
tipoDocumento = parametros?.tipoDocumento?.valor
anoDocumento = parametros?.anoDocumento?.valor

debitos = []
dividas = []
creditos = []
receitas = []
abreviaturaReceitas = []

dadosDocumentosDivida = Dados.procuradoria.v1.documentosDivida.buscar(parametros:["idDocumento":idDocumento,"tipoDocumento":tipoDocumento,"anoDocumento":anoDocumento])
percorrer (dadosDocumentosDivida) { itemDocumentosDividaReceitas ->
  imprimir "itemDocumentos: " + itemDocumentosDividaReceitas
  dividas << [
    periodo		: itemDocumentosDividaReceitas.dividaAno.toString(),
    dtvencimento: itemDocumentosDividaReceitas.dividaDtVcto.format("dd/MM/yyyy"),
    dtInscricao	: itemDocumentosDividaReceitas.dividaDtInsc.format("dd/MM/yyyy"),
    livro		: itemDocumentosDividaReceitas.dividaLivro.toString(),
    folha		: itemDocumentosDividaReceitas.dividaFolha.toString(),
    inscricao	: itemDocumentosDividaReceitas.dividaInscricao,
  ]
  
  dadosDividas = Dados.procuradoria.v2.dividas.buscar(criterio: "id = ${itemDocumentosDividaReceitas.idDivida}")
  
  percorrer (dadosDividas) { itemDividas ->
    
    vlrJuros = 0
    vlrMulta = 0
    vlrCorrecao = 0
    vlTotal = 0
    
    dadosDividasTributos = Dados.tributos.v2.dividas.busca(criterio: "codigo = '${itemDividas.idUnico}'")
    
    percorrer (dadosDividasTributos) { itemDividasTributos ->
      
      dadosAcrescimosDiv = Dados.tributos.v2.acrescimos.dividas.calcula(parametros:["dividas":itemDividasTributos.id])
      
      percorrer (dadosAcrescimosDiv) { itemAcresc ->
        imprimir "Juro: " + itemAcresc.juro
        vlrJuros += itemAcresc.juro;
        vlrMulta += itemAcresc.multa;
        vlrCorrecao += itemAcresc.correcao
        vlTotal += itemAcresc.total
      }
    }
  }
  
  debitos << [
    ano     	: itemDocumentosDividaReceitas.dividaAno.toString(),
    credito		: itemDocumentosDividaReceitas.dividaCredito.toString(),
    original	: itemDocumentosDividaReceitas.valorTributo.toBigDecimal(),
    atual		: itemDocumentosDividaReceitas.valorSaldo.toBigDecimal(),
    correcao 	: vlrCorrecao,
    juros    	: vlrJuros, 
    multa    	: vlrMulta, 
    total    	: vlrCorrecao + vlrJuros + vlrMulta + itemDocumentosDividaReceitas.valorTributo,
    
  ]
  
  creditos << itemDocumentosDividaReceitas.dividaAbreviaturaCredito
  
}

imprimir "Lista debitos: " + debitos

//Traz a descrição da receita
filtroDocumentosDividaReceitas = "tipoDocumento = '${tipoDocumento}' and anoDocumento = ${anoDocumento} and idDocumento = ${idDocumento}"
dadosDocumentosDividaReceitas = Dados.procuradoria.v1.documentosDividaReceitas.buscar(criterio: filtroDocumentosDividaReceitas)
percorrer (dadosDocumentosDividaReceitas) { itemDocumentosDividaReceitas ->
  imprimir itemDocumentosDividaReceitas
  receitas << itemDocumentosDividaReceitas.nomeCredito
}

//Traz a abreviatura da receita
filtroReceitas = "descricao in ('${receitas.unique().join("','")}')"
dadosReceitas = Dados.procuradoria.v1.receitas.buscar(criterio: filtroReceitas)
percorrer (dadosReceitas) { itemReceitas ->
  abreviaturaReceitas << itemReceitas.abreviatura
}

paragrafo1 = ""
paragrafo2 = ""
naturezaCredito = ""

filtroRegistros = "campo1 in ('${creditos.unique().join("','")}') and campo5 in ('${abreviaturaReceitas.unique().join("','")}')"
dadosRegistros = Dados.tributos.v2.tabelaAuxiliar.registros.busca(criterio: filtroRegistros,parametros:["codigoTabelaAuxiliar":22])
if ( dadosRegistros.size() != 0 ) {
  
  percorrer (dadosRegistros) { itemRegistros ->
    paragrafo1 = itemRegistros.campo2
    paragrafo2 = itemRegistros.campo3
    naturezaCredito = itemRegistros.campo4
  }
  
} else {
  
  filtroRegistroSemReceita = "campo1 in ('${creditos.unique().join("','")}')"
  dadosRegistrosSemReceita = Dados.tributos.v2.tabelaAuxiliar.registros.busca(criterio: filtroRegistroSemReceita,parametros:["codigoTabelaAuxiliar":22])
  percorrer (dadosRegistrosSemReceita) { itemRegistroSemReceita ->
    
    if ( itemRegistroSemReceita.campo5 == "" ) {
      paragrafo1 = itemRegistroSemReceita.campo2
      paragrafo2 = itemRegistroSemReceita.campo3
      naturezaCredito = itemRegistroSemReceita.campo4
    }
  }
}

registroGeral = dadosDocumentosDivida[0]

referenteQuadra		= null
referenteLote		= null
referenteAtividade	= null
referenteInscImob	= null
responsavelCpf 		= null

if ( registroGeral.referenteTipo == "I" ) {
  
  dadosImoveis = Dados.tributos.v2.imoveis.busca(criterio: "codigo = ${registroGeral.referenteCodigo}",primeiro:true)
  referenteQuadra		= (dadosImoveis?.quadra?:"").toString()
  referenteLote			= (dadosImoveis?.lote?:"").toString()
  referenteAtividade	= null
  referenteInscImob		= (dadosImoveis.inscricaoImobiliariaFormatada).toString()
  responsavelCpf		= dadosImoveis.responsavel.cpfCnpj
  
} else if ( registroGeral.referenteTipo == "E" ) {
  
  dadosEconomicos = Dados.tributos.v2.economicos.busca(criterio: "codigo = ${registroGeral.referenteCodigo}",primeiro:true)
  dadosAtividades = Dados.tributos.v2.economico.atividades.busca(criterio: "principal = 'SIM'",parametros:["idEconomico":dadosEconomicos.id],primeiro:true)
  dadosContribuinteEconomico = Dados.tributos.v2.contribuintes.busca(criterio: "id = ${dadosEconomicos.contribuinte.id}",primeiro:true)
  
  referenteQuadra		= null
  referenteLote			= null
  referenteAtividade	= dadosAtividades.descricaoPersonalizada
  referenteInscImob		= null
  responsavelCpf 		= dadosContribuinteEconomico.pessoaJuridica.responsavel.cpfCnpj
  
} else {
  
}

//Trazendo dados de inventariantes caso tenha.
inventariante = ""
dadosContribuintes = Dados.tributos.v2.contribuintes.busca(criterio: "cpfCnpj = '${registroGeral.pessoaCpfCnpj}'",primeiro:true)

if ( !(dadosContribuintes.pessoaFisica.tipoRepresentanteLegal.isEmpty() ) ) {
  
  if ( dadosContribuintes.pessoaFisica.tipoRepresentanteLegal.valor == 'NAO_IDENTIFICADO' ) {
    inventariante = "Não identificado"
  } else {
    inventariante = dadosContribuintes?.pessoaFisica?.tipoRepresentanteLegal?.descricao + " - " + dadosContribuintes?.pessoaFisica?.representanteLegal?.nome + " CPF: " + formatarCpfCnpj(dadosContribuintes?.pessoaFisica?.representanteLegal?.cpfCnpj)
  } 
}

// Trazendo dados dos proprietarios dos imoveis que estão em CDA pelo crédito de IPTU
propImoveis = []
imoveisIPTU = dadosDocumentosDivida.findAll{ it.dividaAbreviaturaCredito == 'IPTU' && it.referenteTipo == 'I' }.collect { it.referenteCodigo }
proprietariosImoveis = getProprietariosImov(imoveisIPTU)
proprietariosImoveis.each { item ->
  propImoveis << [
    nome     	: item.nome,
    percentual	: item.percentual,
  ]
}

linha = [
  idDocumento			: idDocumento.toString(),
  tipoDocumento			: tipoDocumento.toString(),
  anoDocumento			: anoDocumento.toString(),
  idPessoa				: registroGeral.idPessoa.toString(),
  pessoaNomeContri		: registroGeral.pessoaNome,
  pessoaNomeFantasia	: registroGeral.pessoaNomeFantasia,
  pessoaCpfCnpj			: formatarCpfCnpj(registroGeral.pessoaCpfCnpj),
  responsavelNome		: registroGeral.responsavelNome,
  responsavelCpf		: formatarCpfCnpj(responsavelCpf),
  referenteCodigo		: registroGeral.referenteCodigo.toString(),
  referenteTipo			: registroGeral.referenteTipo,
  referenteQuadra		: referenteQuadra,
  referenteLote			: referenteLote,
  referenteAtividade	: referenteAtividade,
  referenteInscImob		: referenteInscImob,
  referenteRua			: registroGeral.referenteRua.toString(),
  referenteNumero		: registroGeral.referenteNumero,
  referenteBairro		: registroGeral.referenteBairro,
  referenteCidade		: registroGeral.referenteCidade,
  pessoaRua				: registroGeral.pessoaRua.toString(),
  pessoaNumero			: registroGeral.pessoaNumero,
  pessoaBairro			: registroGeral.pessoaBairro,
  pessoaCidade			: registroGeral.pessoaCidade,
  anosDivida			: registroGeral.anosDivida,
  listaOrigem			: creditos.unique().join(", ").toString().toUpperCase(),
  texto					: registroGeral?.texto?:"",
  paragrafo1			: paragrafo1,
  paragrafo2			: paragrafo2,
  dataCorrecaoMonetaria	: registroGeral.dataBase.format("dd 'de' MMMM 'de' yyyy"),
  naturezaCredito		: (naturezaCredito != "") ? naturezaCredito : "Tributária",
  debitos				: debitos,
  dividas				: dividas,
  valorTotal			: debitos.findAll{it}.collect{it.total}.sum(),
  inventariante			: inventariante,
  propImoveis			: propImoveis,
]

imprimir linha

fonte.inserirLinha(linha)

retornar fonte

// Funções
def formatarCpfCnpj(campo){
  
  if ( campo == null ) {
    return ""
  }
  
  campoFormatado = "";
  switch(campo.tamanho()){
    case 11:
    mascara = ~/(\d{3})(\d{3})(\d{3})(\d{2})/
    campo.replaceAll(mascara){ documento, a, b, c, d ->
      campoFormatado = "${a}.${b}.${c}-${d}"
    }
    break
    case 14:
    mascara = ~/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/
    campo.replaceAll(mascara){ cnpj, a, b, c, d, e ->
      campoFormatado = "${a}.${b}.${c}/${d}-${e}"
    }
    break
    default:
      campoFormatado = campo
    break    
  }  
  return campoFormatado
}

def getProprietariosImov(codImovel) {
  
  if ( codImovel == [] ) {
    return
  }
  
  listProprietarios = []
  dadosImoveis = Dados.tributos.v2.imoveis.busca(criterio: "codigo in (${codImovel.join(",")})",campos: "id",primeiro:true)
  dadosProprietarios = Dados.tributos.v2.imovel.proprietarios.busca(parametros:["idImovel":dadosImoveis.id])
  percorrer (dadosProprietarios) { itemProprietarios ->
    imprimir itemProprietarios
    listProprietarios << [
      nome			: itemProprietarios.contribuinte.nome + ", CPF:" + formatarCpfCnpj(itemProprietarios.contribuinte.cpfCnpj),
      percentual	: "Percentual: "+itemProprietarios.percentual+"%",
    ]
  }
  
  return listProprietarios
}
```

---

> 📌 **O relatório completo está no sistema Procuradoria de Águas de Chapecó.**
