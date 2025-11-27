# Documentação do Script de Habite-se

Este documento descreve a funcionalidade e a estrutura do script responsável por buscar dados de um processo de Habite-se e de sua obra relacionada, formatar informações e estruturar os dados para a geração de um relatório.

## Visão Geral

O script é projetado para ser executado em um ambiente que fornece acesso a fontes de dados de tributos (`FONTE_TRIBUTOS = Dados.tributos.v2`) e a uma biblioteca de enumeração (`enumerador`). Ele recebe parâmetros de entrada (`ano` e `nroDocumento`) para identificar o Habite-se e, em seguida, coleta informações detalhadas sobre o Habite-se, a Obra, o Imóvel (ou Imóvel Rural), campos adicionais e responsáveis técnicos.

## Funcionalidades Principais

O script executa as seguintes tarefas:

1.  **Formatação de Valores:** Possui uma função `formatValor` para formatar valores monetários (`BigDecimal`) no padrão brasileiro (R$ com separador de milhar por ponto e decimal por vírgula).
2.  **Formatação de CPF/CNPJ:** Define uma função anônima `formatacaoCpfCnpj` para formatar strings de CPF (11 dígitos) ou CNPJ (14 dígitos) com a máscara apropriada.
3.  **Busca e Validação do Habite-se:** Busca o registro de Habite-se utilizando o `ano` e `nroDocumento` fornecidos. Em caso de falha na busca, o script é suspenso.
4.  **Processamento de Outorgados:** Coleta e formata a lista de contribuintes outorgados do Habite-se.
5.  **Busca e Validação da Obra:** Busca o registro da Obra associada ao Habite-se. Em caso de falha, o script é suspenso.
6.  **Coleta de Dados do Imóvel:** Identifica se a obra está associada a um Imóvel Urbano ou Rural e coleta dados como código, inscrição, endereço, logradouro, número, bairro, município e matrícula.
7.  **Busca de Campos Adicionais:** Busca o **Valor Venal Predial** do imóvel e outros campos adicionais da obra (Estrutura, Metragem, Tipo de Edificação, Tipo de Construção).
8.  **Busca de Responsáveis Técnicos:** Busca o nome do responsável técnico (engenheiro/arquiteto) da obra.
9.  **Estruturação do Relatório:** Define um esquema (`esquema`) para a estrutura de dados do relatório e popula uma linha (`linha`) com todos os dados coletados e formatados.
10. **Retorno de Dados:** Insere a linha de dados na fonte dinâmica (`fonte`) e a retorna para a geração do relatório.

## Parâmetros de Entrada

| Nome | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `ano` | Inteiro | Sim | Ano do registro do Habite-se. |
| `nroDocumento` | Inteiro | Sim | Número do documento do Habite-se. |
| `habitese` | Inteiro | Sim | (Parâmetro não utilizado diretamente no corpo do script, mas listado na documentação original) |

## Estrutura de Dados do Relatório (`esquema`)

O relatório final é estruturado com os seguintes campos:

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `nroDocumento` | Inteiro | Número do documento do Habite-se. |
| `nroProcesso` | Caracter | Número do processo do Habite-se. |
| `contribuintesOutorgados` | Caracter | Lista de outorgados formatada. |
| `dtEmissao` | Data | Data de emissão do Habite-se. |
| `tipo` | Enumerador | Tipo de Habite-se. |
| `metragem` | Número | Metragem do Habite-se. |
| `contribuinte` | Caracter | Nome do solicitante da obra. |
| `codigo` | Inteiro | Código do imóvel. |
| `inscricao` | Caracter | Inscrição imobiliária ou INCRA. |
| `enderecoDescritivo` | Caracter | Endereço completo formatado. |
| `restricao` | Enumerador | Restrição do Habite-se. |
| `restricaoObservacao` | Caracter | Observação da restrição. |
| `contribuinteCpfCnpj` | Caracter | CPF/CNPJ do solicitante da obra. |
| `logradouro` | Caracter | Nome do logradouro. |
| `numero` | Caracter | Número do imóvel. |
| `bairro` | Caracter | Nome do bairro. |
| `municipio` | Caracter | Nome do município. |
| `respExecucao` | Caracter | Nome do responsável pela execução da obra. |
| `respExecucaoCpfCnpj` | Caracter | CPF/CNPJ do responsável pela execução. |
| `dataConclusao` | Caracter | Data de liberação/conclusão da obra. |
| `dataEntrada` | Caracter | Data de entrada da obra. |
| `area` | Caracter | Medida da área da obra. |
| `matricula` | Caracter | Matrícula do imóvel. |
| `numeroProcesso` | Caracter | Número do processo da obra. |
| `valorVenal` | Caracter | Valor Venal Predial formatado. |
| `respTecnico` | Caracter | Nome do responsável técnico (engenheiro/arquiteto). |
| `estrutura` | Caracter | Campo adicional "Estrutura". |
| `metragemAd` | Caracter | Campo adicional "Metragem". |
| `categoria` | Caracter | Campo adicional "Tipo de Edificação". |
| `destinacao` | Caracter | Campo adicional "Tipo de Construção". |
| `endereco` | Caracter | Endereço completo do imóvel. |
| `observacaoObra` | Caracter | Observação da obra. |

## Código Fonte

```groovy
/*************************************************************************************************/
/*                                     Parâmetros do script                                      */
/*************************************************************************************************/
/*  Nome: ano                           Tipo: Inteiro                          Obrigatório: Sim  */
/*  Nome: nroDocumento                  Tipo: Inteiro                          Obrigatório: Sim  */
/*  Nome: habitese                      Tipo: Inteiro                          Obrigatório: Sim  */
/*************************************************************************************************/

FONTE_TRIBUTOS = Dados.tributos.v2;

enumerador = importar "enumerador";

def String formatValor(BigDecimal valorInicial) {
    //valorInicial: BigDecimal com o valor a ser formatado
    def valor = String.format("%.2f", valorInicial).replace('.', ',')

    def partes = valor.split(',')
    def parteInteira = partes[0]
    def parteDecimal = partes[1]
    def parteInteiraInvertida = parteInteira.reverse()
    def parteInteiraComPontos = parteInteiraInvertida.replaceAll(/(\d{3})/, '$1.').reverse()

    if (parteInteiraComPontos.startsWith('.')) {
        parteInteiraComPontos = parteInteiraComPontos.substring(1)
    }

    def valorFormatado = "R\$${parteInteiraComPontos},${parteDecimal}"
    return valorFormatado
}

formatacaoCpfCnpj = { campo ->
  campoFormatado = "";
  if (campo.tamanho() == 14){
    campoFormatado = campo.subTexto(0,2) + ".";
    campoFormatado += campo.subTexto(2,3) + ".";
    campoFormatado += campo.subTexto(5,3) + "/";
    campoFormatado += campo.subTexto(8,4) + "-";
    campoFormatado += campo.subTexto(12,2);
  } else {
    campoFormatado = campo.subTexto(0,3) + ".";
    campoFormatado += campo.subTexto(3,3) + ".";
    campoFormatado += campo.subTexto(6,3) + "-";
    campoFormatado += campo.subTexto(9,2);
  }
  retornar campoFormatado
}

codigo = "";
inscricao = "";
enderecoDescritivo = "";

//estrutura para o relatorio
esquema = [
  nroDocumento: Esquema.inteiro,
  nroProcesso: Esquema.caracter,
  contribuintesOutorgados: Esquema.caracter,
  dtEmissao: Esquema.data,
  tipo: enumerador.esquema,
  metragem: Esquema.numero,
  contribuinte: Esquema.caracter,
  codigo: Esquema.inteiro,
  inscricao: Esquema.caracter,
  enderecoDescritivo: Esquema.caracter,
  restricao: enumerador.esquema,
  restricaoObservacao: Esquema.caracter,
  contribuinteCpfCnpj: Esquema.caracter,
  logradouro: Esquema.caracter,
  numero: Esquema.caracter,
  bairro: Esquema.caracter,
  municipio: Esquema.caracter,
  respExecucao: Esquema.caracter,
  respExecucaoCpfCnpj: Esquema.caracter,
  dataConclusao: Esquema.caracter,
  dataEntrada: Esquema.caracter,
  area: Esquema.caracter,
  matricula: Esquema.caracter,
  numeroProcesso: Esquema.caracter,
  valorVenal: Esquema.caracter,
  respTecnico: Esquema.caracter,
  estrutura: Esquema.caracter,
  metragemAd: Esquema.caracter,
  categoria: Esquema.caracter,
  destinacao: Esquema.caracter,
  endereco: Esquema.caracter,
  observacaoObra: Esquema.caracter
];

fonte = Dados.dinamico.v2.novo(esquema);

imprimir parametros;

habitese = FONTE_TRIBUTOS.habitese.busca(
  parametros: [ano: parametros.ano?.valor, nroDocumento: parametros.nroDocumento?.valor], 
  primeiro: true
);

imprimir 'habitese';
imprimir habitese;

se (!habitese?.idObra) {
  suspender "Não foi possível encontrar o habite-se com os parâmetros [ano: " + parametros.ano?.valor + ", nroDocumento: " + parametros.nroDocumento?.valor + "]";
}

contribuintesOutorgados = "";
if(habitese.outorgadosHabitese){
  contribuintesOutorgados = [];
  percorrer(habitese.outorgadosHabitese){ itContribuintes ->
    contribuintesOutorgados << itContribuintes.contribuinte.codigo + " - " + itContribuintes.contribuinte.nome + " - " + formatacaoCpfCnpj(itContribuintes.contribuinte.cpfCnpj)
  }
  
  contribuintesOutorgados = contribuintesOutorgados.join(',')
}

obra = FONTE_TRIBUTOS.obras.busca(
  criterio: "id = ${habitese.idObra}",
  primeiro: true
);

imprimir 'obra';
imprimir obra;

se (!obra) {
  suspender "Não foi possível encontrar a obra com o identificador " + habitese?.idObra;
}

se (obra.imovel) {
  idImovel = obra.imovel.id
  codigo = obra.imovel.codigo;
  inscricao = obra.imovel.inscricaoImobiliariaFormatada;
  enderecoDescritivo = obra.imovel.enderecoFormatado;
  logradouro = obra.imovel.logradouro.nome;
  numero = obra.imovel.numero;
  bairro = obra.imovel.bairro.nome;
  municipio = obra.imovel.localidade.municipio.nome;
  matricula = obra.imovel.matricula;
  endereco = obra.imovel.enderecoFormatado;
  observacaoObra = obra.observacao
} senao {
  se (obra.imovelRural) {
    idImovel = obra.imovelRural.id
    codigo = obra.imovelRural.codigo;
    inscricao = obra.imovelRural.inscricaoIncra;
    enderecoDescritivo = obra.imovelRural.enderecoFormatado;
    logradouro = obra.imovelRural.logradouro.nome;
    numero = obra.imovelRural.numero;
    bairro = obra.imovelRural.bairro.nome;
    municipio = obra.imovelRural.localidade.municipio.nome;
    matricula = obra.imovelRural.matricula;
    endereco = obra.imovel.enderecoFormatado;
    observacaoObra = obra.observacao
  }
}

valorVenal = ""
respTecnico = ""
estrutura = ""
metragem = ""
categoria = ""
destinacao = ""

fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;

filtroCamposAdicionais = "idImovel = ${idImovel} and ano = ${Datas.hoje().format("yyyy").toInteger()} and campoAdicional.titulo = 'VALOR VENAL PREDIAL'"

dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais)

dadosCamposAdicionais.each { itemCamposAdicionais ->
  valorVenal = itemCamposAdicionais.vlCampo
}
///
fonteResponsaveistecnicos = Dados.tributos.v2.obra.responsaveistecnicos;

dadosResponsaveistecnicos = fonteResponsaveistecnicos.busca(campos: "engenheiroArquiteto(contribuinte(nome))", parametros:["idObra":habitese.idObra])

dadosResponsaveistecnicos.each { itemResponsaveistecnicos ->
  respTecnico = itemResponsaveistecnicos.engenheiroArquiteto.contribuinte.nome
}
///
fonteCamposAdicionais = Dados.tributos.v2.obra.camposAdicionais;

dadosCamposAdicionais = fonteCamposAdicionais.busca(campos: "campoAdicional(titulo), vlCampo, texto, areaTexto, opcoes", parametros:["idObra":habitese.idObra, "ano":Datas.hoje().format("yyyy").toInteger()])

dadosCamposAdicionais.each { itemCamposAdicionais ->
  
  switch(itemCamposAdicionais.campoAdicional.titulo){
    case "Estrutura":
    estrutura = itemCamposAdicionais.opcoes
    break
    
    case "Metragem":
    metragem = itemCamposAdicionais.vlCampo
    break
    
    case "Tipo de Edificação":
    categoria = itemCamposAdicionais.opcoes
    break
    
    case "Tipo de Construção":
    destinacao = itemCamposAdicionais.opcoes
    break
  }
}

linha = [
  nroDocumento: habitese.nroDocumento,
  nroProcesso: habitese.processo,
  contribuintesOutorgados: contribuintesOutorgados,
  dtEmissao: habitese.dtEmissao,
  tipo: enumerador.converter(habitese.tipo),
  metragem: habitese.metragem ?: 0,
  contribuinte: obra.solicitante.nome,
  contribuinteCpfCnpj: formatacaoCpfCnpj(obra.solicitante.cpfCnpj),
  codigo: codigo,
  inscricao: inscricao,
  enderecoDescritivo: enderecoDescritivo,
  restricao: enumerador.converter(habitese.restricao),
  restricaoObservacao: habitese.restricaoObservacao,
  logradouro: logradouro,
  numero: numero,
  bairro: bairro,
  municipio: municipio,
  respExecucao: obra.responsavelExecucao.contribuinte.nome,
  respExecucaoCpfCnpj: formatacaoCpfCnpj(obra.responsavelExecucao.contribuinte.cpfCnpj),
  dataEntrada: obra.dataEntrada.format("dd/MM/yyyy"),
  numeroProcesso: obra.nroProcesso,
  dataConclusao: obra.dataLiberacao.format("dd/MM/yyyy") == "01/01/1800" ? "" : obra.dataLiberacao.format("dd/MM/yyyy"),
  area: obra.medida,
  matricula: matricula,
  valorVenal: formatValor(valorVenal),
  respTecnico: respTecnico,
  estrutura: estrutura,
  metragemAd: metragem,
  categoria: categoria,
  destinacao:destinacao,
  endereco: endereco,
  observacaoObra: observacaoObra
];

imprimir linha;

fonte.inserirLinha(linha);

retornar fonte;
```

---

Link: [[Leoberto Leal Habite-se](https://relatorios.plataforma.betha.cloud/#/entidades/ZGF0YWJhc2U6ODE3LGVudGl0eToxNTY4/sistemas/58/relatorio/3164510?standalone=true)]