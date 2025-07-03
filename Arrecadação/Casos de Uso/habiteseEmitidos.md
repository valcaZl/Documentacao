# 📄 Relacionamento entre Documentos, Habite-se e Obras no BFC-SCRIPT

Este exemplo demonstra como utilizar o **BFC-SCRIPT** para realizar um relacionamento entre três fontes de dados distintas do módulo de Tributos da Betha Sistemas: **Documentos**, **Habite-se** e **Obras**. O objetivo final é gerar uma **fonte dinâmica consolidada** com as informações de obras que possuem Habite-se emitido.

## 🧱 Fontes de Dados Utilizadas

* `Dados.tributos.v2.documentos`: Consulta os documentos cadastrados no sistema.
* `Dados.tributos.v2.habitese`: Retorna os registros de Habite-se vinculados a documentos.
* `Dados.tributos.v2.obras`: Recupera os dados das obras relacionadas ao Habite-se.

## 🎯 Objetivo do Script

Obter, para um conjunto de anos selecionados pelo usuário, a lista de documentos do tipo **Habite-se TOTAL ou PARCIAL**, que estejam com a situação **"EMITIDO"**, e trazer o **nome do contribuinte responsável pela execução da obra** junto com o **código da obra**.

## 💡 Exemplo de Código

```bfc-script
ESQUEMA = [
  ano: Esquema.numero,
  nroDocumento: Esquema.numero,
  contribuinte: Esquema.caracter,
  codigoObra: Esquema.numero
]

fonte = Dados.dinamico.v2.novo(ESQUEMA);
fonteDocumentos = Dados.tributos.v2.documentos;

p_ano = parametros.ano.selecionados.valor

filtroDocumentos = "tipoHabitese in ('TOTAL', 'PARCIAL') and anoDocumento in (${p_ano.join(', ')})"
dadosDocumentos = fonteDocumentos.busca(criterio: filtroDocumentos)

Linha = []

percorrer (dadosDocumentos) { itemDocumentos ->
  fonteHabitese = Dados.tributos.v2.habitese;
  filtroHabitese = "situacaoHabitese = 'EMITIDO'"

  dadosHabitese = fonteHabitese.busca(criterio: filtroHabitese, parametros:["ano": itemDocumentos.anoDocumento,"nroDocumento": itemDocumentos.nroDocumento])

  percorrer (dadosHabitese) { itemHabitese ->
    fonteObras = Dados.tributos.v2.obras;
    filtroObras = "id = ${itemHabitese.idObra}"
    dadosObras = fonteObras.busca(criterio: filtroObras)

    percorrer (dadosObras) { itemObras ->
      Linha << [
        ano: itemDocumentos.anoDocumento,
        nroDocumento: itemDocumentos.nroDocumento,
        contribuinte: itemObras.responsavelExecucao.contribuinte.nome,
        codigoObra: itemObras.codigo
      ]
    }
  }
}

Linha = Linha.sort{a, b -> a.ano <=> b.ano}

Linha.each{ itemLinha ->
  imprimir JSON.escrever(itemLinha)
  fonte.inserirLinha(itemLinha)
}

retornar fonte
```

## 📌 Explicação do Código

1. Definição de um esquema com os campos desejados: ano, número do documento, nome do contribuinte e código da obra.
2. Busca todos os documentos que sejam do tipo Habite-se (TOTAL ou PARCIAL) e que pertençam aos anos selecionados pelo usuário.
3. Para cada documento encontrado, consulta o Habite-se vinculado com situação "EMITIDO".
4. Para cada Habite-se, busca a obra relacionada.
5. Para cada obra, extrai o nome do contribuinte responsável pela execução e o código da obra.
6. Os dados são organizados em uma lista (Linha), ordenados por ano e inseridos na fonte dinâmica final.

## ✅ Considerações

Este tipo de script é útil para relatórios que exigem cruzamento de dados entre documentos, habite-ses e obras, permitindo que a gestão tributária tenha uma visão consolidada de todas as obras com Habite-se emitido no município.

O parâmetro de ano permite flexibilidade ao usuário para consultar diferentes períodos de forma dinâmica.
