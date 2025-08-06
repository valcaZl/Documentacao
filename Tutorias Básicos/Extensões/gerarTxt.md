# Documentação do Script de Geração de Arquivo TXT de Pessoas e Contribuintes

Este script Groovy tem como objetivo principal **gerar um arquivo de texto (.txt)** contendo informações de ID e nome de contribuintes, com base em um cruzamento de dados de pessoas e contribuintes. Ele interage com fontes de dados `Dados.procuradoria.v2.pessoas` e `Dados.tributos.v2.contribuintes` para buscar, processar e registrar informações em um formato de texto plano.

## Explicação Geral do Código

O script inicia definindo uma função auxiliar para padronizar nomes (`formatarNome`). Em seguida, ele configura a criação de um arquivo TXT com um nome dinâmico baseado na data atual. O fluxo principal envolve a busca de dados de pessoas, a formatação de seus nomes e, crucialmente, o uso desses nomes formatados para localizar contribuintes correspondentes. Para cada contribuinte encontrado, o script **escreve uma linha específica no arquivo TXT**, garantindo que os dados sejam exportados de forma estruturada. Finalmente, o arquivo TXT gerado é preparado para ser disponibilizado como resultado do script.

## Blocos de Código

### Função `formatarNome`

```groovy
String formatarNome(String nome) {
  if (!nome) return ""
  
  // Remove caracteres especiais, mantendo letras (com acento), números e espaços
  String limpo = nome.replaceAll("[^\\p{L}\\p{N} ]", "")
  
  // Remove espaços extras (opcional)
  limpo = limpo.trim().replaceAll("\\s+", " ")
  
  return limpo
}
```

Esta função auxiliar é responsável por limpar e padronizar strings de nome. Ela remove caracteres especiais (mantendo apenas letras, números e espaços) e normaliza múltiplos espaços, garantindo que os nomes usados nas buscas e no arquivo TXT estejam em um formato consistente.

### Inicialização do Arquivo TXT e Fontes de Dados

```groovy
arquivo = Arquivo.novo("Pessoas" + Datas.formatar(Datas.hoje(), "ddMMyyyy")+".txt", "txt", [encoding: "UTF-8", delimitador: ";"]);

fontePessoas = Dados.procuradoria.v2.pessoas;
fonteContribuintes = Dados.tributos.v2.contribuintes;
```

Neste bloco, o script realiza a **configuração essencial para a geração do arquivo TXT**:

*   **Criação do Objeto `arquivo`**: Um novo arquivo de texto é instanciado usando `Arquivo.novo()`. O nome do arquivo é gerado dinamicamente (ex: `Pessoas05082025.txt`), incorporando a data atual. É especificado que o arquivo terá a extensão `.txt`, usará codificação `UTF-8` e terá `;` como delimitador, o que é fundamental para a estrutura dos dados que serão escritos.
*   **Definição das Fontes de Dados**: As variáveis `fontePessoas` e `fonteContribuintes` são inicializadas, apontando para as respectivas fontes de dados que serão consultadas para obter as informações a serem escritas no arquivo TXT.

### Busca, Processamento e Escrita no Arquivo TXT

```groovy
filtroPessoas = "cpfCnpj is null and situacao = 'ATIVADO'"

dadosPessoas = fontePessoas.buscar(criterio: filtroPessoas,campos: "id, nome").take(100)

nomeFormatado = ''

percorrer (dadosPessoas) { itemPessoas ->
  nomeFormatado = formatarNome(itemPessoas.nome)
  //imprimir nomeFormatado
  
  filtroContribuintes = "nome = '${nomeFormatado}'"
  
  dadosContribuintes = fonteContribuintes.busca(criterio: filtroContribuintes)
  
  percorrer (dadosContribuintes) { itemContribuintes ->
    arquivo.escrever("Id: ${itemContribuintes.id} / Nome: ${itemContribuintes.nome}")
    arquivo.novaLinha()
  }
}
```

Esta é a seção central onde os dados são processados e **escritos no arquivo TXT**:

*   **Busca Inicial de Pessoas**: O script busca até 100 registros de pessoas que não possuem CPF/CNPJ e estão ativadas. Apenas o `id` e o `nome` são recuperados.
*   **Iteração e Cruzamento de Dados**: Para cada pessoa encontrada (`itemPessoas`):
    *   O nome da pessoa é formatado usando `formatarNome`.
    *   Um novo filtro é construído para buscar contribuintes cujo nome corresponda ao nome formatado.
    *   Os contribuintes que atendem a esse critério são buscados.
    *   **Escrita no Arquivo TXT**: Para cada contribuinte correspondente (`itemContribuintes`), a linha `arquivo.escrever("Id: ${itemContribuintes.id} / Nome: ${itemContribuintes.nome}")` é executada. Esta instrução é responsável por **adicionar o ID e o nome do contribuinte diretamente ao arquivo TXT** que foi inicializado. Em seguida, `arquivo.novaLinha()` garante que cada registro seja escrito em uma nova linha, mantendo a formatação do arquivo.

### Finalização e Disponibilização do Arquivo TXT

```groovy
Resultado.arquivo(arquivo)
Resultado.nome("Arquivo${Datas.formatar(Datas.hoje(), 'ddMMyyyy')}.zip")
```

Este bloco finaliza o processo de geração do arquivo:

*   `Resultado.arquivo(arquivo)`: Esta linha é crucial, pois **associa o objeto `arquivo` (que contém todos os dados escritos) ao resultado final do script**. Isso significa que o conteúdo do arquivo TXT será disponibilizado para o usuário ou para o próximo passo do fluxo de trabalho.
*   `Resultado.nome("Arquivo${Datas.formatar(Datas.hoje(), 'ddMMyyyy')}.zip")`: Define o nome do arquivo que será gerado para download. Embora o script crie um `.txt`, ele é empacotado em um `.zip` para download, com um nome dinâmico (ex: `Arquivo05082025.zip`).

## Código Completo

```groovy
String formatarNome(String nome) {
  if (!nome) return ""
  
  // Remove caracteres especiais, mantendo letras (com acento), números e espaços
  String limpo = nome.replaceAll("[^\\p{L}\\p{N} ]", "")
  
  // Remove espaços extras (opcional)
  limpo = limpo.trim().replaceAll("\\s+", " ")
  
  return limpo
}

arquivo = Arquivo.novo("Pessoas" + Datas.formatar(Datas.hoje(), "ddMMyyyy")+".txt", "txt", [encoding: "UTF-8", delimitador: ";"]);

fontePessoas = Dados.procuradoria.v2.pessoas;
fonteContribuintes = Dados.tributos.v2.contribuintes;

filtroPessoas = "cpfCnpj is null and situacao = 'ATIVADO'"

dadosPessoas = fontePessoas.buscar(criterio: filtroPessoas,campos: "id, nome").take(100)

nomeFormatado = ''

percorrer (dadosPessoas) { itemPessoas ->
  nomeFormatado = formatarNome(itemPessoas.nome)
  //imprimir nomeFormatado
  
  filtroContribuintes = "nome = '${nomeFormatado}'"
  
  dadosContribuintes = fonteContribuintes.busca(criterio: filtroContribuintes)
  
  percorrer (dadosContribuintes) { itemContribuintes ->
    arquivo.escrever("Id: ${itemContribuintes.id} / Nome: ${itemContribuintes.nome}")
    arquivo.novaLinha()
  }
}

Resultado.arquivo(arquivo)
Resultado.nome("Arquivo${Datas.formatar(Datas.hoje(), 'ddMMyyyy')}.zip")
```

