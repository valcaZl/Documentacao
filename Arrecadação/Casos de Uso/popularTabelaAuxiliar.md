# Explicação da Funcionalidade do Script de População e Atualização de Tabela Auxiliar

Este documento detalha a funcionalidade de um script Groovy projetado para popular e atualizar uma tabela auxiliar (`Dados.tributos.v2.tabelaAuxiliar.registros`) com dados de contribuintes pessoas físicas (`Dados.tributos.v2.contribuintes`). O script é otimizado para lidar tanto com a população inicial da tabela quanto com suas atualizações subsequentes, garantindo que apenas novos registros sejam adicionados.

## Visão Geral do Script

O script opera em duas etapas principais: primeiro, ele identifica o último código de contribuinte já registrado na tabela auxiliar. Em seguida, ele busca novos contribuintes pessoas físicas cujos códigos são maiores que o último registrado e os insere na tabela auxiliar. Uma particularidade importante é a necessidade de comentar/descomentar certas linhas para a primeira execução (população inicial) e para as execuções posteriores (atualizações).

## Detalhes da Implementação

### 1. Fontes de Dados

O script inicia definindo as fontes de dados que serão utilizadas:

```
fonteRegistros = Dados.tributos.v2.tabelaAuxiliar.registros;
fonteContribuintes = Dados.tributos.v2.contribuintes;
```

- `fonteRegistros`: Representa a tabela auxiliar onde os dados dos contribuintes serão armazenados.

- `fonteContribuintes`: Representa a tabela principal de contribuintes, de onde os dados serão extraídos.

### 2. Identificação do Último Código Registrado

Para evitar a duplicação de registros e garantir que apenas novos contribuintes sejam adicionados, o script busca o maior código de contribuinte já presente na tabela auxiliar. Isso é feito através dos seguintes passos:

```
relacaoCodigosContribuintes = fonteRegistros.busca(campos: "campo3", parametros:["codigoTabelaAuxiliar":12])
.collect { 
  try {
    it.campo3.toInteger()
  } catch (Exception e) {
    0
  }
}

ultimoCodigoRegistrado = relacaoCodigosContribuintes.max();
```

- `fonteRegistros.busca(...)`: Realiza uma busca na tabela auxiliar, filtrando por `codigoTabelaAuxiliar: 12` e selecionando apenas o `campo3`, que se espera conter o código do contribuinte.

- `.collect { ... }`: Transforma os resultados da busca em uma lista de inteiros. Um bloco `try-catch` é usado para tratar possíveis erros de conversão para inteiro, atribuindo `0` caso ocorra um erro, o que é útil para garantir que a lista contenha apenas números válidos para a próxima etapa.

- `relacaoCodigosContribuintes.max()`: Encontra o valor máximo (o último código registrado) na lista de códigos coletados. Se a tabela estiver vazia ou todos os valores forem `0` devido a erros, `ultimoCodigoRegistrado` será `0`.

### 3. Filtragem de Contribuintes

Com o `ultimoCodigoRegistrado` em mãos, o script constrói um filtro para buscar apenas os contribuintes pessoas físicas que ainda não foram registrados na tabela auxiliar:

```
filtroContribuintes = "tipoPessoa = 'FISICA' and codigo > '${ultimoCodigoRegistrado}'"

dadosContribuintes = fonteContribuintes.busca(criterio: filtroContribuintes, campos: "id, codigo, nome, cpfCnpj"/*, ordenacao: "codigo asc"*/)
```

- `filtroContribuintes`: Uma string que define o critério de busca. Ele seleciona contribuintes com `tipoPessoa = 'FISICA'` e cujo `codigo` é maior que o `ultimoCodigoRegistrado`.

- `fonteContribuintes.busca(...)`: Executa a busca na tabela principal de contribuintes usando o `filtroContribuintes` e seleciona os campos `id`, `codigo`, `nome` e `cpfCnpj`.

- **Nota sobre ****`ordenacao: "codigo asc"`**: A linha de ordenação é comentada na versão inicial do script. Conforme anota no código, ela deve ser descomentada após a primeira população da tabela para otimizar as atualizações.

### 4. Processamento e Inserção de Novos Contribuintes

O script itera sobre os `dadosContribuintes` obtidos e, para cada contribuinte, prepara um registro para inserção na tabela auxiliar:

```
dadosContribuintes.each { itemContribuintes ->
  
  codigo = itemContribuintes.codigo
  nome = itemContribuintes.nome
  cpfCnpj = itemContribuintes.cpfCnpj
  
  conteudo = [
    campo1: "1800/01/01",
    campo2: "",
    campo3: codigo,
    campo4: nome,
    campo5: cpfCnpj,
  ] 
  

  dadosRegistros = fonteRegistros.cria(parametros:["codigoTabelaAuxiliar":12], conteudo: conteudo)
  
  // Atualiza o último código registrado a cada inserção
  //ultimoCodigoRegistrado = codigo  //depois de popular a tabela uma primeira vez descomente essa linha
}
```

- `dadosContribuintes.each { ... }`: Itera sobre cada item (contribuinte) retornado pela busca.

- `codigo`, `nome`, `cpfCnpj`: Extrai os dados relevantes de cada contribuinte.

- `conteudo`: Cria um mapa com os dados a serem inseridos na tabela auxiliar. Os campos são mapeados da seguinte forma:
  - `campo1`: Definido como "1800/01/01" (possivelmente uma data padrão ou placeholder).
  - `campo2`: Vazio (placeholder).
  - `campo3`: Recebe o `codigo` do contribuinte.
  - `campo4`: Recebe o `nome` do contribuinte.
  - `campo5`: Recebe o `cpfCnpj` do contribuinte.

- `fonteRegistros.cria(...)`: Insere o `conteudo` na tabela auxiliar (`fonteRegistros`), associando-o ao `codigoTabelaAuxiliar: 12`.

- **Nota sobre ****`ultimoCodigoRegistrado = codigo`**: Esta linha, assim como a ordenação, deve ser descomentada após a primeira população da tabela. Ela garante que, durante as atualizações, o `ultimoCodigoRegistrado` seja dinamicamente atualizado a cada inserção, permitindo que o script continue a adicionar novos registros de forma eficiente, mesmo que a execução seja interrompida e reiniciada.

## Instruções de Uso

O script possui uma particularidade importante para sua primeira execução e para as subsequentes:

1. **Primeira Execução (População Inicial):**
  - Comente a linha `//dadosContribuintes = fonteContribuintes.busca(criterio: filtroContribuintes, campos: "id, codigo, nome, cpfCnpj"/*, ordenacao: "codigo asc"*/)` (linha 24 no script original) para que a ordenação não seja aplicada inicialmente.
  - Comente a linha `//ultimoCodigoRegistrado = codigo` (linha 44 no script original) para que o `ultimoCodigoRegistrado` não seja atualizado dentro do loop, garantindo que todos os contribuintes sejam processados na primeira vez.
  - Execute o script para popular a tabela auxiliar com todos os contribuintes pessoas físicas.

1. **Execuções Posteriores (Atualizações):**
  - Descomente a linha `dadosContribuintes = fonteContribuintes.busca(criterio: filtroContribuintes, campos: "id, codigo, nome, cpfCnpj", ordenacao: "codigo asc")` (linha 24 no script original) para que a busca seja otimizada com ordenação.
  - Descomente a linha `ultimoCodigoRegistrado = codigo` (linha 44 no script original) para que o `ultimoCodigoRegistrado` seja atualizado a cada inserção, permitindo que o script adicione apenas novos registros de forma incremental.
  - Execute o script para adicionar novos contribuintes que surgiram desde a última execução.

## Conclusão

Este script oferece uma solução robusta para manter uma tabela auxiliar de contribuintes pessoas físicas atualizada, com um mecanismo inteligente para lidar com a população inicial e as atualizações incrementais, evitando duplicação de dados e otimizando o desempenho através do controle do `ultimoCodigoRegistrado`.