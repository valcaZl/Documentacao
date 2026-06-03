# Documentação do Script: Relatório de Imóveis por Metragem

Este documento detalha o script responsável por gerar um relatório de imóveis, filtrando-os com base em sua metragem (um campo adicional numérico). O script permite dois modos de filtragem: por um intervalo (`ENTRE`) ou acima de um valor mínimo (`ACIMA`). O resultado é um arquivo CSV contendo informações dos imóveis que atendem aos critérios.

## Funcionalidades Principais

- **Filtragem Flexível**: Permite filtrar imóveis por metragem em um intervalo definido ou acima de um valor específico.
- **Geração de CSV**: Exporta os dados dos imóveis filtrados para um arquivo CSV, facilitando a análise e o compartilhamento.
- **Busca Otimizada**: Realiza a busca de campos adicionais em lotes para otimizar o desempenho.

## Parâmetros

Os seguintes parâmetros são utilizados para configurar a execução do script:

| Parâmetro         | Descrição                                                              | Valores Possíveis             | Obrigatório | Usado em                               |
| :---------------- | :--------------------------------------------------------------------- | :---------------------------- | :---------- | :------------------------------------- |
| `tipoFiltro`      | Define o modo de filtragem da metragem.                                | `ENTRE`, `ACIMA`              | Sim         | Lógica de filtragem por metragem       |
| `nomeCampo`       | Nome do campo adicional que contém a metragem do imóvel (ex: "Área Total Construída"). | String (ex: "Área Total Construída") | Sim         | Busca de campos adicionais             |
| `metMin`          | Valor mínimo da metragem para o filtro.                                | Numérico                      | Sim         | Lógica de filtragem por metragem       |
| `metMax`          | Valor máximo da metragem. Usado apenas quando `tipoFiltro` é `ENTRE`. | Numérico (ou `null`)          | Não         | Lógica de filtragem por metragem (`ENTRE`) |
| `situacao`        | Define quais situações de imóveis devem ser consideradas.              | `ATIVADO`, `DESATIVADO`, `AMBOS` | Sim         | Filtragem inicial de imóveis           |

## Estrutura do Script

### 1. Definição de Parâmetros

O script inicia recuperando os valores dos parâmetros de entrada:

```groovy
tipoFiltro = parametros.tipoFiltro.selecionado.valor;
nomeCampo = parametros.nomeCampo.valor;
metMin = parametros.metMin.valor ?: 0;
metMax = parametros.metMax.valor ?: null;
sit = parametros.situacao.selecionado.valor;
```

### 2. Inicialização do Arquivo CSV

Um novo arquivo CSV é criado com um nome baseado na data atual e codificação UTF-8, utilizando `;` como delimitador.

```groovy
arquivo = Arquivo.novo('imoveis_metragem_' + Datas.formatar(Datas.hoje(), 'yyyy_MM_dd') + '.csv', 'csv', [encoding: 'UTF-8', delimitador: ";"]);
```

### 3. Definição do Cabeçalho do CSV

As colunas do arquivo CSV são definidas:

```groovy
arquivo.escrever('CÓDIGO DO IMÓVEL');
arquivo.escrever('INSCRIÇÃO IMOBILIÁRIA');
arquivo.escrever('NOME DO RESPONSÁVEL');
arquivo.escrever('CPF/CNPJ DO RESPONSÁVEL');
arquivo.escrever('ENDEREÇO');
arquivo.escrever('METRAGEM (m²)');
arquivo.novaLinha();
```

### 4. Filtragem de Imóveis por Situação

É construído um critério de filtro para buscar imóveis com base na sua situação (`ATIVADO`, `DESATIVADO` ou `AMBOS`).

```groovy
filtroImoveis = "";
se(sit == "AMBOS"){
  filtroImoveis = "situacao in('ATIVADO','DESATIVADO','DESMEMBRADO','REMEMBRADO')";
}senao{
  filtroImoveis = "situacao = '${sit}'";
}
```

### 5. Busca e Mapeamento de Dados de Imóveis

Os imóveis são buscados utilizando o filtro de situação e ordenados por código. Os dados relevantes de cada imóvel são armazenados em um mapa (`mapImoveis`).

```groovy
fonteImoveis = Dados.tributos.v2.imoveis;
dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis, ordenacao: "codigo asc");

mapImoveis = [:];
percorrer(dadosImoveis){ item ->
  mapImoveis[item.id] = [
    codigo: item.codigo,
    inscricao: item.inscricaoImobiliariaFormatada,
    responsavelNome: item.responsavel.nome,
    responsavelCpfCnpj: item.responsavel.cpfCnpj,
    endereco: item.enderecoFormatado,
    metragem: (BigDecimal) 0
  ];
}
```

### 6. Busca de Campos Adicionais (Metragem) em Lotes

Para otimizar a busca, os campos adicionais são recuperados em lotes de 500 imóveis. A metragem correspondente é então atualizada no `mapImoveis`.

```groovy
fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;

mapImoveis.keySet().collate(500).each{ lote ->
  filtroCampos = "idImovel in(${lote.join(',')})";
  dadosCampos = fonteCamposAdicionais.busca(criterio: filtroCampos);
  percorrer(dadosCampos){ campo ->
    se(campo.campoAdicional.titulo == nomeCampo){
      vlCampo = campo.vlCampo ?: 0;
      mapImoveis[campo.idImovel].metragem = vlCampo;
    }
  }
}
```

### 7. Filtragem Final por Metragem e Geração do CSV

Cada imóvel no `mapImoveis` é verificado em relação aos critérios de metragem (`ENTRE` ou `ACIMA`). Se o imóvel atender aos critérios, seus dados são escritos no arquivo CSV.

```groovy
contador = 0;
mapImoveis.each{ id, dados ->
  met = dados.metragem ?: 0;
  incluir = falso;
  
  se(tipoFiltro == "ENTRE"){
    se(metMax != null){
      incluir = (met >= metMin && met <= metMax);
    }senao{
      incluir = (met >= metMin);
    }
  }senao{
    // ACIMA
    incluir = (met > metMin);
  }
  
  se(incluir){
    contador++;
    arquivo.escrever(dados?.codigo ?: "");
    arquivo.escrever(dados?.inscricao ?: "");
    arquivo.escrever(dados?.responsavelNome ?: "");
    arquivo.escrever(dados?.responsavelCpfCnpj ?: "");
    arquivo.escrever(dados?.endereco ?: "");
    arquivo.escrever(met ?: "");
    arquivo.novaLinha();
  }
}
```

### 8. Saída do Script

Ao final, o script imprime o total de imóveis encontrados e retorna o arquivo CSV gerado, com um nome de arquivo ZIP formatado.

```groovy
imprimir "Total de imóveis encontrados: ${contador}";

Resultado.arquivo(arquivo);
Resultado.nome("ImovelMetragem${Datas.formatar(Datas.hoje(), 'ddMMyyyyHHmmss')}.zip");
```

## Código Completo

```groovy
// ========================================================
// RELATÓRIO: Imóveis - Filtro por Metragem
// Filtra imóveis por metragem (campo adicional numérico)
// Modos: ENTRE (de X até Y m²) ou ACIMA (acima de X m²)
// ========================================================

// --- PARÂMETROS ---
// tipoFiltro: ENTRE ou ACIMA
// nomeCampo: nome do campo adicional de metragem (ex: "Área Total Construída")
// metMin: valor mínimo de metragem (obrigatório)
// metMax: valor máximo de metragem (usado somente no modo ENTRE)
// situacao: ATIVADO, DESATIVADO ou AMBOS

tipoFiltro = parametros.tipoFiltro.selecionado.valor;
nomeCampo = parametros.nomeCampo.valor;
metMin = parametros.metMin.valor ?: 0;
metMax = parametros.metMax.valor ?: null;
sit = parametros.situacao.selecionado.valor;

// --- ARQUIVO CSV ---
arquivo = Arquivo.novo('imoveis_metragem_' + Datas.formatar(Datas.hoje(), 'yyyy_MM_dd') + '.csv', 'csv', [encoding: 'UTF-8', delimitador: ";"]);

// --- CABEÇALHO DO CSV ---
arquivo.escrever('CÓDIGO DO IMÓVEL');
arquivo.escrever('INSCRIÇÃO IMOBILIÁRIA');
arquivo.escrever('NOME DO RESPONSÁVEL');
arquivo.escrever('CPF/CNPJ DO RESPONSÁVEL');
arquivo.escrever('ENDEREÇO');
arquivo.escrever('METRAGEM (m²)');
arquivo.novaLinha();

// --- FILTRO DE SITUAÇÃO ---
filtroImoveis = "";
se(sit == "AMBOS"){
  filtroImoveis = "situacao in('ATIVADO','DESATIVADO','DESMEMBRADO','REMEMBRADO')";
}senao{
  filtroImoveis = "situacao = '${sit}'";
}

// --- BUSCA DE IMÓVEIS ---
fonteImoveis = Dados.tributos.v2.imoveis;
dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis, ordenacao: "codigo asc");

mapImoveis = [:];
percorrer(dadosImoveis){ item ->
  mapImoveis[item.id] = [
    codigo: item.codigo,
    inscricao: item.inscricaoImobiliariaFormatada,
    responsavelNome: item.responsavel.nome,
    responsavelCpfCnpj: item.responsavel.cpfCnpj,
    endereco: item.enderecoFormatado,
    metragem: (BigDecimal) 0
  ];
}

// --- BUSCA DE CAMPOS ADICIONAIS EM LOTES ---
fonteCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais;

mapImoveis.keySet().collate(500).each{ lote ->
  filtroCampos = "idImovel in(${lote.join(',')})";
  dadosCampos = fonteCamposAdicionais.busca(criterio: filtroCampos);
  percorrer(dadosCampos){ campo ->
    se(campo.campoAdicional.titulo == nomeCampo){
      vlCampo = campo.vlCampo ?: 0;
      mapImoveis[campo.idImovel].metragem = vlCampo;
    }
  }
}

// --- FILTRO POR METRAGEM E GERAÇÃO DO CSV ---
contador = 0;
mapImoveis.each{ id, dados ->
  met = dados.metragem ?: 0;
  incluir = falso;
  
  se(tipoFiltro == "ENTRE"){
    se(metMax != null){
      incluir = (met >= metMin && met <= metMax);
    }senao{
      incluir = (met >= metMin);
    }
  }senao{
    // ACIMA
    incluir = (met > metMin);
  }
  
  se(incluir){
    contador++;
    arquivo.escrever(dados?.codigo ?: "");
    arquivo.escrever(dados?.inscricao ?: "");
    arquivo.escrever(dados?.responsavelNome ?: "");
    arquivo.escrever(dados?.responsavelCpfCnpj ?: "");
    arquivo.escrever(dados?.endereco ?: "");
    arquivo.escrever(met ?: "");
    arquivo.novaLinha();
  }
}

imprimir "Total de imóveis encontrados: ${contador}";

Resultado.arquivo(arquivo);
Resultado.nome("ImovelMetragem${Datas.formatar(Datas.hoje(), 'ddMMyyyyHHmmss')}.zip");
```
```
