# Documentação do Script de Consolidação de Protestos e CDAs

Este documento descreve detalhadamente a funcionalidade do script Groovy desenvolvido para a plataforma **Betha Sistemas**, focado na integração e correlação de dados entre Documentos de Dívida, Certidões de Dívida Ativa (CDA) e informações de Protestos no módulo de **Procuradoria**.

## 📄 Descrição
O script realiza a busca de documentos de dívida com base em parâmetros específicos (ID, Tipo e Ano) e correlaciona as CDAs vinculadas a esses documentos com seus respectivos registros de protestos e cartórios. O objetivo principal é consolidar em uma única fonte dinâmica os dados cadastrais do devedor, a natureza da dívida, os números de processos judiciais vinculados e o nome do tabelionato onde o protesto foi lavrado.

## 🛠️ Requisitos e Contexto
* **Módulo:** Procuradoria.
* **Plataforma:** BFC-Script (utilizando `Dados.dinamico.v2` e `Dados.procuradoria.v2`).
* **Finalidade:** Geração de relatórios ou consultas consolidadas para verificação de consistência entre Dívida Ativa e Protestos.

---

## 🔍 Funcionalidades Principais

* **Formatação de Documentos**: Utiliza uma função interna para aplicar máscaras de pontuação em CPFs (11 dígitos) e CNPJs (14 dígitos), garantindo a legibilidade no relatório final.
* **Filtro Dinâmico por Parâmetros**: Localiza o documento base através dos parâmetros de entrada `idDocumento`, `tipoDocumento` e `anoDocumento`.
* **Processamento de CDAs**: Realiza o tratamento da string de CDAs (geralmente no formato "número/ano") para realizar buscas individuais na base de protestos.
* **Vinculação de Cartórios**: Identifica o nome do Tabelionato/Cartório responsável através do cruzamento de IDs entre a fonte de protestos e a fonte de cartórios.
* **Saneamento de Processos**: Coleta os números de processos, remove caracteres não numéricos e os agrupa de forma organizada.

---

## 🧠 Código Completo para Importação

```groovy
//-------------------------------------------
// Definição do Esquema da Fonte Dinâmica
//-------------------------------------------
esquema = [
  pessoaNome: Esquema.caracter,
  pessoaCpfCnpj: Esquema.caracter,
  pessoaNumero: Esquema.caracter,
  pessoaBairro: Esquema.caracter,
  pessoaCep: Esquema.caracter,
  pessoaCidade: Esquema.caracter,
  dividaNatureza: Esquema.caracter,
  listaCdas: Esquema.caracter,
  processos: Esquema.caracter,
  tabelionato: Esquema.caracter,
  valorTotal: Esquema.numero,
  anosDivida: Esquema.caracter
]

//-------------------------------------------
// Função para Formatação de CPF/CNPJ
//-------------------------------------------
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

//-------------------------------------------
// Inicialização de Fontes e Parâmetros
//-------------------------------------------
fonte = Dados.dinamico.v2.novo(esquema);
fonteDocumentosDividaScript = Dados.procuradoria.v2.documentosDividaScript;
fonteProtestos = Dados.procuradoria.v2.protestos;
fonteProtestosMovtos = Dados.procuradoria.v2.protestosMovtos;
fonteCartorios = Dados.procuradoria.v2.cartorios;

p_tipoDocumento = parametros.tipoDocumento.valor
p_anoDocumento = parametros.anoDocumento.valor
p_idDocumento = parametros.idDocumento.valor

//-------------------------------------------
// Lógica de Busca e Consolidação
//-------------------------------------------
filtroDocumentosDividaScript = "idDocumento = ${p_idDocumento} and tipoDocumento = '${p_tipoDocumento}' and anoDocumento = ${p_anoDocumento}"

linha = []
processos = []

// Busca o documento principal
dadosDocumentosDividaScript = fonteDocumentosDividaScript.buscar(criterio: filtroDocumentosDividaScript, primeiro: true)

if (dadosDocumentosDividaScript) {
    // Processa cada CDA listada no documento
    dadosDocumentosDividaScript.listaCdas.split(',').each { itemCda ->
        def partes = itemCda.split('/')
        def nroCda = partes[0]
        def anoCda = partes[1]
        
        filtroProtestos = "anoCda = ${anoCda} and nroCda = ${nroCda}"
        dadosProtestos = fonteProtestos.buscar(criterio: filtroProtestos)
        
        percorrer (dadosProtestos) { itemProtestos -> 
            // Busca movimentação e dados do cartório vinculado
            filtroProtestosMovtos = "idProtesto = ${itemProtestos.id}"
            dadosProtestosMovtos = fonteProtestosMovtos.buscar(criterio: filtroProtestosMovtos, primeiro: true)
            
            filtroCartorios = "id = ${itemProtestos.idCartorio}"
            dadosCartorios = fonteCartorios.buscar(criterio: filtroCartorios, primeiro: true)
            
            if (itemProtestos.processo) {
                processos << itemProtestos.processo 
            }
        }
    }
    
    // Saneamento dos números de processos
    nroProcessos = processos.findAll { it }.collect { p ->
        p.toString().replaceAll("[^0-9]", "")
    }
    
    // Montagem da linha de retorno
    linha = [
        pessoaNome: dadosDocumentosDividaScript.pessoaNome,
        pessoaCpfCnpj: formatCpfCnpj(dadosDocumentosDividaScript.pessoaCpfCnpj),
        pessoaNumero: dadosDocumentosDividaScript.pessoaNumero,
        pessoaBairro: dadosDocumentosDividaScript.pessoaBairro,
        pessoaCep: dadosDocumentosDividaScript.pessoaCep,
        pessoaCidade: dadosDocumentosDividaScript.pessoaCidade,
        dividaNatureza: dadosDocumentosDividaScript.dividaNatureza,
        listaCdas: dadosDocumentosDividaScript.listaCdas,
        processos: nroProcessos.unique().join(', ') ?: "Não Cadastrado no sistema",
        tabelionato: dadosCartorios?.pessoa?.nome ?: "Não Cadastrado no sistema",
        valorTotal: dadosDocumentosDividaScript.valorTotal,
        anosDivida: dadosDocumentosDividaScript.anosDivida
    ]
    
    fonte.inserirLinha(linha)
}

return fonte