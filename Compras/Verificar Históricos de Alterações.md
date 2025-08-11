# Documentação do Script de Geração de Log de Alterações de Materiais

Este script Groovy tem como finalidade buscar informações detalhadas sobre materiais específicos (identificados por seus códigos) e gerar um arquivo de log (`.txt`) contendo dados como ID, código, descrição, e informações de criação e última alteração de cada material. É uma ferramenta útil para auditoria e acompanhamento de alterações em materiais.

## Explicação Geral do Código

O script começa obtendo os códigos dos materiais a partir de um parâmetro de entrada (`ParamListaOpcao`). Em seguida, ele utiliza esses códigos para buscar os materiais correspondentes em uma fonte de dados. O coração do script é a iteração sobre os materiais encontrados, onde para cada um, ele formata e escreve informações relevantes (ID, código, descrição, usuário e data de criação/alteração) tanto no console quanto em um arquivo de log (`log_alteracoes.txt`). Caso nenhum material seja encontrado, uma mensagem apropriada é registrada. Ao final, o arquivo de log é disponibilizado como resultado do script.

## Blocos de Código

### Obtenção de Parâmetros e Configuração da Fonte de Dados

```groovy
// Pega o código do material passado como parâmetro, tratando ParamListaOpcao
def codigoMaterialParam = parametros.material
def codigoMaterialValor = codigoMaterialParam.selecionados

// Fonte de dados
def fonteMateriais = Dados.compras.v1.materiais
def filtroMateriais = "codigoMaterial in (${codigoMaterialValor.join(\",\")})"
def camposRetorno = "id, codigoMaterial, descricao, usuarioCriacao, dataCriacao, usuarioAlteracao, dataAlteracao"
```

Neste bloco, o script prepara os dados de entrada e a fonte de onde buscará as informações:

*   `codigoMaterialParam = parametros.material`: Obtém o parâmetro `material` que é passado para o script. Presume-se que este parâmetro seja do tipo `ParamListaOpcao`, que permite a seleção de múltiplos valores.
*   `codigoMaterialValor = codigoMaterialParam.selecionados`: Extrai os valores selecionados do parâmetro `material`. Estes são os códigos dos materiais que o script deve processar.
*   `fonteMateriais = Dados.compras.v1.materiais`: Define a fonte de dados para materiais, apontando para o serviço de materiais de compras.
*   `filtroMateriais = "codigoMaterial in (${codigoMaterialValor.join(\",\")})"`: Constrói uma string de filtro para a busca de materiais. Ele usa a cláusula `in` para buscar materiais cujos `codigoMaterial` estejam na lista de `codigoMaterialValor` fornecida. O `join(",")` é crucial para formatar a lista de códigos em uma string separada por vírgulas, adequada para a consulta.
*   `camposRetorno = "id, codigoMaterial, descricao, usuarioCriacao, dataCriacao, usuarioAlteracao, dataAlteracao"`: Define quais campos devem ser retornados na busca dos materiais. Isso otimiza a requisição, trazendo apenas os dados necessários.

### Busca dos Materiais e Criação do Arquivo de Log

```groovy
// Busca os materiais
def dadosMateriais = fonteMateriais.busca(criterio: filtroMateriais, campos: camposRetorno)

// Nome do arquivo e criação do log com configuração
def nomeArquivo = "log_alteracoes.txt"
def arquivoLog = Arquivo.novo(nomeArquivo, "txt", [ encoding: "UTF-8", entreAspas: "N" ])
```

Esta seção executa a busca dos dados e configura o arquivo de log:

*   `dadosMateriais = fonteMateriais.busca(...)`: Realiza a busca dos materiais na fonte de dados, aplicando o `criterio` (filtro) e solicitando os `camposRetorno` definidos anteriormente.
*   `nomeArquivo = "log_alteracoes.txt"`: Define o nome do arquivo de log que será gerado.
*   `arquivoLog = Arquivo.novo(...)`: Cria uma nova instância de arquivo de texto para o log. As configurações incluem `encoding: "UTF-8"` para suportar caracteres especiais e `entreAspas: "N"`, pois o conteúdo não será formatado como CSV e não necessita de encapsulamento automático por aspas.

### Geração do Conteúdo do Log

```groovy
// Geração do conteúdo do log
if (!dadosMateriais || dadosMateriais.size() == 0) {
    def msg = "Nenhum material encontrado com os códigos informados."
    imprimir(msg)
    arquivoLog.escrever(msg)
} else {
    percorrer(dadosMateriais) { item ->
        def linha1 = "ID=${item.id} | Código=${item.codigoMaterial} | Descrição=${item.descricao}"
        imprimir(linha1)
        arquivoLog.escrever(linha1 + "\n")

        if (item.usuarioCriacao != null && item.dataCriacao != null) {
            def dataCriacao = item.dataCriacao.format("dd/MM/yyyy")
            def horaCriacao = item.dataCriacao.format("HH:mm:ss")
            def linha2 = "Criado por: ${item.usuarioCriacao} em ${dataCriacao} ${horaCriacao}"
            imprimir(linha2)
            arquivoLog.escrever(linha2 + "\n")
        } else {
            def linha2 = "Informações de criação não disponíveis."
            imprimir(linha2)
            arquivoLog.escrever(linha2 + "\n")
        }

        if (item.usuarioAlteracao != null && item.dataAlteracao != null) {
            def dataAlteracao = item.dataAlteracao.format("dd/MM/yyyy")
            def horaAlteracao = item.dataAlteracao.format("HH:mm:ss")
            def linha3 = "Última alteração realizada por: ${item.usuarioAlteracao} em ${dataAlteracao} ${horaAlteracao}"
            imprimir(linha3)
            arquivoLog.escrever(linha3 + "\n")
        } else {
            def linha3 = "Ainda não alterado."
            imprimir(linha3)
            arquivoLog.escrever(linha3 + "\n")
        }

        // Espaçamento entre registros
        def separador = "-" * 80
        imprimir(separador + "\n")
        arquivoLog.escrever(separador + "\n\n")
    }
}
```

Este é o bloco principal onde o conteúdo do log é gerado, tanto para o console quanto para o arquivo:

*   **Verificação de Materiais Encontrados**: O script verifica se `dadosMateriais` está vazio ou nulo. Se sim, uma mensagem indicando que nenhum material foi encontrado é impressa no console e escrita no `arquivoLog`.
*   **Iteração e Escrita de Log**: Se materiais forem encontrados, o script itera sobre cada `item` (material):
    *   **Linha 1 (ID, Código, Descrição)**: Cria uma string com o ID, código e descrição do material. Esta linha é impressa no console e escrita no `arquivoLog`, seguida por uma quebra de linha (`\n`).
    *   **Linha 2 (Informações de Criação)**: Verifica se as informações de `usuarioCriacao` e `dataCriacao` estão disponíveis. Se sim, formata a data e hora e cria uma string com essas informações, que é impressa e escrita no log. Caso contrário, uma mensagem de 


indisponibilidade é registrada.
    *   **Linha 3 (Informações de Alteração)**: Similar à linha 2, verifica as informações de `usuarioAlteracao` e `dataAlteracao`. Se disponíveis, formata e registra. Caso contrário, indica que o material `Ainda não alterado`.
    *   **Espaçamento entre Registros**: Após cada material, uma linha separadora (`-` repetido 80 vezes) é impressa no console e escrita no `arquivoLog`, seguida por duas quebras de linha (`\n\n`) para criar um espaçamento visual entre os registros no log.

### Retorno do Arquivo

```groovy
// Exibe o arquivo como resultado para download
Resultado.arquivo(arquivoLog, nomeArquivo)
```

Esta linha finaliza o script, disponibilizando o arquivo de log gerado:

*   `Resultado.arquivo(arquivoLog, nomeArquivo)`: Associa o objeto `arquivoLog` (que contém todo o conteúdo gerado) ao resultado final do script. Isso permite que o arquivo `log_alteracoes.txt` seja baixado ou acessado por outros sistemas após a execução do script.

## Código Completo

```groovy
// Pega o código do material passado como parâmetro, tratando ParamListaOpcao
def codigoMaterialParam = parametros.material
def codigoMaterialValor = codigoMaterialParam.selecionados

// Fonte de dados
def fonteMateriais = Dados.compras.v1.materiais
def filtroMateriais = "codigoMaterial in (${codigoMaterialValor.join(\",\")})"
def camposRetorno = "id, codigoMaterial, descricao, usuarioCriacao, dataCriacao, usuarioAlteracao, dataAlteracao"

// Busca os materiais
def dadosMateriais = fonteMateriais.busca(criterio: filtroMateriais, campos: camposRetorno)

// Nome do arquivo e criação do log com configuração
def nomeArquivo = "log_alteracoes.txt"
def arquivoLog = Arquivo.novo(nomeArquivo, "txt", [ encoding: "UTF-8", entreAspas: "N" ])

// Geração do conteúdo do log
if (!dadosMateriais || dadosMateriais.size() == 0) {
    def msg = "Nenhum material encontrado com os códigos informados."
    imprimir(msg)
    arquivoLog.escrever(msg)
} else {
    percorrer(dadosMateriais) { item ->
        def linha1 = "ID=${item.id} | Código=${item.codigoMaterial} | Descrição=${item.descricao}"
        imprimir(linha1)
        arquivoLog.escrever(linha1 + "\n")

        if (item.usuarioCriacao != null && item.dataCriacao != null) {
            def dataCriacao = item.dataCriacao.format("dd/MM/yyyy")
            def horaCriacao = item.dataCriacao.format("HH:mm:ss")
            def linha2 = "Criado por: ${item.usuarioCriacao} em ${dataCriacao} ${horaCriacao}"
            imprimir(linha2)
            arquivoLog.escrever(linha2 + "\n")
        } else {
            def linha2 = "Informações de criação não disponíveis."
            imprimir(linha2)
            arquivoLog.escrever(linha2 + "\n")
        }

        if (item.usuarioAlteracao != null && item.dataAlteracao != null) {
            def dataAlteracao = item.dataAlteracao.format("dd/MM/yyyy")
            def horaAlteracao = item.dataAlteracao.format("HH:mm:ss")
            def linha3 = "Última alteração realizada por: ${item.usuarioAlteracao} em ${dataAlteracao} ${horaAlteracao}"
            imprimir(linha3)
            arquivoLog.escrever(linha3 + "\n")
        } else {
            def linha3 = "Ainda não alterado."
            imprimir(linha3)
            arquivoLog.escrever(linha3 + "\n")
        }

        // Espaçamento entre registros
        def separador = "-" * 80
        imprimir(separador + "\n")
        arquivoLog.escrever(separador + "\n\n")
    }
}

imprimir "Processo de exclusão finalizado."
```

