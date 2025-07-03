# 📄 Geração de Arquivo CSV com Filtro Específico no BFC-SCRIPT

Este exemplo demonstra como gerar um **arquivo `.csv` no Studio Extensões da Betha Sistemas** utilizando um **filtro customizado** para extrair dados de uma tabela auxiliar do módulo de tributos.

## 📅 Fonte de Dados Utilizada

A fonte principal é:

* `Dados.tributos.v2.tabelaAuxiliar.registros`: Retorna os registros de uma **tabela auxiliar** configurada no sistema.

O filtro aplicado restringe os resultados apenas para os registros com:

* `campo1 = '2024'`
* `campo5` iniciando com `"DESCONTO"`.

## 💡 Exemplo de Uso

```bfc-script
fonteRegistros = Dados.tributos.v2.tabelaAuxiliar.registros;

arquivo = Arquivo.novo('imoveis' + Datas.formatar(Datas.hoje(), 'yyyy_MM_dd')+'.csv', 'csv', [encoding: 'UTF-8', delimitador: ";"]);

filtroRegistros = "campo1 = '2024' and campo5 like 'DESCONTO%'"

dadosRegistros = fonteRegistros.busca(criterio: filtroRegistros, campos: "id, idTabelaAuxiliar, codigoTabelaAuxiliar, campo1, campo2, campo3, campo4, campo5, campo6, campo7, campo8, campo9, campo10", parametros: ["codigoTabelaAuxiliar": 2])

arquivo.escrever('Ano');
arquivo.escrever('Rubrica');
arquivo.escrever('DescricaoRubrica');
arquivo.escrever('PipoLancto');
arquivo.escrever('IdReceitaCloud');
arquivo.escrever('DescReceitaCloud');
arquivo.escrever('ContaContabilRubricas');

arquivo.novaLinha()

percorrer (dadosRegistros) { itemRegistros ->
    campo1  = itemRegistros.campo1;
    campo2  = itemRegistros.campo2;
    campo3  = itemRegistros.campo3;
    campo5  = itemRegistros.campo5;
    campo7  = itemRegistros.campo7;
    campo8  = itemRegistros.campo8;
    campo9  = itemRegistros.campo9;

    arquivo.escrever(campo1);
    arquivo.escrever('');
    arquivo.escrever(campo3);
    arquivo.escrever(campo5);
    arquivo.escrever(campo7);
    arquivo.escrever(campo8);
    arquivo.escrever(campo9);

    arquivo.novaLinha()
}

Resultado.arquivo(arquivo)
Resultado.nome("Pagamentos${Datas.formatar(Datas.hoje(), 'ddMMyyyyHHmmss')}.zip")
```

## 📌 Explicação do Código

1. **Inicialização da Fonte de Dados**
   A fonte `tabelaAuxiliar.registros` é consultada com filtro específico sobre os campos `campo1` e `campo5`.

2. **Criação do Arquivo CSV**
   O arquivo é nomeado com a data do dia, possui codificação UTF-8 e usa ponto e vírgula (`;`) como delimitador.

3. **Cabeçalho do CSV**
   São definidos sete campos no cabeçalho, representando os dados que serão extraídos da tabela.

4. **Processamento dos Dados**
   Cada item retornado da busca passa pelo `percorrer`, onde os campos de interesse são extraídos.

5. **Escrita das Linhas**
   Para cada registro, é feita a escrita de uma linha no CSV com os dados formatados, inclusive com um campo em branco (posição da rubrica).

6. **Geração do Resultado**
   O arquivo é compactado automaticamente e renomeado com timestamp para facilitar identificação e versionamento.

## 📦 Resultado Esperado

Um arquivo `.csv` contendo os registros da tabela auxiliar com filtros específicos, estruturado com os seguintes campos:

```
Ano;Rubrica;DescricaoRubrica;PipoLancto;IdReceitaCloud;DescReceitaCloud;ContaContabilRubricas
```

## ✅ Conclusão

Este script exemplifica uma forma direta e eficiente de gerar arquivos `.csv` no Studio Extensões da Betha Sistemas com uso de **filtros**, **formatação customizada** e **exportação compactada**. Essa prática é muito úcil para relatórios que precisam ser extraídos e compartilhados externamente, como planilhas de controle, prestação de contas ou análises fiscais. 🚀
