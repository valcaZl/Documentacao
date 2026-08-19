# 💰 Documentação do Script de Relatório de Pagamentos (Detalhes)

Este script em **BFC-Script/Groovy** consulta a fonte `Dados.tributos.v2.pagamentos.detalhes`, aplicando uma série de **filtros opcionais** informados por parâmetro (período de pagamento, crédito, receita, ano, contribuinte, bairro, logradouro, tipo de baixa, parcela, configuração de parcelamento, período de vencimento, período de crédito e convênio). Para cada pagamento encontrado, o script trata valores de receita, identifica dados do convênio de cobrança (quando existir) e consolida tudo em uma fonte dinâmica (`relatorio`) usada na geração do relatório de pagamentos.

---

## ✨ Fontes de Dados Utilizadas

| Fonte | Finalidade |
| --- | --- |
| `Dados.tributos.v2.pagamentos.detalhes` | Fonte principal: detalhes dos pagamentos realizados |
| `Dados.tributos.v2.convenios` | Dados do convênio de cobrança vinculado ao pagamento (agência, conta, cedente) |

---

## 📋 Estrutura de Dados do Relatório (`esquema`)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `credito` | Objeto | Dados do crédito do débito pago (ver subestrutura) |
| `configuracao` | Objeto | Descrição da configuração de parcelamento |
| `nroParcela` | Inteiro | Número da parcela paga |
| `receita` | Objeto | Dados da receita do pagamento (ver subestrutura) |
| `valorPagoParcela` | Número | Valor total pago na parcela (lançado + multa + juros + correção) |
| `valorPagoCorrecao` | Número | Valor pago referente à correção |
| `valorPagoJuros` | Número | Valor pago referente a juros |
| `valorPagoMulta` | Número | Valor pago referente à multa |
| `valorDiferenca` | Número | Soma das diferenças de correção, juros, multa e tributo |
| `convenio` | Objeto | Dados do convênio de cobrança (ver subestrutura) |

> ⚠️ O campo `codRef`, atribuído na `linha` (ver Bloco 3), **não está declarado no `esquema`** — ver seção Observações.

### Subestrutura `credito`
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `abreviatura` | Caracter | Abreviatura do crédito |
| `descricao` | Caracter | Descrição do crédito |

### Subestrutura `configuracao`
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `descricao` | Caracter | Descrição da configuração de parcelamento |

### Subestrutura `receita`
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `abreviatura` | Caracter | Abreviatura da receita |
| `descricao` | Caracter | Descrição da receita |

### Subestrutura `convenio`
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `idConvenio` | Inteiro | Identificador do convênio |
| `descConv` | Caracter | Descrição do convênio |
| `agConv` | Caracter | Agência bancária, no formato `nroAgencia-digAgencia` |
| `contaConv` | Caracter | Conta bancária, no formato `contaBancaria-dvContaBancaria` |
| `cedConv` | Caracter | Cedente do convênio |

---

## 🔎 Parâmetros de Entrada (todos opcionais)

| Parâmetro | Cláusula aplicada no `criterio` |
| --- | --- |
| `dataPgtoInicial` | `dataPagamentoString >= 'yyyy-MM-dd'` |
| `dataPgtoFinal` | `dataPagamentoString <= 'yyyy-MM-dd'` |
| `credito` | `idCredito in (...)` |
| `receita` | `idReceita in (...)` |
| `ano` | `ano = <valor>` |
| `pessoa` | `idContribuinte in (...)` |
| `bairro` | `economico.endereco.bairro.id in (...) or contribuinte.endereco.bairro.id in (...) or imovel.endereco.bairro.id in (...)` |
| `tipoBaixa` | `tipoBaixa in ('<valor>')` |
| `logradouro` | `economico.endereco.logradouro.id in (...) or contribuinte.endereco.logradouro.id in (...) or imovel.endereco.logradouro.id in (...)` |
| `nroParcela` | `nroParcela in (...)` |
| `configuracao` | `idConfigParcelamento = <valor>` |
| `dataVencimentoInicial` | `dtVencimento >= 'yyyy-MM-dd'` |
| `dataVencimentoFinal` | `dtVencimento <= 'yyyy-MM-dd'` |
| `dataCreditoInicial` | `dataCreditoString >= 'yyyy-MM-dd'` |
| `dataCreditoFinal` | `dataCreditoString <= 'yyyy-MM-dd'` |
| `convenio` | `pagamento.idConvenio = <valor>` |

Todos os filtros são combinados com `and`. O critério inicial (`" pagamento.id is not null"`) é sempre aplicado — o comentário no código indica que, por padrão, o relatório apresentará apenas os débitos.

---

## 🧭 Explicação Geral do Código

O script começa criando a fonte dinâmica `relatorio` a partir do `esquema`. Em seguida, monta dinamicamente a string `criterio`, adicionando uma cláusula `and` para cada parâmetro informado pelo usuário (datas de pagamento, crédito, receita, ano, contribuinte, bairro, tipo de baixa, logradouro, parcela, configuração, datas de vencimento, datas de crédito e convênio). Com o critério final montado, busca os pagamentos na fonte `Dados.tributos.v2.pagamentos.detalhes`. Para cada pagamento, trata a descrição da receita (com um caso especial para juros de financiamento), busca os dados do convênio de cobrança quando houver `idConvenio`, monta a `linha` somando os valores pagos e as diferenças, imprime o resultado em JSON e insere a linha na fonte dinâmica. Por fim, retorna o `relatorio`.

---

## 🧩 Blocos de Código

### 1. Esquema e Inicialização da Fonte

```groovy
fonte = Dados.tributos.v2.pagamentos.detalhes;
esquema = [ /* ...campos descritos na seção Esquema... */ ];
relatorio = Dados.dinamico.v2.novo(esquema);
```

Define a fonte de origem dos pagamentos e cria a fonte dinâmica de saída (`relatorio`) com base no `esquema`.

---

### 2. Montagem Dinâmica do Critério de Busca

```bfc-script
criterio = " pagamento.id is not null"; // PADRÃO APRESENTARÁ APENAS OS DÉBITOS

se (parametros.dataPgtoInicial?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio += "dataPagamentoString >= '" + Datas.formatar(parametros.dataPgtoInicial.valor, "yyyy-MM-dd") + "'";
}

// ... mesmo padrão repetido para dataPgtoFinal, credito, receita, ano, pessoa,
// bairro, tipoBaixa, logradouro, nroParcela, configuracao,
// dataVencimentoInicial/Final, dataCreditoInicial/Final e convenio

imprimir "criterio="+criterio;
pagamentos = fonte.busca(criterio: criterio);
```

Cada parâmetro é testado individualmente (`se (parametros.X?.valor)`); quando informado, uma nova cláusula é concatenada ao `criterio` com o conector `and`. Os filtros de `bairro` e `logradouro` são os únicos que combinam múltiplas colunas com `or`, pois o bairro/logradouro pode estar vinculado ao econômico, ao contribuinte ou ao imóvel. Ao final, o `criterio` é impresso no console (útil para depuração) e utilizado na busca dos pagamentos.

---

### 3. Tratamento dos Dados de Receita e Convênio

```bfc-script
percorrer (pagamentos) { pgto ->
  codRef     = pgto.debito.referente.codigo
  descRec    = pgto.receita?.descricao?:""
  abrevRec   = pgto.receita?.abreviatura?:""
  tipoRec    = pgto.tipoReceitaPagamento?.valor?:""
  idConvenio = pgto.pagamento.idConvenio?:0
  descConv   = ""
  agConv     = ""
  contaConv  = ""
  cedConv    = ""

  se (tipoRec == "JURO_FINANCIAMENTO" && descRec == ""){
    descRec  = "Juro de financiamento"
    abrevRec = "JurFin"
  }

  se (idConvenio > 0){
    fonteConvenios = Dados.tributos.v2.convenios;
    filtroConvenios = "id = $idConvenio"
    dadosConvenios = fonteConvenios.busca(criterio: filtroConvenios)

    percorrer (dadosConvenios) { itemConvenios ->
      descConv = itemConvenios.descricao
      agConv   = "${itemConvenios.agenciaBancaria?.nroAgencia?:""}-${itemConvenios.agenciaBancaria?.digAgencia?:""}"
      contaConv = "${itemConvenios.contaBancaria?:""}-${itemConvenios.dvContaBancaria?:""}"
      cedConv   = "${itemConvenios.cedente?:""}"
    }
  }
  // ...
}
```

Para cada pagamento, o script extrai o código de referência do débito (`codRef`) e os dados da receita, aplicando um fallback especial: quando o tipo de receita é `JURO_FINANCIAMENTO` e a descrição vier vazia, força a descrição para `"Juro de financiamento"` e a abreviatura para `"JurFin"`. Se o pagamento estiver vinculado a um convênio (`idConvenio > 0`), busca o convênio em `Dados.tributos.v2.convenios` e monta a agência (`nroAgencia-digAgencia`), a conta (`contaBancaria-dvContaBancaria`) e o cedente.

---

### 4. Montagem da Linha e Inserção na Fonte

```bfc-script
linha = [
  credito: [descricao: pgto.debito?.descricaoCredito,
            abreviatura: pgto.debito?.abreviaturaCredito],
  nroParcela: pgto.debito?.nroParcela,
  configuracao: [descricao: pgto.debito?.descricaoParcelamento],
  receita: [descricao: descRec,
            abreviatura: abrevRec],
  valorPagoParcela: pgto.valorPagoLancado + pgto.valorPagoMultaParcelada + pgto.valorPagoJurosParcelado + pgto.valorPagoCorrecaoParcelada,
  valorPagoCorrecao: pgto.valorPagoCorrecao,
  valorPagoJuros: pgto.valorPagoJuros,
  valorPagoMulta: pgto.valorPagoMulta,
  valorDiferenca: pgto.valorDiferencaCorrecao + pgto.valorDiferencaJuros + pgto.valorDiferencaMulta + pgto.valorDiferencaTributo,
  codRef: codRef,
  convenio: [idConvenio: idConvenio,
             descConv: descConv,
             agConv: agConv,
             contaConv: contaConv,
             cedConv: cedConv]
];

imprimir JSON.escrever(linha)

relatorio.inserirLinha(linha);
```

Monta o objeto `linha` com os dados do crédito, parcela, configuração, receita (já tratada no bloco anterior), os valores pagos (`valorPagoParcela` como soma de lançado + multa + juros + correção parceladas), a diferença total (`valorDiferenca`) e os dados do convênio. A linha é impressa em formato JSON para depuração e então inserida na fonte dinâmica `relatorio`.

---

### 5. Retorno do Relatório

```bfc-script
retornar relatorio;
```

Após percorrer todos os pagamentos retornados pela busca, a fonte dinâmica populada é retornada para geração do relatório.

---

## ⚠️ Observações

- **Campo `codRef` fora do `esquema`:** a `linha` atribui o campo `codRef: codRef`, mas o `esquema` declarado no início do script **não possui** esse campo. Dependendo da implementação de `Dados.dinamico.v2`, isso pode gerar um campo ignorado silenciosamente ou um erro em tempo de execução — vale confirmar se o `esquema` deveria incluir `codRef: Esquema.caracter` (ou tipo equivalente).
- **Comentário do critério base:** o comentário `// PADRÃO APRESENTARÁ APENAS OS DÉBITOS` acompanha o critério `pagamento.id is not null`, mas semanticamente esse filtro garante que **apenas pagamentos já efetivados** (com `pagamento` vinculado) sejam retornados; vale revisar se o comentário reflete a intenção original.
- **Filtro de convênio comentado:** existe uma linha comentada (`//criterio += "pagamento.idConvenio in ($parametros.convenio.valor)";`) substituída por uma comparação de igualdade (`pagamento.idConvenio = $parametros.convenio.valor`) — ou seja, atualmente o filtro de convênio **não suporta múltiplos convênios selecionados**, apenas um único valor.
- **Filtros combinados com `or` entre entidades:** os filtros de `bairro` e `logradouro` verificam três origens possíveis (econômico, contribuinte e imóvel), cobrindo diferentes tipos de cadastro vinculados ao pagamento.
- **Concatenação de string em `criterio`:** os valores de parâmetros são interpolados diretamente na string do critério (ex.: `"idCredito in ($parametros.credito.valor)"`), sem escaping adicional — o comportamento depende de os parâmetros virem sempre como listas/valores numéricos seguros.

---

## 📜 Código Completo

```bfc-script
fonte = Dados.tributos.v2.pagamentos.detalhes;
esquema = [credito: Esquema.objeto([abreviatura: Esquema.caracter, descricao: Esquema.caracter]),
           configuracao: Esquema.objeto([ descricao: Esquema.caracter ]),
           nroParcela: Esquema.inteiro,
           receita: Esquema.objeto([ abreviatura: Esquema.caracter, descricao: Esquema.caracter ]),
           valorPagoParcela: Esquema.numero,
           valorPagoCorrecao: Esquema.numero,
           valorPagoJuros: Esquema.numero,
           valorPagoMulta: Esquema.numero,
           valorDiferenca: Esquema.numero,
           convenio: Esquema.objeto([ idConvenio: Esquema.inteiro, descConv: Esquema.caracter, agConv: Esquema.caracter, contaConv: Esquema.caracter, cedConv: Esquema.caracter ])
          ];
relatorio = Dados.dinamico.v2.novo(esquema);
criterio = " pagamento.id is not null"; // PADRÃO APRESENTARÁ APENAS OS DÉBITOS
se (parametros.dataPgtoInicial?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio += "dataPagamentoString >= '" + Datas.formatar(parametros.dataPgtoInicial.valor, "yyyy-MM-dd") + "'";
}
se (parametros.dataPgtoFinal?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "dataPagamentoString <= '" + Datas.formatar(parametros.dataPgtoFinal.valor, "yyyy-MM-dd") + "'"
}
se (parametros.credito?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "idCredito in ($parametros.credito.valor)";
}
se (parametros.receita?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "idReceita in ($parametros.receita.valor)";
  
}
se (parametros.ano?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "ano = " + parametros.ano.valor;
  
}
se (parametros.pessoa?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "idContribuinte in ($parametros.pessoa.valor)";
}
bairro = parametros.bairro.valor;
se (bairro && bairro != '') {
  se (criterio !='') {
    criterio += ' and ';
  }
  criterio +=  "( economico.endereco.bairro.id in ($parametros.bairro.valor)" +
    " or contribuinte.endereco.bairro.id in ($parametros.bairro.valor)" + 
    " or imovel.endereco.bairro.id in ($parametros.bairro.valor) )";    
}
se (parametros.tipoBaixa?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "tipoBaixa in ('$parametros.tipoBaixa.valor')";
}
logradouro = parametros.logradouro.valor;
se (logradouro && logradouro != '') {
  se (criterio !='') {
    criterio += ' and ';
  }
  criterio +=  "( economico.endereco.logradouro.id in ($logradouro)" +
    " or contribuinte.endereco.logradouro.id in ($logradouro)" + 
    " or imovel.endereco.logradouro.id in ($logradouro) )";
}
se (parametros.nroParcela?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "nroParcela in ($parametros.nroParcela.valor)";
}
se (parametros.configuracao?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "idConfigParcelamento = " + parametros.configuracao.valor;
}
se (parametros.dataVencimentoInicial?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio += "dtVencimento >= '" + Datas.formatar(parametros.dataVencimentoInicial.valor, "yyyy-MM-dd") + "'";
}
se (parametros.dataVencimentoFinal?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "dtVencimento <= '" + Datas.formatar(parametros.dataVencimentoFinal.valor, "yyyy-MM-dd") + "'"
}
se (parametros.dataCreditoInicial?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio += "dataCreditoString >= '" + Datas.formatar(parametros.dataCreditoInicial.valor, "yyyy-MM-dd") + "'";
}
se (parametros.dataCreditoFinal?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  criterio +=  "dataCreditoString <= '" + Datas.formatar(parametros.dataCreditoFinal.valor, "yyyy-MM-dd") + "'"
}
se (parametros.convenio?.valor) {
  se (criterio!='') {
    criterio += ' and ';
  }
  //criterio +=  "pagamento.idConvenio in ($parametros.convenio.valor)";
  criterio +=  "pagamento.idConvenio = "  + parametros.convenio.valor;
  
}
imprimir "criterio="+criterio;
pagamentos = fonte.busca(criterio: criterio);
percorrer (pagamentos) { pgto ->
  codRef     = pgto.debito.referente.codigo
  descRec    = pgto.receita?.descricao?:""
  abrevRec   = pgto.receita?.abreviatura?:""
  tipoRec    = pgto.tipoReceitaPagamento?.valor?:""
  idConvenio = pgto.pagamento.idConvenio?:0
  descConv   = ""
  agConv     = ""
  contaConv  = ""
  cedConv    = ""
  
  
  se (tipoRec == "JURO_FINANCIAMENTO" && descRec == ""){
    descRec  = "Juro de financiamento"
    abrevRec = "JurFin"
  }
  
  se (idConvenio > 0){
    fonteConvenios = Dados.tributos.v2.convenios;
    filtroConvenios = "id = $idConvenio"
    dadosConvenios = fonteConvenios.busca(criterio: filtroConvenios)
    
    percorrer (dadosConvenios) { itemConvenios ->
      descConv = itemConvenios.descricao
      agConv   = "${itemConvenios.agenciaBancaria?.nroAgencia?:""}-${itemConvenios.agenciaBancaria?.digAgencia?:""}"
      contaConv     = "${itemConvenios.contaBancaria?:""}-${itemConvenios.dvContaBancaria?:""}"
      cedConv   = "${itemConvenios.cedente?:""}"
    }
  }
  
  
  linha = [
    
    credito: [descricao: pgto.debito?.descricaoCredito,
              abreviatura: pgto.debito?.abreviaturaCredito],
    nroParcela: pgto.debito?.nroParcela,
    configuracao: [descricao: pgto.debito?.descricaoParcelamento],
    receita: [descricao: descRec,
              abreviatura: abrevRec],
    valorPagoParcela: pgto.valorPagoLancado + pgto.valorPagoMultaParcelada + pgto.valorPagoJurosParcelado + pgto.valorPagoCorrecaoParcelada,
    valorPagoCorrecao: pgto.valorPagoCorrecao,
    valorPagoJuros: pgto.valorPagoJuros,
    valorPagoMulta: pgto.valorPagoMulta,
    valorDiferenca: pgto.valorDiferencaCorrecao + pgto.valorDiferencaJuros + pgto.valorDiferencaMulta + pgto.valorDiferencaTributo,
    codRef: codRef,
    convenio: [idConvenio: idConvenio,
               descConv: descConv,
               agConv: agConv,
               contaConv: contaConv,
               cedConv: cedConv]
    //convenio: parametros.convenio.valor
  ];
  
  imprimir JSON.escrever(linha)
  
  relatorio.inserirLinha(linha);	
  
}
retornar relatorio;
```

---

> 📄 Documentação gerada a partir do script de Relatório de Pagamentos (Detalhes), seguindo o padrão de documentação `valcaZl/Documentacao`.
