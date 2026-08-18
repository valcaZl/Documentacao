# Documentação do Script de Extração do Leiaute de Cadastro Imobiliário (ITBI)

Este script BFC-Script é responsável por gerar um arquivo CSV no leiaute de **Cadastro Imobiliário**, consolidando dados de imóveis que tiveram uma transferência (ITBI) registrada em um período informado. O script cruza dados de documentos, certidões de ITBI, imóveis, obras e habite-se, além de campos adicionais cadastrados no sistema, para montar uma linha completa por imóvel.

## Explicação Geral do Código

O script inicia criando o arquivo de saída (`leiauteCadastroImobiliario.csv`) e definindo as fontes de dados que serão utilizadas (`documentos`, `certidaoITBI`, `imoveis`, `obras`, `habitese` e `camposAdicionais`). Em seguida, escreve o cabeçalho do CSV com todos os campos exigidos pelo leiaute.

O fluxo principal parte da busca de **documentos de transferência de imóveis** (`tipoReferente = 'TRANSFERENCIA_IMOVEIS'`) emitidos dentro do intervalo de datas informado nos parâmetros (`dataInicial` e `dataFinal`). Para cada documento encontrado, o script busca a **certidão de ITBI** correspondente e, a partir dela, os **imóveis vinculados** àquela certidão.

Como um mesmo imóvel pode aparecer em mais de uma certidão/documento, o script mantém uma lista de controle (`imoveisProcessados`) para garantir que cada imóvel seja processado **apenas uma vez** no arquivo final.

Para cada imóvel não processado, o script:
1. Busca os dados cadastrais completos do imóvel;
2. Verifica se existe uma **obra vinculada** ao imóvel e, em caso positivo, busca o **habite-se** dessa obra, preenchendo a data de emissão somente quando ela existir;
3. Busca os **campos adicionais** do imóvel (área do terreno, área construída, valor venal e tipo de edificação);
4. Escreve uma linha no CSV com todas as informações coletadas.

Ao final, o arquivo é retornado como resultado do script.

## Parâmetros de Entrada

| Nome | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `dataInicial` | Data | Sim | Data inicial do período de emissão dos documentos de transferência a serem considerados. |
| `dataFinal` | Data | Sim | Data final do período de emissão dos documentos de transferência a serem considerados. |

## Blocos de Código

### 1. Criação do Arquivo e Definição das Fontes

```groovy
arquivo = Arquivo.novo('leiauteCadastroImobiliario.csv', 'csv', [encoding: 'UTF-8', delimitador: ";"]);

fonteDocumentos = Dados.tributos.v2.documentos;
fonteCertidaoITBI = Dados.tributos.v2.certidaoITBI;
fonteImoveisITBI = Dados.tributos.v2.certidaoITBI.imoveis;
fonteImoveis = Dados.tributos.v2.imoveis;
fonteObras = Dados.tributos.v2.obras;
fonteHabitese = Dados.tributos.v2.obra.habitese;
fonteCamposAdicionais = Dados.tributos.v2.imovel.camposAdicionais;

p_dataInicial = parametros.dataInicial.valor
p_dataFinal = parametros.dataFinal.valor
```

Este bloco cria o arquivo CSV de saída, com codificação `UTF-8` e `;` como delimitador, e inicializa todas as fontes de dados que serão utilizadas ao longo do script: documentos, certidão de ITBI, imóveis vinculados à certidão de ITBI, imóveis, obras, habite-se e campos adicionais. Também recupera os parâmetros de data informados pelo usuário (`dataInicial` e `dataFinal`).

### 2. Cabeçalho do Arquivo

```groovy
arquivo.escrever('Nome do Proprietario');
arquivo.escrever('CPF/CNPJ do Proprietario');
arquivo.escrever('Nome do Corresponsavel');
arquivo.escrever('CPF/CNPJ do Corresponsavel');
arquivo.escrever('Matricula do Imovel no Registro de Imoveis');
arquivo.escrever('Codigo Nacional de Matricula do Imovel (CNM)');
arquivo.escrever('Inscricao Imobiliaria');
arquivo.escrever('Imovel Rural ou Urbano (R/U)');
arquivo.escrever('Tipo do Imovel (casa, apartamento, etc)');
arquivo.escrever('Tipo Logradouro');
arquivo.escrever('Nome Logradouro');
arquivo.escrever('Complemento');
arquivo.escrever('Numero do Imovel');
arquivo.escrever('Bairro');
arquivo.escrever('Municipio');
arquivo.escrever('CEP');
arquivo.escrever('Coordenada X');
arquivo.escrever('Coordenada Y');
arquivo.escrever('Area (m2) do Terreno / Fracao Tradicional');
arquivo.escrever('Area (m2) Construcao');
arquivo.escrever('Valor de mercado do imovel');
arquivo.escrever('Data do Habite-se');
arquivo.escrever('Informacao Adicional');
arquivo.escrever('Versao do Leiaute');
arquivo.novaLinha()
```

Escreve a linha de cabeçalho do CSV, com todas as 23 colunas exigidas pelo leiaute de Cadastro Imobiliário, na ordem em que os dados serão gravados posteriormente.

### 3. Busca dos Documentos de Transferência (ITBI)

```groovy
filtroDocumentos = "tipoReferente = 'TRANSFERENCIA_IMOVEIS' and dtEmissao > ${p_dataInicial.format("yyyy-MM-dd")} and dtEmissao < ${p_dataFinal.format("yyyy-MM-dd")} and nroDocumento >= 1"

dadosDocumentos = fonteDocumentos.busca(criterio: filtroDocumentos)

imoveisProcessados = []
```

Monta o filtro para buscar somente documentos do tipo `TRANSFERENCIA_IMOVEIS` (ITBI) cuja data de emissão esteja dentro do intervalo informado pelo usuário, e com número de documento válido (`>= 1`). A lista `imoveisProcessados` é inicializada vazia e será usada como controle de deduplicação de imóveis ao longo do processamento.

### 4. Percorrer Documentos → Certidão de ITBI → Imóveis Vinculados

```groovy
percorrer (dadosDocumentos) { itemDocumentos ->
  
  dadosCertidaoITBI = fonteCertidaoITBI.busca(parametros:["ano":itemDocumentos.anoDocumento,"nroDocumento":itemDocumentos.nroDocumento])
  
  percorrer (dadosCertidaoITBI) { itemCertidaoITBI ->
    
    dadosImoveisITBI = fonteImoveisITBI.busca(parametros:["ano":itemDocumentos.anoDocumento,"nroDocumento":itemDocumentos.nroDocumento])
    
    percorrer (dadosImoveisITBI) { itemImoveisITBI ->
      
      se (!imoveisProcessados.contains(itemImoveisITBI.idImovel)) {
        
        imoveisProcessados.add(itemImoveisITBI.idImovel)
        ...
```

Para cada documento de transferência, o script busca a certidão de ITBI correspondente (usando ano e número do documento). A partir da certidão, busca os imóveis vinculados a ela. Antes de processar um imóvel, o script verifica se o seu `idImovel` já está na lista `imoveisProcessados`; caso já esteja, o imóvel é ignorado, evitando que o mesmo imóvel seja gravado mais de uma vez no CSV caso apareça em várias certidões/documentos.

### 5. Busca dos Dados Cadastrais do Imóvel e Reinicialização das Variáveis

```groovy
filtroImoveis = "id = ${itemImoveisITBI.idImovel}"

dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis)

percorrer (dadosImoveis) { itemImoveis ->
  
  // Reinicializa as variaveis para CADA imovel, evitando herdar valores do imovel anterior
  areaDoTerreno = 0
  areaConstruida = 0
  valorVenal = 0
  tipoEdificacao = ''
  dtEmissao = "Não há habite-se no sistema para este imóvel"
```

Busca o cadastro completo do imóvel pelo seu `id`. As variáveis de área, valor venal, tipo de edificação e data de habite-se são reinicializadas a cada iteração, garantindo que valores de um imóvel não sejam indevidamente herdados pelo próximo. Por padrão, a data de habite-se recebe o texto `"Não há habite-se no sistema para este imóvel"`, que só é sobrescrito caso um habite-se emitido seja encontrado.

### 6. Validação da Obra e do Habite-se

```groovy
filtroObras = "imovel.id = ${itemImoveis.id}"

dadosObras = fonteObras.busca(criterio: filtroObras)

percorrer (dadosObras) { itemObras ->
  
  dadosHabitese = fonteHabitese.busca(parametros:["idObra":itemObras.id])
  
  percorrer (dadosHabitese) { itemHabitese ->
    se (itemHabitese.dtEmissao != null) {
      imprimir 'Imovel ' + itemImoveis.id + ' - Obra ' + itemObras.codigo + ' - Habite-se emitido em ' + itemHabitese.dtEmissao
      dtEmissao = itemHabitese.dtEmissao.format('dd/MM/yyyy')
    }
  }
}
```

Busca as obras vinculadas ao imóvel. Para cada obra, busca o(s) habite-se relacionado(s) e, somente quando a data de emissão (`dtEmissao`) não for nula, atualiza a variável `dtEmissao` com a data formatada (`dd/MM/yyyy`) e imprime uma mensagem de log informando o imóvel, a obra e a data do habite-se emitido. Caso não exista obra ou não exista habite-se emitido, a variável mantém o valor padrão definido no bloco anterior.

### 7. Busca dos Campos Adicionais do Imóvel

```groovy
dadosCamposAdicionais = fonteCamposAdicionais.busca(parametros:["idImovel":itemImoveis.id], criterio: "campoAdicional.titulo = 'ÁREA DO TERRENO'")

percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
  switch(itemCamposAdicionais.campoAdicional.titulo){
    case "ÁREA DO TERRENO": areaDoTerreno = itemCamposAdicionais.vlCampo
    break
    case "ÁREA TOTAL CONSTRUÍDA": areaConstruida = itemCamposAdicionais.vlCampo
    break
    case "VALOR VENAL DO IMOVEL": valorVenal = itemCamposAdicionais.vlCampo
    break
    case "TIPO DE EDIFICACAO": tipoEdificacao = itemCamposAdicionais.opcoes
    break
  }
}
```

Busca os campos adicionais cadastrados para o imóvel e, através de um `switch`, distribui o valor de cada campo adicional encontrado (`ÁREA DO TERRENO`, `ÁREA TOTAL CONSTRUÍDA`, `VALOR VENAL DO IMOVEL` e `TIPO DE EDIFICACAO`) para a respectiva variável que será escrita no CSV.

> ⚠️ O critério de busca (`criterio`) está filtrando apenas pelo campo `'ÁREA DO TERRENO'`. Vale revisar se o filtro deveria contemplar os demais títulos usados no `switch`, para garantir que os campos `ÁREA TOTAL CONSTRUÍDA`, `VALOR VENAL DO IMOVEL` e `TIPO DE EDIFICACAO` também sejam retornados pela busca.

### 8. Escrita da Linha no Arquivo CSV

```groovy
arquivo.escrever(itemImoveis.responsavel.nome);
arquivo.escrever(itemImoveis.responsavel.cpfCnpj);
arquivo.escrever(itemImoveis.corresponsavel.nome);
arquivo.escrever(itemImoveis.corresponsavel.cpfCnpj);
arquivo.escrever(itemImoveis.matricula);
arquivo.escrever(itemImoveis.codigo);
arquivo.escrever(itemImoveis.inscricaoImobiliariaFormatada);
arquivo.escrever(itemImoveis.tipoImovel.valor);
arquivo.escrever(tipoEdificacao);
arquivo.escrever(itemImoveis.logradouro.tipoLogradouroDescricao);
arquivo.escrever(itemImoveis.logradouro.nome);
arquivo.escrever(itemImoveis.complemento);
arquivo.escrever(itemImoveis.numero);
arquivo.escrever(itemImoveis.bairro.nome);
arquivo.escrever(itemImoveis.localidade.municipio.nome);
arquivo.escrever(itemImoveis.cep);
arquivo.escrever('');
arquivo.escrever('');
arquivo.escrever(areaDoTerreno);
arquivo.escrever(areaConstruida);
arquivo.escrever(valorVenal);
arquivo.escrever(dtEmissao);
arquivo.escrever(itemCertidaoITBI.comentario);
arquivo.escrever('1');
arquivo.novaLinha()
```

Escreve, na ordem definida pelo cabeçalho, todos os dados coletados do imóvel: responsável, corresponsável, matrícula, código (CNM), inscrição imobiliária, tipo de imóvel, tipo de edificação, endereço completo, área do terreno, área construída, valor venal, data do habite-se, o comentário da certidão de ITBI (usado como "Informação Adicional") e a versão fixa do leiaute (`'1'`). As colunas de **Coordenada X** e **Coordenada Y** são escritas em branco, pois não há origem de dado mapeada para elas no script.

### 9. Retorno do Resultado

```groovy
Resultado.arquivo(arquivo)
```

Ao final do processamento de todos os documentos, certidões e imóveis, o arquivo CSV gerado é disponibilizado como resultado do script.

## Código Completo

```groovy
arquivo = Arquivo.novo('leiauteCadastroImobiliario.csv', 'csv', [encoding: 'UTF-8', delimitador: ";"]);

fonteDocumentos = Dados.tributos.v2.documentos;
fonteCertidaoITBI = Dados.tributos.v2.certidaoITBI;
fonteImoveisITBI = Dados.tributos.v2.certidaoITBI.imoveis;
fonteImoveis = Dados.tributos.v2.imoveis;
fonteObras = Dados.tributos.v2.obras;
fonteHabitese = Dados.tributos.v2.obra.habitese;
fonteCamposAdicionais = Dados.tributos.v2.imovel.camposAdicionais;

p_dataInicial = parametros.dataInicial.valor
p_dataFinal = parametros.dataFinal.valor

arquivo.escrever('Nome do Proprietario');
arquivo.escrever('CPF/CNPJ do Proprietario');
arquivo.escrever('Nome do Corresponsavel');
arquivo.escrever('CPF/CNPJ do Corresponsavel');
arquivo.escrever('Matricula do Imovel no Registro de Imoveis');
arquivo.escrever('Codigo Nacional de Matricula do Imovel (CNM)');
arquivo.escrever('Inscricao Imobiliaria');
arquivo.escrever('Imovel Rural ou Urbano (R/U)');
arquivo.escrever('Tipo do Imovel (casa, apartamento, etc)');
arquivo.escrever('Tipo Logradouro');
arquivo.escrever('Nome Logradouro');
arquivo.escrever('Complemento');
arquivo.escrever('Numero do Imovel');
arquivo.escrever('Bairro');
arquivo.escrever('Municipio');
arquivo.escrever('CEP');
arquivo.escrever('Coordenada X');
arquivo.escrever('Coordenada Y');
arquivo.escrever('Area (m2) do Terreno / Fracao Tradicional');
arquivo.escrever('Area (m2) Construcao');
arquivo.escrever('Valor de mercado do imovel');
arquivo.escrever('Data do Habite-se');
arquivo.escrever('Informacao Adicional');
arquivo.escrever('Versao do Leiaute');
arquivo.novaLinha()

filtroDocumentos = "tipoReferente = 'TRANSFERENCIA_IMOVEIS' and dtEmissao > ${p_dataInicial.format("yyyy-MM-dd")} and dtEmissao < ${p_dataFinal.format("yyyy-MM-dd")} and nroDocumento >= 1"

dadosDocumentos = fonteDocumentos.busca(criterio: filtroDocumentos)

imoveisProcessados = []

percorrer (dadosDocumentos) { itemDocumentos ->
  
  dadosCertidaoITBI = fonteCertidaoITBI.busca(parametros:["ano":itemDocumentos.anoDocumento,"nroDocumento":itemDocumentos.nroDocumento])
  
  percorrer (dadosCertidaoITBI) { itemCertidaoITBI ->
    
    dadosImoveisITBI = fonteImoveisITBI.busca(parametros:["ano":itemDocumentos.anoDocumento,"nroDocumento":itemDocumentos.nroDocumento])
    
    percorrer (dadosImoveisITBI) { itemImoveisITBI ->
      
      se (!imoveisProcessados.contains(itemImoveisITBI.idImovel)) {
        
        imoveisProcessados.add(itemImoveisITBI.idImovel)
        
        filtroImoveis = "id = ${itemImoveisITBI.idImovel}"
        
        dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis)
        
        percorrer (dadosImoveis) { itemImoveis ->
          
          // Reinicializa as variaveis para CADA imovel, evitando herdar valores do imovel anterior
          areaDoTerreno = 0
          areaConstruida = 0
          valorVenal = 0
          tipoEdificacao = ''
          dtEmissao = "Não há habite-se no sistema para este imóvel"
          
          // Validacao do Habite-se: so preenche dtEmissao se existir obra vinculada ao imovel
          // E um habite-se emitido (com data de emissao) para essa obra
          filtroObras = "imovel.id = ${itemImoveis.id}"
          
          dadosObras = fonteObras.busca(criterio: filtroObras)
          
          percorrer (dadosObras) { itemObras ->
            
            dadosHabitese = fonteHabitese.busca(parametros:["idObra":itemObras.id])
            
            percorrer (dadosHabitese) { itemHabitese ->
              se (itemHabitese.dtEmissao != null) {
                imprimir 'Imovel ' + itemImoveis.id + ' - Obra ' + itemObras.codigo + ' - Habite-se emitido em ' + itemHabitese.dtEmissao
                dtEmissao = itemHabitese.dtEmissao.format('dd/MM/yyyy')
              }
            }
          }
          
          dadosCamposAdicionais = fonteCamposAdicionais.busca(parametros:["idImovel":itemImoveis.id], criterio: "campoAdicional.titulo = 'ÁREA DO TERRENO'")
          
          percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
            switch(itemCamposAdicionais.campoAdicional.titulo){
              case "ÁREA DO TERRENO": areaDoTerreno = itemCamposAdicionais.vlCampo
              break
              case "ÁREA TOTAL CONSTRUÍDA": areaConstruida = itemCamposAdicionais.vlCampo
              break
              case "VALOR VENAL DO IMOVEL": valorVenal = itemCamposAdicionais.vlCampo
              break
              case "TIPO DE EDIFICACAO": tipoEdificacao = itemCamposAdicionais.opcoes
              break
            }
          }
          
          arquivo.escrever(itemImoveis.responsavel.nome);
          arquivo.escrever(itemImoveis.responsavel.cpfCnpj);
          arquivo.escrever(itemImoveis.corresponsavel.nome);
          arquivo.escrever(itemImoveis.corresponsavel.cpfCnpj);
          arquivo.escrever(itemImoveis.matricula);
          arquivo.escrever(itemImoveis.codigo);
          arquivo.escrever(itemImoveis.inscricaoImobiliariaFormatada);
          arquivo.escrever(itemImoveis.tipoImovel.valor);
          arquivo.escrever(tipoEdificacao);
          arquivo.escrever(itemImoveis.logradouro.tipoLogradouroDescricao);
          arquivo.escrever(itemImoveis.logradouro.nome);
          arquivo.escrever(itemImoveis.complemento);
          arquivo.escrever(itemImoveis.numero);
          arquivo.escrever(itemImoveis.bairro.nome);
          arquivo.escrever(itemImoveis.localidade.municipio.nome);
          arquivo.escrever(itemImoveis.cep);
          arquivo.escrever('');
          arquivo.escrever('');
          arquivo.escrever(areaDoTerreno);
          arquivo.escrever(areaConstruida);
          arquivo.escrever(valorVenal);
          arquivo.escrever(dtEmissao);
          arquivo.escrever(itemCertidaoITBI.comentario);
          arquivo.escrever('1');
          arquivo.novaLinha()
        }
      }
    }
  }
}

Resultado.arquivo(arquivo)
```