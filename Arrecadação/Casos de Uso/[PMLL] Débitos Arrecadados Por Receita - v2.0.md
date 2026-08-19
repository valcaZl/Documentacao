# Documentação do Script — Relatório de Pagamentos de Tributos (Detalhes)

## Visão Geral

Este script é uma **fonte dinâmica** (BFC-Script) que consulta os pagamentos de tributos registrados no sistema (`Dados.tributos.v2.pagamentos.detalhes`), aplica um conjunto de filtros opcionais informados pelo usuário via `parametros`, e monta um relatório consolidado com os valores pagos por parcela (principal, correção, juros, multa e eventuais diferenças), além de dados do crédito, da receita, da configuração de parcelamento e — quando aplicável — do convênio bancário utilizado no pagamento.

O resultado é retornado como uma fonte dinâmica (`relatorio`) pronta para ser exibida em um relatório do sistema.

## Fonte de Dados

| Fonte | Descrição |
| :--- | :--- |
| `Dados.tributos.v2.pagamentos.detalhes` | Fonte principal, com o detalhamento dos pagamentos de tributos. |
| `Dados.tributos.v2.convenios` | Consultada linha a linha, apenas quando o pagamento possui `idConvenio > 0`, para obter os dados bancários do convênio. |

## Estrutura do Relatório (`esquema`)

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `credito.abreviatura` | Caracter | Abreviatura do crédito tributário do débito. |
| `credito.descricao` | Caracter | Descrição do crédito tributário do débito. |
| `configuracao.descricao` | Caracter | Descrição da configuração de parcelamento vinculada ao débito. |
| `nroParcela` | Inteiro | Número da parcela paga. |
| `receita.abreviatura` | Caracter | Abreviatura da receita (ou `"JurFin"` quando aplicada a regra especial de juros de financiamento). |
| `receita.descricao` | Caracter | Descrição da receita (ou `"Juro de financiamento"` quando aplicada a regra especial). |
| `valorPagoParcela` | Número | Soma do valor lançado + multa parcelada + juros parcelado + correção parcelada pagos. |
| `valorPagoCorrecao` | Número | Valor pago referente à correção monetária. |
| `valorPagoJuros` | Número | Valor pago referente a juros. |
| `valorPagoMulta` | Número | Valor pago referente a multa. |
| `valorDiferenca` | Número | Soma das diferenças de correção, juros, multa e tributo. |
| `convenio.idConvenio` | Inteiro | Identificador do convênio bancário usado no pagamento (0 quando não há). |
| `convenio.descConv` | Caracter | Descrição do convênio. |
| `convenio.agConv` | Caracter | Agência bancária do convênio, no formato `nroAgencia-digAgencia`. |
| `convenio.contaConv` | Caracter | Conta bancária do convênio, no formato `contaBancaria-dvContaBancaria`. |
| `convenio.cedConv` | Caracter | Cedente do convênio. |

> **Atenção:** a linha (`linha`) montada durante o processamento também inclui o campo `codRef` (código de referência do débito), mas esse campo **não está declarado em `esquema`**. Isso é uma inconsistência do script — o campo deve ser adicionado ao esquema (ex.: `codRef: Esquema.caracter`) para que o valor efetivamente apareça no relatório, caso contrário poderá ser descartado ou gerar erro na inserção da linha.

## Parâmetros de Entrada

Todos os parâmetros são opcionais; quando não informados, o filtro correspondente simplesmente não é adicionado ao critério de busca.

| Parâmetro | Descrição | Campo filtrado |
| :--- | :--- | :--- |
| `dataPgtoInicial` | Data inicial de pagamento | `dataPagamentoString >=` |
| `dataPgtoFinal` | Data final de pagamento | `dataPagamentoString <=` |
| `credito` | Crédito(s) tributário(s) | `idCredito in (...)` |
| `receita` | Receita(s) | `idReceita in (...)` |
| `ano` | Ano de referência | `ano =` |
| `pessoa` | Contribuinte(s) | `idContribuinte in (...)` |
| `bairro` | Bairro(s) | `economico.endereco.bairro.id`, `contribuinte.endereco.bairro.id` ou `imovel.endereco.bairro.id in (...)` |
| `tipoBaixa` | Tipo de baixa do pagamento | `tipoBaixa in ('...')` |
| `logradouro` | Logradouro(s) | `economico.endereco.logradouro.id`, `contribuinte.endereco.logradouro.id` ou `imovel.endereco.logradouro.id in (...)` |
| `nroParcela` | Número(s) de parcela | `nroParcela in (...)` |
| `configuracao` | Configuração de parcelamento | `idConfigParcelamento =` |
| `dataVencimentoInicial` | Data inicial de vencimento | `dtVencimento >=` |
| `dataVencimentoFinal` | Data final de vencimento | `dtVencimento <=` |
| `dataCreditoInicial` | Data inicial de crédito | `dataCreditoString >=` |
| `dataCreditoFinal` | Data final de crédito | `dataCreditoString <=` |
| `convenio` | Convênio bancário | `pagamento.idConvenio =` |

Todas as datas são formatadas para `yyyy-MM-dd` através de `Datas.formatar(...)` antes de compor o critério.

## Critério de Busca (`criterio`)

O critério parte de um valor fixo:

```
pagamento.id is not null
```

> O comentário no código (`// PADRÃO APRESENTARÁ APENAS OS DÉBITOS`) indica que a intenção original era que, por padrão, o relatório trouxesse apenas os débitos; porém a condição efetivamente usada (`pagamento.id is not null`) filtra registros que **possuem pagamento**, o que é o oposto do comentário. Vale confirmar com quem mantém o script se a condição está correta ou se o comentário está desatualizado.

A cada parâmetro informado, uma cláusula `and` é concatenada ao critério, seguindo o padrão:

```bfc-script
se (parametros.<param>?.valor) {
  se (criterio!='') { criterio += ' and '; }
  criterio += "<condição>";
}
```

Duas exceções a esse padrão: `bairro` e `logradouro` são lidos diretamente com `.valor` (sem o operador seguro `?.`), o que pode gerar erro caso `parametros.bairro` ou `parametros.logradouro` não existam na definição do relatório.

O critério final é impresso no console para depuração:

```bfc-script
imprimir "criterio="+criterio;
```

## Processamento dos Registros

Após a busca (`fonte.busca(criterio: criterio)`), o script percorre cada pagamento (`pgto`) e executa os seguintes passos:

1. **Extração de valores com tratamento de nulos** (`?.` e `?:`):
   - `codRef` — código de referência do débito (`pgto.debito.referente.codigo`).
   - `descRec` / `abrevRec` — descrição/abreviatura da receita, com fallback para string vazia.
   - `tipoRec` — tipo de receita do pagamento.
   - `idConvenio` — identificador do convênio, com fallback para `0`.

2. **Regra especial de juros de financiamento:** se `tipoRec == "JURO_FINANCIAMENTO"` e a receita não tem descrição (`descRec == ""`), o script força:
   - `descRec = "Juro de financiamento"`
   - `abrevRec = "JurFin"`

3. **Busca dos dados do convênio:** se `idConvenio > 0`, o script consulta `Dados.tributos.v2.convenios` filtrando por `id = idConvenio` e, para o registro encontrado, extrai:
   - `descConv` — descrição do convênio;
   - `agConv` — agência no formato `nroAgencia-digAgencia`;
   - `contaConv` — conta no formato `contaBancaria-dvContaBancaria`;
   - `cedConv` — cedente.

4. **Montagem da linha (`linha`)** com os campos do crédito, configuração de parcelamento, receita (já tratada pela regra especial), valores pagos (parcela, correção, juros, multa), diferença total e dados do convênio.

   - `valorPagoParcela` é calculado somando `valorPagoLancado + valorPagoMultaParcelada + valorPagoJurosParcelado + valorPagoCorrecaoParcelada`.
   - `valorDiferenca` é calculado somando `valorDiferencaCorrecao + valorDiferencaJuros + valorDiferencaMulta + valorDiferencaTributo`.

5. **Depuração:** cada linha montada é impressa em formato JSON (`imprimir JSON.escrever(linha)`) antes de ser inserida no relatório.

6. **Inserção:** a linha é adicionada à fonte dinâmica `relatorio.inserirLinha(linha)`.

Ao final do laço, o script retorna a fonte dinâmica populada:

```bfc-script
retornar relatorio;
```

## Pontos de Atenção

- **Campo `codRef` fora do esquema:** conforme citado acima, `codRef` é preenchido na linha mas não existe em `esquema`; recomenda-se adicionar `codRef: Esquema.caracter` ao esquema (ou remover o campo da linha, se não for necessário).
- **Comentário do critério base divergente:** o comentário `PADRÃO APRESENTARÁ APENAS OS DÉBITOS` não corresponde à condição `pagamento.id is not null`, que na prática filtra pagamentos existentes, não débitos em aberto.
- **`convenio` aceita apenas um valor:** diferente dos demais filtros de lista (`credito`, `receita`, `pessoa`, `nroParcela`), o filtro de convênio usa igualdade simples (`pagamento.idConvenio = valor`) em vez de `in (...)`. Há inclusive uma linha comentada (`//criterio += "pagamento.idConvenio in ($parametros.convenio.valor)"`) sugerindo que o suporte a múltiplos convênios foi cogitado, mas não implementado.
- **`bairro` e `logradouro` sem operador seguro:** ao contrário dos demais filtros, esses dois leem `parametros.bairro.valor` e `parametros.logradouro.valor` diretamente, sem `?.`, podendo causar erro se o parâmetro não estiver definido no relatório.
- **Impressões de depuração em produção:** os comandos `imprimir "criterio="+criterio` e `imprimir JSON.escrever(linha)` (este último dentro do laço, executado para cada registro) são úteis para depuração, mas podem poluir o log e impactar performance em relatórios com grande volume de pagamentos; recomenda-se removê-los ou condicioná-los a um modo de depuração antes de uso em produção.
- **Concatenação direta de valores no critério:** os valores de parâmetros são inseridos diretamente na string do critério (ex.: `"ano = " + parametros.ano.valor`, `"idCredito in ($parametros.credito.valor)"`). Isso segue o padrão comum de outras fontes dinâmicas do sistema, mas depende de que os parâmetros sejam sempre validados/tipados pela definição do relatório, já que não há tratamento explícito contra valores inesperados.
