# Documentação do Script de Exportação de Dados de Imóveis

Este script Groovy é projetado para extrair e consolidar uma vasta gama de informações sobre imóveis do sistema, incluindo dados cadastrais, informações do responsável, débitos de IPTU e diversos campos adicionais. O objetivo final é gerar um arquivo CSV com todos esses dados, permitindo análises e integrações externas.

## Explicação Geral do Código

O script inicia definindo as fontes de dados necessárias e duas funções auxiliares para formatação de CPF/CNPJ e valores monetários. Em seguida, ele configura o arquivo CSV de saída com um cabeçalho detalhado. O fluxo principal envolve a busca de imóveis com base em filtros de situação e tipo, o preenchimento de um mapa (`mapImoveis`) com as informações básicas de cada imóvel. Posteriormente, o script enriquece esse mapa buscando débitos de IPTU e diversos campos adicionais (como área construída, valor venal, etc.) e associando-os aos imóveis correspondentes. Finalmente, ele itera sobre o mapa enriquecido e escreve cada registro no arquivo CSV, formatando os dados conforme necessário.

## Blocos de Código

### 1. Definição de Fontes e Funções Auxiliares

```groovy
//FONTES//
fonteImoveis = Dados.tributos.v2.imoveis;
fonteDebitos = Dados.tributos.v2.debitos;
fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;

//FORMATAÇÃO DO CPF/CNPJ//
def String formatCpfCnpj(String cpfCnpj) {
  //cpfCnpj: String numeral, com tamanho 11 ou 14;
  if(cpfCnpj.trim().size() == 11) {
    return cpfCnpj.trim().take(11).replaceAll(/(\d{3})(\d{3})(\d{3})(\d{2})/) { match ->
      "${match[1]}.${match[2]}.${match[3]}-${match[4]}"
    }
  } else if (cpfCnpj.trim().size() == 14) {
    return cpfCnpj.trim().take(14).replaceAll(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/) { match ->
      "${match[1]}.${match[2]}.${match[3]}/${match[4]}-${match[5]}"
    }
  } else {
    return cpfCnpj;
  }
}

def String formatValor(BigDecimal valorInicial) {
  //valorInicial: BigDecimal com o valor a ser formatado
  def valor = String.format("%.2f", valorInicial).replace(".", ",")
  
  def partes = valor.split(",")
  def parteInteira = partes[0]
  def parteDecimal = partes[1]
  def parteInteiraInvertida = parteInteira.reverse()
  def parteInteiraComPontos = parteInteiraInvertida.replaceAll(/(\d{3})/, '$1.').reverse()
  
  if (parteInteiraComPontos.startsWith(".")) {
    parteInteiraComPontos = parteInteiraComPontos.substring(1)
  }
  
  def valorFormatado = "R\\$${parteInteiraComPontos},${parteDecimal}"
  return valorFormatado
}
```

Este bloco inicializa as fontes de dados (`fonteImoveis`, `fonteDebitos`, `fonteCamposAdicionais`) que serão utilizadas para buscar as informações. Ele também define duas funções auxiliares essenciais: `formatCpfCnpj` para formatar números de CPF e CNPJ com máscaras adequadas, e `formatValor` para formatar valores monetários com duas casas decimais e separador de milhar.

### 2. Configuração do Arquivo CSV e Parâmetros

```groovy
//TIPO DE ARQUIVO//
arquivo = Arquivo.novo('imoveis' + Datas.formatar(Datas.hoje(), 'yyyy_MM_dd')+'.csv', 'csv', [encoding: 'UTF-8', delimitador: ";"]);

//PARÂMETROS//
p_ano = parametros.ano.valor
p_situacao = parametros.situacao?.selecionado?.valor
p_tipo = parametros.tipo?.selecionado?.valor

//VARIÁVEIS//
mapImoveis = [:]
listaFinal = []
filtroImoveis = []
filtroImoveisFinal = ''

//CABEÇALHO//
arquivo.escrever('CÓDIGO DO IMÓVEL');
arquivo.escrever('NOME DO RESPONSÁVEL');
arquivo.escrever('CPF/CNPJ DO RESPONSÁVEL');
arquivo.escrever('INSCRIÇÃO IMOBILIÁRIA');
arquivo.escrever('DISTRITO');
arquivo.escrever('SETOR');
arquivo.escrever('QUADRA');
arquivo.escrever('LOTE');
arquivo.escrever('BLOCO');
arquivo.escrever('UNIDADE');
arquivo.escrever('MATRICULA');
arquivo.escrever('CODIGO DO LOGRADOURO');
arquivo.escrever('TIPO DO LOGRADOURO');
arquivo.escrever('ENDERECO');
arquivo.escrever('MURADO');
arquivo.escrever('PASSEIO');
arquivo.escrever('AREA TOTAL CONSTRUIDA');
arquivo.escrever('TOTAL DE UNID. NO LOTE');
arquivo.escrever('AREA DO LOTE')
arquivo.escrever('ÁREA CONST. UNIDADE');
arquivo.escrever('VALOR VENAL DO TERRENO');
arquivo.escrever('VALOR VENAL DO PRÉDIO');
arquivo.escrever('VALOR IP');
arquivo.escrever('VALOR IT');
arquivo.novaLinha()
```

Neste bloco, o script define o nome e as configurações do arquivo CSV de saída, incluindo a codificação (`UTF-8`) e o delimitador (`;`). Ele também recupera os parâmetros de entrada (`p_ano`, `p_situacao`, `p_tipo`) e inicializa variáveis importantes como `mapImoveis` (um mapa para armazenar os dados dos imóveis) e `filtroImoveis`. Por fim, ele escreve o cabeçalho do arquivo CSV com todas as colunas que serão exportadas.

### 3. Busca Inicial de Imóveis e Preenchimento do Mapa

```groovy
if(p_situacao){
  filtroImoveis << "situacao = '${p_situacao}'"
}
if(p_tipo){
  filtroImoveis << "tipoImovel = '${p_tipo}'"
}

filtroImoveisFinal = filtroImoveis.join(' and ')

dadosImoveis = fonteImoveis.busca(criterio: filtroImoveisFinal, ordenacao: "codigo asc")

percorrer (dadosImoveis) { itemImoveis -> 
  mapImoveis[itemImoveis.id] = [
    codigoImovel: itemImoveis.codigo,
    responsavelNome: itemImoveis.responsavel.nome,
    responsavelcpfCnpj: formatCpfCnpj(itemImoveis.responsavel.cpfCnpj),
    inscricaoImobiliariaFormatada: itemImoveis.inscricaoImobiliariaFormatada,
    distritoNome: itemImoveis.distrito.nome,
    setor: itemImoveis.setor,
    quadra: itemImoveis.quadra,
    lote: itemImoveis.lote,
    bloco: itemImoveis.bloco,
    unidade: itemImoveis.unidade,
    matricula: itemImoveis.matricula,
    logradouroCodigo: itemImoveis.logradouro.codigo,
    logradouroTipoLogradouroDescricao: itemImoveis.logradouro.tipoLogradouroDescricao,
    enderecoFormatado: itemImoveis.enderecoFormatado,
    murado: '',
    passeio: '',
    areaTotalConstruida: '',
    totalUnid: '',
    areaDoLote: '',
    areaConstUnidade: '',
    valorVenalPredial: 0,
    valorVenalTerreno: 0,
    valorIP: 0,
    valorIT: 0,
  ]
}
```

Este bloco constrói o critério de busca para os imóveis com base nos parâmetros de situação e tipo. Em seguida, ele busca os imóveis na `fonteImoveis` e preenche o `mapImoveis` com as informações básicas de cada imóvel, utilizando o `id` do imóvel como chave. Campos como `murado`, `passeio`, `areaTotalConstruida` e valores venais são inicializados com valores padrão, que serão preenchidos posteriormente.

### 4. Enriquecimento de Dados: Receitas (IP/IT) e Campos Adicionais

```groovy
mapImoveis.keySet().collate(500).each{itemCollate ->
  fonteReceitas = Dados.tributos.v2.debitos.receitas;
  
  filtroReceitas = "debito.idImovel in (${itemCollate.join(',')}) and receita.abreviatura in ('IP', 'IT') and debito.ano = ${p_ano}"
  
  dadosReceitas = fonteReceitas.busca(criterio: filtroReceitas)
  
  percorrer (dadosReceitas) { itemReceitas ->
    if(itemReceitas.creditoReceita.receita.abreviatura == 'IP'){
      mapImoveis[itemReceitas.debito.idImovel].valorIP = itemReceitas.valor 
    }
    if(itemReceitas.creditoReceita.receita.abreviatura == 'IT'){
      mapImoveis[itemReceitas.debito.idImovel].valorIT = itemReceitas.valor 
    }
  }
  
  filtroCamposAdicionais = "idImovel in (${itemCollate.join(',')})"
  
  dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais,ordenacao: "ano desc")
  
  percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
    if(itemCamposAdicionais.campoAdicional.titulo == 'Murado'){
      mapImoveis[itemCamposAdicionais.idImovel].murado = itemCamposAdicionais.opcoes   
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Passeio'){
      mapImoveis[itemCamposAdicionais.idImovel].passeio =  itemCamposAdicionais.opcoes         
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Área Total Construída'){
      mapImoveis[itemCamposAdicionais.idImovel].areaTotalConstruida = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Total De Unid. No Lote'){
      mapImoveis[itemCamposAdicionais.idImovel].totalUnid = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Área Do Lote'){
      mapImoveis[itemCamposAdicionais.idImovel].areaDoLote = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Área Const. Unidade'){
      mapImoveis[itemCamposAdicionais.idImovel].areaConstUnidade = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Valor Venal Do Prédio'){
      mapImoveis[itemCamposAdicionais.idImovel].valorVenalPredial = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Valor Venal Do Terreno'){
      mapImoveis[itemCamposAdicionais.idImovel].valorVenalTerreno = itemCamposAdicionais.vlCampo
    }
  }
}
```

Este bloco é o coração do enriquecimento de dados. Ele itera sobre os IDs dos imóveis em lotes de 500 para otimizar as buscas. Para cada lote, ele realiza duas operações principais:

*   **Busca de Receitas (IP/IT)**: Busca receitas de IPTU (IP) e ITBI (IT) associadas aos imóveis do lote para o ano especificado (`p_ano`) e atualiza os campos `valorIP` e `valorIT` no `mapImoveis`.
*   **Busca de Campos Adicionais**: Busca campos adicionais para os imóveis do lote. Um conjunto de condicionais (`if`) é utilizado para mapear o `titulo` de cada campo adicional para a propriedade correspondente no `mapImoveis` (por exemplo, 


    "Murado", "Passeio", "Área Total Construída", etc.) e atribui o `vlCampo` ou `opcoes` correspondente.

### 5. Geração do Arquivo CSV

```groovy
mapImoveis.each{ key, value ->
  arquivo.escrever(value?.codigoImovel ?: "");  
  arquivo.escrever(value?.responsavelNome ?: "");
  arquivo.escrever(value?.responsavelcpfCnpj ?: "");
  arquivo.escrever(value?.inscricaoImobiliariaFormatada ?: "");
  arquivo.escrever(value?.distritoNome ?: "");
  arquivo.escrever(value?.setor ?: "");
  arquivo.escrever(value?.quadra ?: "");
  arquivo.escrever(value?.lote ?: "");
  arquivo.escrever(value?.bloco ?: "");
  arquivo.escrever(value?.unidade ?: "");
  arquivo.escrever(value?.matricula ?: "");
  arquivo.escrever(value?.logradouroCodigo ?: "");
  arquivo.escrever(value?.logradouroTipoLogradouroDescricao ?: "");
  arquivo.escrever(value?.enderecoFormatado ?: "");
  arquivo.escrever(value?.murado ?: "");
  arquivo.escrever(value?.passeio ?: "");
  arquivo.escrever(value.areaTotalConstruida ?: "");
  arquivo.escrever(value?.totalUnid ?: "");
  arquivo.escrever(value?.areaDoLote ?: "");
  arquivo.escrever(value?.areaConstUnidade ?: "");
  arquivo.escrever(value?.valorVenalTerreno ?: "");
  arquivo.escrever(value?.valorVenalPredial ?: "");
  arquivo.escrever(value?.valorIP ?: "");
  arquivo.escrever(value?.valorIT ?: "");
  arquivo.novaLinha()
  imprimir value
}
Resultado.arquivo(arquivo)
Resultado.nome("Pagamentos${Datas.formatar(Datas.hoje(), \'ddMMyyyyHHmmss\')}.zip")
```

Este bloco final itera sobre cada imóvel no `mapImoveis` (que agora contém todas as informações enriquecidas) e escreve os dados no arquivo CSV. Cada campo é escrito na ordem definida no cabeçalho, com tratamento para valores nulos (`?: ""`). Após escrever todos os dados, o script define o arquivo CSV como resultado para download e nomeia o arquivo ZIP de saída com um timestamp.

## Código Completo

```groovy
//FONTES//
fonteImoveis = Dados.tributos.v2.imoveis;
fonteDebitos = Dados.tributos.v2.debitos;
fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;

//FORMATAÇÃO DO CPF/CNPJ//
def String formatCpfCnpj(String cpfCnpj) {
  //cpfCnpj: String numeral, com tamanho 11 ou 14;
  if(cpfCnpj.trim().size() == 11) {
    return cpfCnpj.trim().take(11).replaceAll(/(\d{3})(\d{3})(\d{3})(\d{2})/) { match ->
      "${match[1]}.${match[2]}.${match[3]}-${match[4]}"
    }
  } else if (cpfCnpj.trim().size() == 14) {
    return cpfCnpj.trim().take(14).replaceAll(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/) { match ->
      "${match[1]}.${match[2]}.${match[3]}/${match[4]}-${match[5]}"
    }
  } else {
    return cpfCnpj;
  }
}

def String formatValor(BigDecimal valorInicial) {
  //valorInicial: BigDecimal com o valor a ser formatado
  def valor = String.format("%.2f", valorInicial).replace(".", ",")
  
  def partes = valor.split(",")
  def parteInteira = partes[0]
  def parteDecimal = partes[1]
  def parteInteiraInvertida = parteInteira.reverse()
  def parteInteiraComPontos = parteInteiraInvertida.replaceAll(/(\d{3})/, '$1.').reverse()
  
  if (parteInteiraComPontos.startsWith(".")) {
    parteInteiraComPontos = parteInteiraComPontos.substring(1)
  }
  
  def valorFormatado = "R\\$${parteInteiraComPontos},${parteDecimal}"
  return valorFormatado
}

//TIPO DE ARQUIVO//
arquivo = Arquivo.novo('imoveis' + Datas.formatar(Datas.hoje(), 'yyyy_MM_dd')+'.csv', 'csv', [encoding: 'UTF-8', delimitador: ";"]);

//PARÂMETROS//
p_ano = parametros.ano.valor
p_situacao = parametros.situacao?.selecionado?.valor
p_tipo = parametros.tipo?.selecionado?.valor

//VARIÁVEIS//
mapImoveis = [:]
listaFinal = []
filtroImoveis = []
filtroImoveisFinal = ''

//CABEÇALHO//
arquivo.escrever('CÓDIGO DO IMÓVEL');
arquivo.escrever('NOME DO RESPONSÁVEL');
arquivo.escrever('CPF/CNPJ DO RESPONSÁVEL');
arquivo.escrever('INSCRIÇÃO IMOBILIÁRIA');
arquivo.escrever('DISTRITO');
arquivo.escrever('SETOR');
arquivo.escrever('QUADRA');
arquivo.escrever('LOTE');
arquivo.escrever('BLOCO');
arquivo.escrever('UNIDADE');
arquivo.escrever('MATRICULA');
arquivo.escrever('CODIGO DO LOGRADOURO');
arquivo.escrever('TIPO DO LOGRADOURO');
arquivo.escrever('ENDERECO');
arquivo.escrever('MURADO');
arquivo.escrever('PASSEIO');
arquivo.escrever('AREA TOTAL CONSTRUIDA');
arquivo.escrever('TOTAL DE UNID. NO LOTE');
arquivo.escrever('AREA DO LOTE')
arquivo.escrever('ÁREA CONST. UNIDADE');
arquivo.escrever('VALOR VENAL DO TERRENO');
arquivo.escrever('VALOR VENAL DO PRÉDIO');
arquivo.escrever('VALOR IP');
arquivo.escrever('VALOR IT');
arquivo.novaLinha()

if(p_situacao){
  filtroImoveis << "situacao = \'${p_situacao}\'"
}
if(p_tipo){
  filtroImoveis << "tipoImovel = \'${p_tipo}\'"
}

filtroImoveisFinal = filtroImoveis.join(' and ')

dadosImoveis = fonteImoveis.busca(criterio: filtroImoveisFinal, ordenacao: "codigo asc")

percorrer (dadosImoveis) { itemImoveis -> 
  mapImoveis[itemImoveis.id] = [
    codigoImovel: itemImoveis.codigo,
    responsavelNome: itemImoveis.responsavel.nome,
    responsavelcpfCnpj: formatCpfCnpj(itemImoveis.responsavel.cpfCnpj),
    inscricaoImobiliariaFormatada: itemImoveis.inscricaoImobiliariaFormatada,
    distritoNome: itemImoveis.distrito.nome,
    setor: itemImoveis.setor,
    quadra: itemImoveis.quadra,
    lote: itemImoveis.lote,
    bloco: itemImoveis.bloco,
    unidade: itemImoveis.unidade,
    matricula: itemImoveis.matricula,
    logradouroCodigo: itemImoveis.logradouro.codigo,
    logradouroTipoLogradouroDescricao: itemImoveis.logradouro.tipoLogradouroDescricao,
    enderecoFormatado: itemImoveis.enderecoFormatado,
    murado: '',
    passeio: '',
    areaTotalConstruida: '',
    totalUnid: '',
    areaDoLote: '',
    areaConstUnidade: '',
    valorVenalPredial: 0,
    valorVenalTerreno: 0,
    valorIP: 0,
    valorIT: 0,
  ]
}

mapImoveis.keySet().collate(500).each{itemCollate ->
  fonteReceitas = Dados.tributos.v2.debitos.receitas;
  
  filtroReceitas = "debito.idImovel in (${itemCollate.join(',')}) and receita.abreviatura in ('IP', 'IT') and debito.ano = ${p_ano}"
  
  dadosReceitas = fonteReceitas.busca(criterio: filtroReceitas)
  
  percorrer (dadosReceitas) { itemReceitas ->
    if(itemReceitas.creditoReceita.receita.abreviatura == 'IP'){
      mapImoveis[itemReceitas.debito.idImovel].valorIP = itemReceitas.valor 
    }
    if(itemReceitas.creditoReceita.receita.abreviatura == 'IT'){
      mapImoveis[itemReceitas.debito.idImovel].valorIT = itemReceitas.valor 
    }
  }
  
  fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;
  
  filtroCamposAdicionais = "idImovel in (${itemCollate.join(',')})"
  
  dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais,ordenacao: "ano desc")
  
  percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
    if(itemCamposAdicionais.campoAdicional.titulo == 'Murado'){
      mapImoveis[itemCamposAdicionais.idImovel].murado = itemCamposAdicionais.opcoes   
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Passeio'){
      mapImoveis[itemCamposAdicionais.idImovel].passeio =  itemCamposAdicionais.opcoes         
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Área Total Construída'){
      mapImoveis[itemCamposAdicionais.idImovel].areaTotalConstruida = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Total De Unid. No Lote'){
      mapImoveis[itemCamposAdicionais.idImovel].totalUnid = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Área Do Lote'){
      mapImoveis[itemCamposAdicionais.idImovel].areaDoLote = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Área Const. Unidade'){
      mapImoveis[itemCamposAdicionais.idImovel].areaConstUnidade = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Valor Venal Do Prédio'){
      mapImoveis[itemCamposAdicionais.idImovel].valorVenalPredial = itemCamposAdicionais.vlCampo
    }
    if(itemCamposAdicionais.campoAdicional.titulo == 'Valor Venal Do Terreno'){
      mapImoveis[itemCamposAdicionais.idImovel].valorVenalTerreno = itemCamposAdicionais.vlCampo
    }
  }
}

mapImoveis.each{ key, value ->
  arquivo.escrever(value?.codigoImovel ?: "");  
  arquivo.escrever(value?.responsavelNome ?: "");
  arquivo.escrever(value?.responsavelcpfCnpj ?: "");
  arquivo.escrever(value?.inscricaoImobiliariaFormatada ?: "");
  arquivo.escrever(value?.distritoNome ?: "");
  arquivo.escrever(value?.setor ?: "");
  arquivo.escrever(value?.quadra ?: "");
  arquivo.escrever(value?.lote ?: "");
  arquivo.escrever(value?.bloco ?: "");
  arquivo.escrever(value?.unidade ?: "");
  arquivo.escrever(value?.matricula ?: "");
  arquivo.escrever(value?.logradouroCodigo ?: "");
  arquivo.escrever(value?.logradouroTipoLogradouroDescricao ?: "");
  arquivo.escrever(value?.enderecoFormatado ?: "");
  arquivo.escrever(value?.murado ?: "");
  arquivo.escrever(value?.passeio ?: "");
  arquivo.escrever(value.areaTotalConstruida ?: "");
  arquivo.escrever(value?.totalUnid ?: "");
  arquivo.escrever(value?.areaDoLote ?: "");
  arquivo.escrever(value?.areaConstUnidade ?: "");
  arquivo.escrever(value?.valorVenalTerreno ?: "");
  arquivo.escrever(value?.valorVenalPredial ?: "");
  arquivo.escrever(value?.valorIP ?: "");
  arquivo.escrever(value?.valorIT ?: "");
  arquivo.novaLinha()
  imprimir value
}
Resultado.arquivo(arquivo)
Resultado.nome("Pagamentos${Datas.formatar(Datas.hoje(), \'ddMMyyyyHHmmss\')}.zip")
```

