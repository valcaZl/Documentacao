# Documentação do Script de Processamento de Débitos e Campos Adicionais

Este script Groovy é projetado para processar débitos e campos adicionais de imóveis, consolidando essas informações em um formato estruturado para posterior utilização. Ele busca dados de débitos e campos adicionais, associa-os aos imóveis correspondentes e, em seguida, insere os dados enriquecidos em uma fonte de dados dinâmica.

## Explicação Geral do Código

O script começa definindo um esquema para a fonte de dados dinâmica de saída. Em seguida, ele busca débitos e campos adicionais de imóveis, utilizando um `map` para armazenar e enriquecer os dados dos imóveis. Os débitos são associados aos imóveis com base no `idImovel`, e os campos adicionais são mapeados para propriedades específicas do imóvel. Finalmente, os dados processados são inseridos na fonte de dados dinâmica.

## Blocos de Código

### 1. Definição do Esquema e Inicialização da Fonte de Dados

```groovy
esquema = [
  codigoImovel: Esquema.numero,
  responsavelNome: Esquema.caracter,
  responsavelcpfCnpj: Esquema.caracter,
  valorTerreno: Esquema.numero,
  valorVenalTerritorial: Esquema.numero,
  valorEdificacao: Esquema.numero,
  valorVenalPredial: Esquema.numero,
  valorVenalImovel: Esquema.numero,
  valorIptu: Esquema.numero
]

fonte = Dados.dinamico.v2.novo(esquema);
```

Este bloco define a estrutura dos dados que serão manipulados e gerados pelo script. O `esquema` especifica os campos e seus tipos (número, caractere) para a fonte de dados dinâmica. A `fonte` é então inicializada como uma nova fonte de dados dinâmica com base nesse esquema, pronta para receber os dados processados.

### 2. Função de Formatação de CPF/CNPJ

```groovy
def String formatCpfCnpj(String cpfCnpj) {
  if(cpfCnpj.trim().size() == 11) {
    return cpfCnpj.trim().take(11).replaceAll(/(\d{3})(\d{3})(\d{3})(\d{2})/) { match ->
      "${match[1]}.${match[2]}.${match[3]}-${match[4]}"
    }
  } else if (cpfCnpj.trim().size() == 14) {
    return cpfCnpj.trim().take(14).replaceAll(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/) { match ->
      "${match[1]}.${match[2]}.${match[3]}/${match[4]}-${match[5]}"
    }
  } else {
    return cpfCpf;
  }
}
```

Esta função auxiliar `formatCpfCnpj` é utilizada para padronizar a exibição de números de CPF (11 dígitos) e CNPJ (14 dígitos), aplicando máscaras de formatação. Caso o `cpfCnpj` não se encaixe em nenhum dos padrões, ele é retornado sem formatação.

### 3. Busca de Imóveis e Inicialização do Mapa

```groovy
linha = []

fonteImoveis = Dados.tributos.v2.imoveis;

filtroImoveis = "situacao = 'ATIVADO'"

dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis).take(250)

mapImoveis = [:]

percorrer (dadosImoveis) { itemImoveis -> 
  mapImoveis[itemImoveis.id] = [
    codigoImovel: itemImoveis.codigo,
    responsavelNome: itemImoveis.responsavel.nome,
    responsavelcpfCnpj: formatCpfCnpj(itemImoveis.responsavel.cpfCnpj),
    valorTerreno: 0,
    valorVenalTerritorial: 0,
    valorEdificacao: 0,
    valorVenalPredial: 0,
    valorVenalImovel: 0,
    valorIptu: 0
  ]
}
```

Este bloco busca até 250 imóveis com a situação 'ATIVADO' na fonte de dados `Dados.tributos.v2.imoveis`. Para cada imóvel encontrado, um novo registro é criado no `mapImoveis`, utilizando o `id` do imóvel como chave. Os campos `codigoImovel`, `responsavelNome` e `responsavelcpfCnpj` são preenchidos com os dados do imóvel, e os campos de valor são inicializados com zero, aguardando o enriquecimento posterior.

### 4. Enriquecimento de Dados: Débitos de IPTU e Campos Adicionais

```groovy
mapImoveis.keySet().collate(500).each{itemCollate ->
  
  fonteDebitos = Dados.tributos.v2.debitos;
  
  filtroDebitos = "idImovel in (${itemCollate.join(",")}) and abreviaturaCredito = 'IPTU' and ano = 2025 and nroParcela = 0"
  
  dadosDebitos = fonteDebitos.busca(criterio: filtroDebitos)
  
  percorrer (dadosDebitos) { itemDebitos ->
    mapImoveis[itemDebitos.idImovel].valorIptu = itemDebitos.vlLancado - itemDebitos.vlDesconto
  }
  
  fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;
  
  filtroCamposAdicionais = "idImovel in (${itemCollate.join(",")})"
  
  dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais, ordenaca: "ano desc")
  
  percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
    switch(itemCamposAdicionais.campoAdicional.titulo){
      case "Valor - m2 Terreno:": mapImoveis[itemCamposAdicionais.idImovel].valorTerreno = itemCamposAdicionais.vlCampo
      break
      case "Valor Venal - Territorial:": mapImoveis[itemCamposAdicionais.idImovel].valorVenalTerritorial = itemCamposAdicionais.vlCampo
      break
      case "Valor - m2 Edificação:": mapImoveis[itemCamposAdicionais.idImovel].valorEdificacao = itemCamposAdicionais.vlCampo
      break
      case "Valor - Imposto Predial:": mapImoveis[itemCamposAdicionais.idImovel].valorVenalPredial = itemCamposAdicionais.vlCampo
      break
      case "Valor Venal - Imóvel:": mapImoveis[itemCamposAdicionais.idImovel].valorVenalImovel = itemCamposAdicionais.vlCampo
      break
    }
  }
}
```

Este bloco é responsável por enriquecer os dados dos imóveis no `mapImoveis`. Ele itera sobre os IDs dos imóveis em lotes de 500 para otimizar as buscas. Para cada lote, ele realiza duas operações:

*   **Busca de Débitos de IPTU**: Busca débitos de IPTU (para o ano de 2025 e parcela 0) associados aos imóveis do lote e atualiza o `valorIptu` no `mapImoveis` com o valor líquido do débito.
*   **Busca de Campos Adicionais**: Busca campos adicionais para os imóveis do lote. Um `switch` case é utilizado para mapear o `titulo` de cada campo adicional para a propriedade correspondente no `mapImoveis` (por exemplo, 


    "Valor - m2 Terreno:", "Valor Venal - Territorial:", etc.) e atribui o `vlCampo` correspondente.

### 5. Inserção dos Dados na Fonte Dinâmica

```groovy
mapImoveis.each{ key, value ->
  fonte.inserir(value)
}
```

Este bloco final itera sobre cada entrada no `mapImoveis` (que agora contém os dados básicos do imóvel, os valores de IPTU e os campos adicionais) e insere cada objeto diretamente na `fonte` de dados dinâmica. Isso consolida todas as informações processadas em uma única estrutura de dados acessível.

## Código Completo

```groovy
esquema = [
  codigoImovel: Esquema.numero,
  responsavelNome: Esquema.caracter,
  responsavelcpfCnpj: Esquema.caracter,
  valorTerreno: Esquema.numero,
  valorVenalTerritorial: Esquema.numero,
  valorEdificacao: Esquema.numero,
  valorVenalPredial: Esquema.numero,
  valorVenalImovel: Esquema.numero,
  valorIptu: Esquema.numero
]

fonte = Dados.dinamico.v2.novo(esquema);

def String formatCpfCnpj(String cpfCnpj) {
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

linha = []

fonteImoveis = Dados.tributos.v2.imoveis;

filtroImoveis = "situacao = 'ATIVADO'"

dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis).take(250)

mapImoveis = [:]

percorrer (dadosImoveis) { itemImoveis -> 
  mapImoveis[itemImoveis.id] = [
    codigoImovel: itemImoveis.codigo,
    responsavelNome: itemImoveis.responsavel.nome,
    responsavelcpfCnpj: formatCpfCnpj(itemImoveis.responsavel.cpfCnpj),
    valorTerreno: 0,
    valorVenalTerritorial: 0,
    valorEdificacao: 0,
    valorVenalPredial: 0,
    valorVenalImovel: 0,
    valorIptu: 0
  ]
}

mapImoveis.keySet().collate(500).each{itemCollate ->
  
  fonteDebitos = Dados.tributos.v2.debitos;
  
  filtroDebitos = "idImovel in (${itemCollate.join(',')}) and abreviaturaCredito = 'IPTU' and ano = 2025 and nroParcela = 0"
  
  dadosDebitos = fonteDebitos.busca(criterio: filtroDebitos)
  
  percorrer (dadosDebitos) { itemDebitos ->
    mapImoveis[itemDebitos.idImovel].valorIptu = itemDebitos.vlLancado - itemDebitos.vlDesconto
  }
  
  fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;
  
  filtroCamposAdicionais = "idImovel in (${itemCollate.join(',')})"
  
  dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais, ordenaca: "ano desc")
  
  percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
    switch(itemCamposAdicionais.campoAdicional.titulo){
      case "Valor - m2 Terreno:": mapImoveis[itemCamposAdicionais.idImovel].valorTerreno = itemCamposAdicionais.vlCampo
      break
      case "Valor Venal - Territorial:": mapImoveis[itemCamposAdicionais.idImovel].valorVenalTerritorial = itemCamposAdicionais.vlCampo
      break
      case "Valor - m2 Edificação:": mapImoveis[itemCamposAdicionais.idImovel].valorEdificacao = itemCamposAdicionais.vlCampo
      break
      case "Valor - Imposto Predial:": mapImoveis[itemCamposAdicionais.idImovel].valorVenalPredial = itemCamposAdicionais.vlCampo
      break
      case "Valor Venal - Imóvel:": mapImoveis[itemCamposAdicionais.idImovel].valorVenalImovel = itemCamposAdicionais.vlCampo
      break
    }
  }
}

mapImoveis.each{key, value ->
  imprimir value
  fonte.inserirLinha(value)
}

retornar fonte
```