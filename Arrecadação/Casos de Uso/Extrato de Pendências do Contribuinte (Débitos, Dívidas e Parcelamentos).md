# Extrato Imóveis e Econômicos

Este documento descreve o script desenvolvido para a plataforma **Betha Sistemas** que monta a fonte dinâmica do extrato de pendências do contribuinte, reunindo em uma única lista de lançamentos os **débitos**, as **dívidas ativas** e as **parcelas de parcelamento**, com juros, multa e correção calculados na data de hoje e com os pagamentos já realizados abatidos.

## 📄 Descrição

A partir de um imóvel ou econômico informado por parâmetro, o script identifica o contribuinte responsável e levanta a situação fiscal completa dele nos três blocos do módulo de **Tributos**. Cada lançamento é devolvido com o crédito tributário, o vencimento, a situação, os valores originais, os acréscimos legais e o que já foi pago — tudo em uma lista única (`lancamentos`), diferenciada pelo campo `tipoLancamento`.

Quando nenhum dos três blocos possui lançamento em aberto, o campo `mensagemPendencias` retorna `Sem nenhuma pendência`, permitindo que o relatório imprima a mensagem em vez de um extrato vazio.

O cálculo dos acréscimos e a conversão dos enumeradores não são feitos no próprio script: ele importa os scripts auxiliares `enumerador`, `valores` e `acrescimos`, o que mantém a regra de cálculo centralizada e reaproveitável.

## 🛠️ Requisitos e Contexto

* **Módulo:** Tributos (v2).
* **Plataforma:** BFC-Script, com fonte dinâmica `Dados.dinamico.v2`.
* **Finalidade:** Alimentar relatórios de extrato, consulta de pendências e certidões de situação fiscal do contribuinte.
* **Scripts importados (obrigatórios):**
  * `enumerador` — fornece `esquema` e `converter()` para os campos enumerados (situação, vencido, única, executada/protestada).
  * `valores` — fornece `receitas()`, usado no rateio dos valores lançados por receita.
  * `acrescimos` — fornece `calcular(tipo, ids)` para débitos, dívidas e parcelamentos.

### Parâmetros de entrada

| Parâmetro | Valores | Efeito |
|---|---|---|
| `tipo` | `DEBITOS`, `DIVIDAS`, `PARCELAMENTOS` (um ou mais) | Define quais blocos serão pesquisados. Quando nenhum é informado, os três são pesquisados. |
| `tipoReferente` | `IMOVEL` ou `ECONOMICO` | Indica em qual cadastro o código do referente será localizado. |
| `referente` | Código do imóvel ou do econômico | Restringe a busca ao referente e define o contribuinte do extrato. Código inexistente interrompe a execução com mensagem. |
| `situacao` | Lista separada por vírgula | Filtra a situação dos lançamentos nos três blocos. |
| `ano` | `2024` ou intervalos como `2020-2023,2025` | Monta a expressão de filtro por ano; aceita anos avulsos e intervalos combinados. |
| `mostrarUnicaVencida` | `SIM` / demais valores | Quando diferente de `SIM`, oculta a cota única vencida e sem pagamento, evitando duplicidade com as parcelas. |

---

## 🔍 Funcionalidades Principais

* **Três origens em uma lista só**: débitos, dívidas ativas e parcelas de parcelamento alimentam a mesma lista `lancamentos`, diferenciadas por `tipoLancamento` (`DEBITO`, `DIVIDA_ATIVA`, `PARCELAMENTO`).
* **Acréscimos na data atual**: juros, multa e correção são calculados apenas para os lançamentos em aberto e vencidos, através do script `acrescimos`.
* **Abatimento por pagamento**: havendo pagamento detalhado, os valores do lançamento são recompostos a partir dos valores devidos, pagos, descontados e remidos do próprio pagamento.
* **Dívida parcelada**: quando a dívida está em parcelamento, os valores vêm das receitas do parcelamento e o campo `parcelamento` identifica número, ano e data.
* **Identificação do referente**: imóveis retornam endereço e inscrição imobiliária formatada; econômicos retornam endereço e a lista de atividades.
* **Filtro de anos por intervalo**: o parâmetro `ano` aceita combinações como `2019-2021,2024`, traduzidas para a expressão de filtro de cada bloco.
* **Mensagem de ausência de pendências**: sem lançamentos em aberto nos três blocos, o extrato retorna a mensagem no lugar da lista.

---

## 🧩 Estrutura da Fonte Dinâmica

### Campos do cabeçalho

| Campo | Tipo | Conteúdo |
|---|---|---|
| `mensagemPendencias` | caracter | `Sem nenhuma pendência` quando não há nada em aberto nos três blocos |
| `tipoReferente` | caracter | Tipo do referente |
| `referente` | inteiro | Referente pesquisado |
| `idContribuinteref` | caracter | Identificador do contribuinte vinculado ao referente |
| `contribuintes` | objeto | Código, nome, CPF/CNPJ, nome fantasia e endereço completo (logradouro, bairro, município e estado) |
| `contribuinte` | objeto | Código, nome, nome fantasia e CPF/CNPJ |
| `enderecoContrib` | caracter | Endereço do contribuinte já formatado pelo cadastro |
| `lancamentos` | lista | Lançamentos do extrato (detalhados abaixo) |

### Lista `lancamentos`

| Campo | Tipo | Conteúdo |
|---|---|---|
| `tipoLancamento` | enumerador | `DEBITO`, `DIVIDA_ATIVA` ou `PARCELAMENTO` |
| `creditoTributario` | objeto | Abreviatura e descrição do crédito (`N/A` nas parcelas) |
| `parcelamento` | caracter | Número, ano e data do parcelamento, quando a dívida está parcelada |
| `ano` | inteiro | Ano do lançamento |
| `nroParcela` | inteiro | Número da parcela |
| `unica` | enumerador | Indica cota única |
| `vencido` | enumerador | `SIM` quando o vencimento é anterior a hoje |
| `dtVencimento` | data | Vencimento do lançamento |
| `valorLancamento` | numero | Valor lançado, já líquido de desconto e benefício |
| `valor` | numero | Valor do tributo considerado no cálculo |
| `desconto` | numero | Descontos, benefícios, anistias e remissões |
| `correcao` / `juros` / `multa` | numero | Acréscimos legais |
| `total` | numero | Total do lançamento, líquido de desconto |
| `totalLancamento` | numero | Total por receita, somando os acréscimos |
| `situacao` | caracter | Situação resumida do lançamento |
| `status` | enumerador | Situação do lançamento (aberto, parcelada, quitada…) |
| `porDiferenca` | enumerador | Indica lançamento gerado por diferença de pagamento |
| `executadaProtestada` | enumerador | Nas dívidas, indica execução ou protesto |
| `dtPagamento` | data | Data da quitação |
| `valorPago` | numero | Valor efetivamente pago |
| `valorDiferenca` | numero | Diferença apurada no pagamento |
| `local` | caracter | Sigla do banco do pagamento |
| `referente` | caracter | Tipo e código do referente, ou o número do parcelamento |
| `referenteEndereco` | caracter | Endereço do imóvel/econômico; nas parcelas, os créditos que compõem o parcelamento |
| `referenteInformacoes` | caracter | Inscrição imobiliária ou atividades; nas parcelas, a configuração e a lei do parcelamento |

---

## 🔄 Fluxo de Execução

1. **Importações e parâmetros**: carrega `enumerador`, `valores` e `acrescimos` e lê os parâmetros, definindo quais blocos serão pesquisados.
2. **Referente**: localiza o imóvel ou o econômico pelo código, monta o critério (`idImovel` ou `idEconomico`) e guarda o identificador do contribuinte — responsável, no caso do imóvel; contribuinte, no caso do econômico. Código não encontrado interrompe a execução com `suspender`.
3. **Filtro de anos**: converte o parâmetro `ano` em expressão de critério, tratando anos avulsos e intervalos.
4. **Contribuinte**: busca o contribuinte e seu endereço formatado.
5. **Débitos**: busca os pagamentos detalhados do contribuinte e as receitas dos débitos conforme referente, situação e ano, acumulando os identificadores dos referentes.
6. **Dívidas**: mesmo levantamento para as dívidas ativas.
7. **Parcelamentos**: busca as parcelas e, a partir delas, as composições agrupadas de cada parcelamento.
8. **Referentes**: com os identificadores acumulados, busca imóveis (endereço e inscrição imobiliária) e econômicos (endereço e atividades).
9. **Montagem**: cada bloco agrupa as receitas por lançamento, calcula os acréscimos dos itens em aberto e vencidos, aplica os pagamentos quando existirem e insere o item em `lancamentos`.
10. **Fechamento**: define `mensagemPendencias`, monta a linha e retorna a fonte.

---

## 🧮 Regras de Cálculo

* **Acréscimos**: `acrescimos.calcular` é chamado apenas para os lançamentos em situação `ABERTO` e com vencimento anterior a hoje. Lançamentos quitados ou a vencer não recebem juros, multa e correção.
* **Pagamento no lugar do cálculo**: quando o lançamento tem pagamento detalhado, os valores são zerados e recompostos a partir do pagamento — somando os valores devidos (lançado, correção, juros e multa), os descontos concedidos e remidos, e os valores efetivamente pagos. O valor do pagamento prevalece sobre o acréscimo calculado.
* **Dívida parcelada**: quando existem receitas de parcelamento vinculadas à dívida, os valores de tributo, correção, juros, multa e desconto passam a vir dessas receitas, e `total` é recomposto como `valor + correção + juros + multa`.
* **Total líquido**: em débitos e dívidas, `total` é gravado já descontado (`total - desconto`).
* **Parcelas**: o total parte do acréscimo calculado ou de `vlParcela - vlDesconto`, somando taxa, juro de financiamento e correção prefixada.
* **Cota única**: com `mostrarUnicaVencida` diferente de `SIM`, a cota única vencida e sem pagamento é descartada do extrato.

---

## ⚠️ Pontos de Atenção

* **Variáveis declaradas dentro do laço do contribuinte**: `verificaDebitosAbertos`, `verificaDividasAbertas`, `verificaParcelamentosAbertos` e `retornoEndereco` são inicializadas dentro do primeiro `percorrer(contribuinte)`, mas consultadas depois, fora dele — na montagem dos blocos e na linha final. Se a busca do contribuinte não retornar nenhum registro, essas variáveis não terão sido criadas. Declará-las antes do laço evita a dependência.
* **Reaproveitamento da variável `referente`**: ela nasce como critério de busca em texto (`idImovel = 123`), e dentro dos laços de montagem passa a ser um mapa com `codigo` e `tipo`. Na linha final é gravada no campo `referente`, declarado no esquema como `Esquema.inteiro` — vale conferir o que chega ao relatório.
* **`contribuinte` é uma lista**: o retorno de `.collect { c -> c }` é uma coleção, mas no bloco `linha` os campos são lidos como `contribuinte.codigo`, `contribuinte.nome` e assim por diante. Como o esquema declara um objeto único, convém usar o primeiro elemento da lista.
* **`tipoReferente` sai sempre vazio**: a variável é inicializada com `""` e nunca recebe o valor do parâmetro.
* **Acumuladores sobre si mesmos**: `contribuintes << contribuintes` e `enderecoContrib << enderecoContrib` adicionam a própria estrutura dentro dela mesma. O campo que efetivamente chega ao relatório é `enderecoFormatado`.
* **Busca de endereço duplicada**: o endereço do contribuinte é consultado em três trechos distintos (`retornoEndereco`, `dadosEnderecos` e `enderecoContrib`). Apenas `enderecoFormatado` é usado na linha final.
* **Comandos `imprimir`**: as saídas de depuração espalhadas pelo script ajudam na homologação e podem ser removidas na versão definitiva.
* **Dependência dos scripts importados**: sem `enumerador`, `valores` e `acrescimos` publicados no ambiente, o script não executa.

---

## 🧠 Código Completo para Importação

```groovy
// Importações
enumerador = importar "enumerador";
valores = importar "valores";
acrescimos = importar "acrescimos";
mostrarUnicaVencida = parametros.mostrarUnicaVencida?.valor == 'SIM';


FonteTributos = Dados.tributos.v2;

esquema = [
  mensagemPendencias: Esquema.caracter,
  tipoReferente: Esquema.caracter,
  referente: Esquema.inteiro,
  idContribuinteref: Esquema.caracter,
  contribuintes : Esquema.objeto([
    codigo: Esquema.inteiro,
    nome: Esquema.caracter,
    cpfCnpj : Esquema.caracter,
    nomeFantasia: Esquema.caracter,
    endereco    : Esquema.objeto([
      complemento: Esquema.caracter,
      cep        : Esquema.caracter,
      numero     : Esquema.caracter,
      bairro     : Esquema.objeto([
        nome: Esquema.caracter
      ]),
      logradouro : Esquema.objeto([
        nome                   : Esquema.caracter,
        tipoLogradouroDescricao: Esquema.caracter
      ]),
      municipio  : Esquema.objeto([
        nome  : Esquema.caracter,
        estado: Esquema.objeto([
          uf: Esquema.caracter
        ])
      ])
    ])
  ]),
  contribuinte    : Esquema.objeto([
    codigo      : Esquema.inteiro,
    nome        : Esquema.caracter,
    nomeFantasia: Esquema.caracter,
    cpfCnpj     : Esquema.caracter
  ]),
  enderecoContrib    : Esquema.caracter,
  lancamentos       : Esquema.lista(Esquema.objeto([
    creditoTributario   : Esquema.objeto([
      abreviatura: Esquema.caracter,
      descricao  : Esquema.caracter
    ]),
    parcelamento        : Esquema.caracter,
    tipoLancamento      : enumerador.esquema,
    vencido             : enumerador.esquema,
    referente           : Esquema.caracter,
    ano                 : Esquema.inteiro,
    nroParcela          : Esquema.inteiro,
    unica               : enumerador.esquema,
    dtVencimento        : Esquema.data,
    valorLancamento     : Esquema.numero,
    valor               : Esquema.numero,
    desconto            : Esquema.numero,
    correcao            : Esquema.numero,
    juros               : Esquema.numero,
    multa               : Esquema.numero,
    total               : Esquema.numero,
    totalLancamento     : Esquema.numero,
    situacao            : Esquema.caracter,
    executadaProtestada : enumerador.esquema,
    status              : enumerador.esquema,
    porDiferenca        : enumerador.esquema,
    dtPagamento         : Esquema.data,
    valorPago           : Esquema.numero,
    valorDiferenca      : Esquema.numero,
    local               : Esquema.caracter,
    referenteEndereco   : Esquema.caracter,
    referenteInformacoes: Esquema.caracter
  ]))
];

fonte = Dados.dinamico.v2.novo(esquema);
FonteContribuintes = FonteTributos.contribuintes;
FonteDebitos = FonteTributos.debitos;
FonteDividas = FonteTributos.dividas;
FonteParcelamentos = FonteTributos.parcelamentos;
FontePagamentos = FonteTributos.pagamentos;


parametroSituacao = nulo;

se(parametros.situacao?.valor) {
  parametroSituacao = parametros.situacao?.valor.split(',').collect { item -> "'$item'" }.join(',');
}

BUSCA_DEBITOS = parametros.tipo.valor.posicao("DEBITOS", 0) > -1;
BUSCA_DIVIDAS = parametros.tipo.valor.posicao("DIVIDAS", 0) > -1;
BUSCA_PARCELAMENTOS = parametros.tipo.valor.posicao("PARCELAMENTOS", 0) > -1;

se(!BUSCA_DEBITOS && !BUSCA_DIVIDAS && !BUSCA_PARCELAMENTOS) {
  BUSCA_DEBITOS = true;
  BUSCA_DIVIDAS = true;
  BUSCA_PARCELAMENTOS = true;
}

tipoReferente = "";
referente = "";
idContribuinte = "";

imprimir referente

se(parametros.referente?.valor) {
  se(parametros.tipoReferente?.selecionado?.valor == 'IMOVEL') {
    ref = FonteTributos.imoveis.busca(
      criterio: "codigo = " + parametros.referente.valor, primeiro: true
    );
    se(ref.id) {
      referente = "idImovel = " + ref.id;
      idContribuinteref = ref.responsavel.id;
      imprimir "127: " + idContribuinteref
    }
  }
  se(parametros.tipoReferente?.selecionado?.valor == 'ECONOMICO') {
    ref = FonteTributos.economicos.busca(
      criterio: "codigo = " + parametros.referente.valor, primeiro: true
    );
    se(ref.id) {
      referente = "idEconomico = " + ref.id;
      idContribuinteref = ref.contribuinte.id;
    }
  }
  se(parametros.tipoReferente?.selecionado?.valor && referente.vazio()) {
    suspender "Não foi encontrado referente com o código informado."
  }
}

parametroAnos = nulo;
se (parametros.ano?.valor) {
  queryAnos = [];
  intervalos = (parametros.ano?.valor + '').split(',');
  intervalos.each { intervalo ->
    periodos = intervalo.split('-');
    anoInicial = periodos[0];
    anoFinal = nulo;
    if (periodos.length > 1) {
      anoFinal = periodos[1];
    }
    if (anoInicial && anoFinal) {
      queryAnos << "({ano} >= $anoInicial and {ano} <= $anoFinal)";
    } else if (anoInicial) {
      queryAnos << "{ano} = $anoInicial";
    }
  }
  parametroAnos = "(" + queryAnos.join(' or ') + ")";
}

// Contribuinte

lancamentos = [];
acrescimo = [];
pagamento = [];
valor = [];
contribuintes = [];
enderecoFormatado = ''

imprimir "172: " + idContribuinteref

contribuinte = FonteContribuintes.busca(
  criterio: "id in ($idContribuinteref)"
).collect { c -> c };
  percorrer(contribuinte) { contribuinte ->
    verificaDebitosAbertos = 0;
    verificaDividasAbertas = 0;
    verificaParcelamentosAbertos = 0;
    retornoEndereco = FonteTributos.contribuinte.enderecos.busca(
      parametros: [idContribuinte: idContribuinteref],
      primeiro: true
    );
  }
percorrer(contribuinte) { contrib ->
  contribuintes = [ 
    codigo: contrib.codigo,
    nome: contrib.nome,
    cpfCnpj: contrib.cpfCnpj,
    nomeFantasia: contrib.nomeFantasia      
  ]
  contribuintes << contribuintes;
}


fonteContribuintes = Dados.tributos.v2.contribuintes;

filtroContribuintes = "id = ${idContribuinteref}"

dadosContribuintes = fonteContribuintes.busca(criterio: filtroContribuintes)

percorrer (dadosContribuintes) { itemContribuintes ->

  dadosEnderecos = Dados.tributos.v2.contribuinte.enderecos.busca(parametros: [idContribuinte: itemContribuintes.id]  )
  
  percorrer (dadosEnderecos) { itemEnderecos ->
    imprimir "aqui 204"
    enderecoFormatado = itemEnderecos.enderecoFormatado
  }
}

enderecoContrib = FonteTributos.contribuinte.enderecos.busca(parametros: [idContribuinte: idContribuinteref]);
percorrer(enderecoContrib) { endContrib ->
  enderecoContrib = [
    complemento: endContrib.complemento,
    cep: endContrib.cep,
    numero: endContrib.numero,
    bairro: endContrib.bairro.nome,
    logradouro: endContrib.logradouro.nome,
    municipio: endContrib.municipio.nome,
    tipoLogradouroDescricao: endContrib.logradouro.tipoLogradouroDescricao,
    estado: endContrib.municipio.estado.uf
  ]
  enderecoContrib << enderecoContrib;
}

// BUSCANDO DÉBITOS

referentes = [
  IMOVEIS           : [:],
  ECONOMICOS        : [:],
  RECEITAS_DIVERSAS : [:],
  NOTA_FISCAL_AVULSA: [:]
];

idsEconomicos = [];
idsImoveis = [];
idsReceitasDiversas = [];
idsNotasAvulsas = [];
filtroPagamentosDetalhados = [];
pagamentosDebitos = [];
pagamentosDividas = [];
pagamentosParcelamentos = [];


respostaReceitasDebitos = [];
se(BUSCA_DEBITOS) {
  pagamentosDebitos = FontePagamentos.detalhes.valores.busca(criterio: "debito.contribuinte.id in ($idContribuinteref)");
  imprimir "===== PAGAMENTOS DO DÉBITO ====="
  imprimir pagamentosDebitos
  criteriosDebito = [];
  se(!referente.vazio()) {
    criteriosDebito << "debito." + referente;
  }
  se(parametroSituacao) {
    criteriosDebito << "debito.situacao in ($parametroSituacao)";
  }
  se (parametroAnos) {
    criteriosDebito << Caracteres.substituir(parametroAnos, "{ano}", "debito.ano");
  }
  respostaReceitasDebitos = FonteDebitos.receitas.busca(
    criterio: criteriosDebito.join(' and '),
    ordenacao: "debito.ano asc"
  ).collect { receitaDebito -> receitaDebito };
    respostaReceitasDebitos.each { receitaDebito ->
      imprimir receitaDebito
      idsEconomicos << receitaDebito.debito.idEconomico;
      idsImoveis << receitaDebito.debito.idImovel;
      idsReceitasDiversas << receitaDebito.debito.idReceitaDiversa;
      idsNotasAvulsas << receitaDebito.debito.idNotaAvulsa;
    }
}


// BUSCANDO DÍVIDA

respostaReceitasDividas = [];
se(BUSCA_DIVIDAS) {
  pagamentosDividas= FontePagamentos.detalhes.valores.busca(criterio: "divida.contribuinte.id in ($idContribuinteref)");
  criteriosDivida = [];
  se(!referente.vazio()) {
    criteriosDivida << "divida." + referente;
  }
  se(parametroSituacao) {
    criteriosDivida << "divida.situacaoDivida in ($parametroSituacao)";
  }
  se (parametroAnos) {
    criteriosDivida << Caracteres.substituir(parametroAnos, "{ano}", "ano");
  }
  respostaReceitasDividas = FonteDividas.receitas.busca(
    criterio: criteriosDivida.join(' and '),
    ordenacao: "ano asc"
  ).collect { receitaDivida -> receitaDivida };
    respostaReceitasDividas.each { receitaDivida ->
      idsEconomicos << receitaDivida.divida.idEconomico;
      idsImoveis << receitaDivida.divida.idImovel;
      idsReceitasDiversas << receitaDivida.divida.idReceitaDiversa;
      idsNotasAvulsas << receitaDivida.divida.idNotaAvulsa;
    }
}


// BUSCANDO PARCELAMENTOS

respostaParcelamentos = [];
composicoes = [];
se(BUSCA_PARCELAMENTOS) {
  pagamentosParcelamentos= FontePagamentos.detalhes.valores.busca(criterio: "parcelamento.contribuinte.id in ($idContribuinteref)");
  criteriosParcelamento = [];
  se(!referente.vazio()) {
    criteriosParcelamento << "parcelamento." + referente;
  }
  se(parametroSituacao) {
    criteriosParcelamento << "situacao in ($parametroSituacao)";
  }
  se (parametroAnos) {
    wSituacao = [
      Caracteres.substituir(parametroAnos, "{ano}", "parcelamento.anoParcelamento"),
      Caracteres.substituir(parametroAnos, "{ano}", "parcelamento.anoLancamento")
    ].join(' or ');
    criteriosParcelamento << "($wSituacao)";
  }
  respostaParcelamentos = FonteParcelamentos.parcelas.busca(
    criterio: criteriosParcelamento.join(' and '),
  ).collect { parcelamento -> parcelamento };
    
    filtroComposicao = respostaParcelamentos.groupBy { parc -> parc.parcelamento.id }
  .collect { idParcelamento, itens -> idParcelamento }.join(',');
  se(filtroComposicao != nulo && !filtroComposicao.vazio) {
    composicoes = FonteParcelamentos.composicoes.agrupadas.busca(
      criterio: "parcelamento.id in ($filtroComposicao)"
    ).collect { comp -> comp };
      }
}

se(BUSCA_DEBITOS || BUSCA_DIVIDAS) {
  filtroImoveis = idsImoveis.unique().join(',');
  se(!Caracteres.vazio(filtroImoveis)) {
    FonteTributos.imoveis.busca(
      criterio: "id in ($filtroImoveis)"
    ).collect { imo -> imo }.each { imovel ->
      referentes["IMOVEIS"]['' + imovel.codigo] = [
        endereco   : imovel.enderecoFormatado,
        informacoes: imovel.inscricaoImobiliariaFormatada
      ]
    }
  }
  
  relEcoId = [:];
  filtroEconomicos = idsEconomicos.unique().join(',');
  se(!Caracteres.vazio(filtroEconomicos)) {
    atividades = FonteTributos.economicos.atividades.busca(
      criterio: "idEconomico in ($filtroEconomicos)"
    ).collect { atv -> atv };
      FonteTributos.economicos.busca(
        criterio: "id in ($filtroEconomicos)"
      ).collect { eco -> eco }.each { economico ->
        informacoes = atividades
        .findAll { t -> t.idEconomico == economico.id }
        .collect { t -> t.atividade.descricao }
        .join(', ');
        referentes["ECONOMICOS"]['' + economico.codigo] = [
          endereco   : economico.enderecoFormatado,
          informacoes: informacoes
        ];
      }
  }
}

pagamentosDetalhados = pagamentosDebitos + pagamentosDividas + pagamentosParcelamentos;

// Montagem débitos
se(BUSCA_DEBITOS) {
  debitos = respostaReceitasDebitos.groupBy { rec ->
    rec.debito.id
  };
    idsDebitos = debitos.findAll { idDebito, receitas ->
      debito = receitas[0].debito;
      return enumerador.converter(debito.situacao).valor == 'ABERTO' &&
        Datas.diferencaDias(debito.dtVencimento, Datas.hoje()) > 0
    }.collect { idDebito, itens -> idDebito };
      acrescimosDebito = acrescimos.calcular('debitos', idsDebitos);
  
  valoresDebito = valores.receitas(respostaReceitasDebitos, Datas.hoje());
  debitos.each { idDebito, receitas ->
    debito = receitas[0].debito;
    se(enumerador.converter(debito.situacao).valor == 'ABERTO' || enumerador.converter(debito.situacao).valor == 'PARCELADA') {
      verificaDebitosAbertos = 1;
    }
    vencido = Datas.diferencaDias(debito.dtVencimento, Datas.hoje()) > 0 ?
      [valor: "SIM", descricao: "Sim"] : [valor: "NAO", descricao: "Não"];
        referente = [
          codigo: debito.referente?.identificador,
          tipo  : enumerador.converter(debito.tipoCadastro)
        ];
    idsReceitas = receitas.collect { it.id };
      acrescimo = acrescimosDebito.findAll { it.id in idsReceitas };
        pagamento = pagamentosDetalhados.findAll { it.idDebito == debito.id }
    valor = valoresDebito.findAll { it.id in idsReceitas };
      infoReferente = referentes?."$referente.tipo.valor"?."$referente.codigo";
    total = acrescimo.sum { it.total } ?: debito.vlLancado;
    correcao = acrescimo.sum { it.correcao };
      juros = acrescimo.sum { it.juro };
        multa = acrescimo.sum { it.multa };
          desconto = debito.vlBeneficio + debito.vlDesconto;
    valorPago = 0;
    valorLancamento = 0;
    totalLancamento = 0;
    valor.each { val ->
      valorDesconto = val.vlBeneficio + val.vlDesconto;
      valorLancamento += val.vlLancado - valorDesconto;
      acr = acrescimo.find { it.id == val.id }
      totalLancamento += (acr?.total ?: val.vlLancado) - valorDesconto;
    }
    
    if (!mostrarUnicaVencida
        && vencido.valor == 'SIM'
        && enumerador.converter(debito.unica).valor == 'SIM'
        && pagamento.empty) {
      return;
    }
    
    se(!pagamento.empty) {
      pagamentosDetalhados
      total = 0;
      desconto = 0;
      valorPago = 0;
      correcao = 0;
      multa = 0;
      juros = 0;
      pagamento?.each { pg ->
        total += pg?.valorDevidoLancado +
          pg?.valorDevidoCorrecao +
          pg?.valorDevidoJuros +
          pg?.valorDevidoMulta;
        desconto += pg?.valorDescontoConcedidoCorrecao +
          pg?.valorDescontoConcedidoJuros +
          pg?.valorDescontoConcedidoLancado +
          pg?.valorDescontoConcedidoMulta +
          pg?.valorRemidoLancado +
          pg?.valorRemidoMulta +
          pg?.valorRemidoJuros +
          pg?.valorRemidoCorrecao;
        valorPago += pg?.valorPagoLancado +
          pg?.valorPagoCorrecao +
          pg?.valorPagoJuros +
          pg?.valorPagoMulta;
        correcao += pg?.valorDevidoCorrecao;
        multa += pg?.valorDevidoMulta;
        juros += pg?.valorDevidoJuros;
      }
    }
    lancamentos << [
      ano                 : debito.ano,
      creditoTributario   : [
        abreviatura: debito.abreviaturaCredito,
        descricao  : debito.descricaoCredito
      ],
      nroParcela          : debito.nroParcela,
      dtVencimento        : debito.dtVencimento,
      valorLancamento     : valorLancamento,
      valor               : acrescimo.sum { it.valor } ?: debito.vlLancado,
      desconto            : desconto ?: 0,
      correcao            : correcao ?: 0,
      juros               : juros ?: 0,
      multa               : multa ?: 0,
      totalLancamento     : totalLancamento,
      total               : total - desconto,
      situacao            : debito.situacaoResumida,
      status              : enumerador.converter(debito.situacao),
      porDiferenca        : enumerador.converter(debito.porDiferenca),
      unica               : enumerador.converter(debito.unica),
      dtPagamento         : debito.dtQuitacao,
      valorPago           : valorPago ?: 0,
      valorDiferenca      : debito.vlDiferencaPagamento,
      local               : debito.siglaBancoPagamento,
      tipoLancamento      : [valor: "DEBITO", descricao: "Débitos"],
      referente           : referente.tipo.descricao + " " + referente.codigo,
      referenteEndereco   : infoReferente?.endereco,
      referenteInformacoes: infoReferente?.informacoes,
      vencido             : vencido
    ];
  }
}

// Montagem dívidas
se(BUSCA_DIVIDAS) {
  dividas = respostaReceitasDividas.groupBy { rec ->
    rec.divida.id
  };
    idsDividas = dividas.findAll { idDivida, receitas ->
      divida = receitas[0].divida;
      return enumerador.converter(divida.situacaoDivida).valor == 'ABERTO' &&
        Datas.diferencaDias(divida.dataVencimento, Datas.hoje()) > 0
    }.collect { idDivida, itens -> idDivida };
      acrescimosDivida = acrescimos.calcular('dividas', idsDividas);
  
  idsDividasParcelas = dividas.findAll { idDivida, receitas ->
    divida = receitas[0].divida;
    return enumerador.converter(divida.situacaoDivida).valor == 'PARCELADA'
  }.collect { idDivida, itens -> idDivida }.join(',');
  parcelamentosRec = [];
  se(idsDividasParcelas != '') {
    parcelamentosRec = FonteTributos.parcelamentos.receitas.busca(criterio: "divida.id in ($idsDividasParcelas)");
  }
  dividas.each { idDivida, receitas ->
    divida = receitas[0].divida;
    
    se(enumerador.converter(divida.situacaoDivida).valor == 'ABERTO' || enumerador.converter(divida.situacaoDivida).valor == 'PARCELADA') {
      verificaDividasAbertas = 1;
    }
    referente = [
      codigo: divida.referente?.codigo,
      tipo  : enumerador.converter(divida.referente.tipo)
    ];
    parcelamento = nulo;
    idsReceitas = receitas.collect { it.id };
      acrescimo = acrescimosDivida.findAll { it.id in idsReceitas };
        imprimir "acrescimo=";
    imprimir acrescimo;
    parcReceita = parcelamentosRec.findAll { it.idDivida == divida.id };
      pagamento = pagamentosDetalhados.findAll { it.idDivida == divida.id };
        infoReferente = referentes?."$referente.tipo.valor"?."$referente.codigo";
    total = acrescimo.sum { it.total } ?: divida.valorTributoAtual;
    valor = acrescimo.sum { it.valor } ?: divida.valorTributoAtual;
    desconto = 0;
    valorPago = 0;
    correcao = acrescimo.sum { it.correcao } ?: 0;
    juros = acrescimo.sum { it.juro } ?: 0;
    multa = acrescimo.sum { it.multa } ?: 0;
    acrescimo.each { ac ->
      desconto += (ac.valorRemissao +
                   ac.valorAnistiaTributo +
                   ac.valorAnistiaCorrecao +
                   ac.valorAnistiaJuro +
                   ac.valorAnistiaMulta);
    }
    se(!pagamento.empty) {
      desconto = 0;
      valorPago = 0;
      pagamento?.each { pg ->
        se(enumerador.converter(divida.situacaoDivida).valor != 'ABERTO') {
          desconto += pg?.valorDescontoConcedidoCorrecao +
            pg?.valorDescontoConcedidoJuros +
            pg?.valorDescontoConcedidoLancado +
            pg?.valorDescontoConcedidoMulta +
            pg?.valorRemidoLancado +
            pg?.valorRemidoMulta +
            pg?.valorRemidoJuros +
            pg?.valorRemidoCorrecao;
        }
        valorPago += pg?.valorPagoLancado +
          pg?.valorPagoCorrecao +
          pg?.valorPagoJuros +
          pg?.valorPagoMulta +
          pg?.valorPagoCorrecaoParcelada +
          pg?.valorPagoMultaParcelada +
          pg?.valorPagoJurosParcelado;
      }
    }
    imprimir "v1=" + valor;
    se(!parcReceita.empty) {
      desconto = parcReceita.sum {
        it.valorDescontoTributo + it.valorDescontoCorrecao + it.valorDescontoJuro + it.valorDescontoMulta
      }
      valor = parcReceita.sum { it.valorTributo } ?: 0;
      correcao = parcReceita.sum { it.valorCorrecao } ?: 0;
      juros = parcReceita.sum { it.valorJuro } ?: 0;
      multa = parcReceita.sum { it.valorMulta } ?: 0;
      valorPago = 0;
      idParcelamento = parcReceita[0].idParcelamento;
      parcelamentoDb = FonteTributos.parcelamentos.busca(criterio: "id in ($idParcelamento)", primeiro: true);
      dataHora = Datas.formatar(parcelamentoDb.dhParcelamento, 'dd/MM/yyyy');
      parcelamento = "Nº $parcelamentoDb.nroParcelamento/$parcelamentoDb.anoParcelamento em $dataHora";
    }
    imprimir "v2=" + valor;
    total = valor + correcao + juros + multa;
    lancamentos << [
      parcelamento        : parcelamento,
      ano                 : divida.ano,
      creditoTributario   : [
        abreviatura: divida.creditoTributario.abreviatura,
        descricao  : divida.creditoTributario.descricao
      ],
      nroParcela          : divida.parcela,
      executadaProtestada :
      enumerador.converter(divida.executada).valor == "SIM" ?
      enumerador.converter(divida.executada) : enumerador.converter(divida.protestada),
      dtVencimento        : divida.dataVencimento,
      valorLancamento     : valor,
      valor               : valor,
      desconto            : desconto,
      correcao            : correcao ?: 0,
      juros               : juros ?: 0,
      multa               : multa ?: 0,
      total               : total - desconto,
      totalLancamento     : total - desconto,
      situacao            : divida.situacaoResumidaDivida,
      status              : enumerador.converter(divida.situacaoDivida),
      dtPagamento         : divida.dataQuitacao,
      valorPago           : valorPago,
      valorDiferenca      : divida.valorDiferencaPagamento,
      local               : divida.siglaBancoPagamento,
      tipoLancamento      : [valor: "DIVIDA_ATIVA", descricao: "Dívidas Ativas"],
      referente           : referente.tipo.descricao + " " + referente.codigo,
      referenteEndereco   : infoReferente?.endereco,
      referenteInformacoes: infoReferente?.informacoes,
      vencido             : Datas.diferencaDias(divida.dataVencimento, Datas.hoje()) > 0 ?
      [valor: "SIM", descricao: "Sim"] : [valor: "NAO", descricao: "Não"]
    ];
  }
}

// Montagem parcelamentos
se(BUSCA_PARCELAMENTOS) {
  idsParcelamentos = respostaParcelamentos.findAll { parcela ->
    return enumerador.converter(parcela.situacao).valor == 'ABERTO' &&
      Datas.diferencaDias(parcela.dtVencimento, Datas.hoje()) > 0
  }
  .groupBy { parc -> parc.parcelamento.id }
  .collect { idParcelamento, itens -> idParcelamento };
    acrescimosParcelamento = acrescimos.calcular('parcelamentos', idsParcelamentos);
  percorrer(respostaParcelamentos) { parcela ->
    se(enumerador.converter(parcela.situacao).valor == 'ABERTO') {
      verificaParcelamentosAbertos = 1;
    }
    vencido = Datas.diferencaDias(parcela.dtVencimento, Datas.hoje()) > 0 ?
      [valor: "SIM", descricao: "Sim"] : [valor: "NAO", descricao: "Não"];
        acrescimo = [];
    se(enumerador.converter(parcela.situacao).valor == 'ABERTO'
       && vencido.valor == "SIM") {
      acrescimo = acrescimosParcelamento.find { it.id == parcela.id };
        }
    total = acrescimo?.total ?: parcela.vlParcela - parcela.vlDesconto;
    
    total += (parcela.vlTotalTaxa +
              parcela.vlJuroFinanciamento +
              parcela.vlCorrecaoPrefixada
             );
    
    correcao = acrescimo?.correcao;
    juros = acrescimo?.juro;
    multa = acrescimo?.multa;
    
    pagamento = pagamentosDetalhados.findAll { it.idParcela == parcela.id }
    valor = acrescimo?.valor ?: parcela.vlParcela;
    valorPago = 0;
    desconto = parcela.vlDesconto;
    infos1 = composicoes.findAll { c -> c.idParcelamento == parcela.parcelamento.id }
    .collect { c -> c.abreviatura + '/' + c.ano }
    .join(', ');
    infos2 = "$parcela.parcelamento.configParcelamento.descricao " +
      " (Lei $parcela.parcelamento.configParcelamento.ato.nroOficial)";
    se(!pagamento.empty) {
      
      valorPago = 0;
      correcao = 0;
      multa = 0;
      juros = 0;
      
      pagamento?.each { pg ->
        
        total += pg?.valorDevidoCorrecao +
          pg?.valorDevidoJuros +
          pg?.valorDevidoMulta;
        
        valorPago += pg?.valorPagoLancado +
          pg?.valorPagoCorrecao +
          pg?.valorPagoJuros +
          pg?.valorPagoMulta +
          //
          pg?.valorPagoCorrecaoParcelada +
          pg?.valorPagoJurosParcelado +
          pg?.valorPagoMultaParcelada;
        
        correcao += pg?.valorDevidoCorrecao;
        multa += pg?.valorDevidoMulta;
        juros += pg?.valorDevidoJuros;
        
      }
    }
    lancamentos << [
      ano                 : parcela.parcelamento.anoParcelamento,
      creditoTributario   : [
        abreviatura: "N/A",
        descricao  : "N/A"
      ],
      nroParcela          : parcela.nroParcela,
      dtVencimento        : parcela.dtVencimento,
      valorLancamento     : valor,
      valor               : valor,
      desconto            : desconto,
      correcao            : correcao ?: 0,
      juros               : juros ?: 0,
      multa               : multa ?: 0,
      total               : total,
      totalLancamento     : total,
      situacao            : parcela.situacaoResumida,
      status              : enumerador.converter(parcela.situacao),
      dtPagamento         : parcela.dtQuitacao,
      valorPago           : valorPago,
      valorDiferenca      : parcela.vlDiferencaPagamento,
      local               : parcela.siglaBancoPagamento,
      tipoLancamento      : [valor: "PARCELAMENTO", descricao: "Parcelamentos"],
      referente           : "Parcelamento $parcela.parcelamento.nroParcelamento",
      referenteEndereco   : infos1,
      referenteInformacoes: infos2,
      vencido             : vencido
    ];
  }
}
mensagemPendencias = "";
se(verificaDebitosAbertos != 1 && verificaDividasAbertas != 1 && verificaParcelamentosAbertos != 1 && lancamentos.size== 0) {
  mensagemPendencias = "Sem nenhuma pendência";
}

linha = [
  mensagemPendencias: mensagemPendencias,
  tipoReferente: tipoReferente,
  referente: referente,
  idContribuinteref: idContribuinteref,
  contribuintes: contribuintes,
  contribuinte: [
    codigo      : contribuinte.codigo,
    nome        : contribuinte.nome,
    nomeFantasia: contribuinte.nomeFantasia,
    cpfCnpj     : contribuinte.cpfCnpj,
    endereco    : retornoEndereco        
  ],
  enderecoContrib: enderecoFormatado,
  lancamentos: lancamentos
];
imprimir linha
fonte.inserirLinha(linha);


retornar fonte;
```

---

## 🔑 Chaves de Exportação

| Item | Chave |
|---|---|
| Relatório | `b5a65dc8-cd8f-468f-8f4c-e09426f67399` |
| Fonte | `ac567402-0938-4082-854f-46097e5f78b7` |
