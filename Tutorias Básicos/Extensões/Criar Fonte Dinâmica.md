# 📌 Conceitos Básicos para o Desenvolvimento de Fontes Dinâmicas

As **fontes dinâmicas** são uma das ferramentas disponíveis no **Studio Extensões**. Sua principal utilidade é atuar como um **backend** para o desenvolvimento de relatórios, sejam eles padrões ou customizados. Todo relatório depende de fontes dinâmicas para buscar informações no banco de dados utilizado.

## 🔍 O que é uma Fonte Dinâmica?

Assim como os scripts, a fonte dinâmica utiliza por padrão a linguagem **BFC-SCRIPT**. O **BFC-SCRIPT** é um framework que possibilita a integração de scripts com aplicações. Ele oferece um ambiente de desenvolvimento, compilação e execução de scripts, além de uma linguagem acessível para usuários não técnicos.

## 🖥️ Características do BFC-SCRIPT

- Sintaxe similar ao Java.
- Suporte a operadores lógicos, comparação, atribuição e aritméticos.
- Uso de chaves `{}` para circundar blocos de código.
- **Case-sensitive** (diferencia letras maiúsculas e minúsculas).
- Não requer ponto e vírgula (`;`) ao final das instruções.
- Comandos em português, facilitando o uso por usuários sem experiência em programação.

Para mais informações sobre a linguagem, consulte a documentação oficial: [BFC-SCRIPT 2.7.X](https://test.betha.com.br/documentacao/bfc-script/2.7.X/index.html).

## 📑 Estrutura Padrão de uma Fonte Dinâmica

Antes de desenvolver um relatório, é necessário construir o **backend**. A estrutura básica para criar uma fonte dinâmica é a seguinte:

```bfc-script
# Define a estrutura dos dados que serão armazenados na fonte dinâmica
esquema = [
  id: Esquema.numero,    # Campo numérico para identificar cada registro
  nome: Esquema.caracter, # Campo de texto para armazenar o nome
  codigo: Esquema.caracter # Campo de texto para armazenar o código
]

# Cria a fonte dinâmica baseada no esquema definido acima
fonte = Dados.dinamico.v2.novo(esquema);

# Define a origem dos dados, que será a fonte de contribuintes
fonteContribuintes = Dados.tributos.v2.contribuintes;

# Obtém o valor do parâmetro selecionado para filtrar os contribuintes
p_tipoPessoa = parametros.tipoPessoa.selecionado.valor

# Inicializa uma lista vazia para armazenar os registros antes de inseri-los na fonte
linha = []

# Define um critério de busca para filtrar os contribuintes pelo tipo de pessoa
filtroContribuintes = "tipoPessoa = '${p_tipoPessoa}'"

# Realiza a busca dos contribuintes aplicando o filtro definido e limitando a 10 registros
dadosContribuintes = fonteContribuintes.busca(criterio: filtroContribuintes,campos: "id, codigo, nome").take(10)

# Percorre os resultados obtidos
percorrer (dadosContribuintes) { itemContribuintes ->  
  # Monta a estrutura de cada linha que será inserida na fonte dinâmica
  linha = [
    id: itemContribuintes.id,
    nome: itemContribuintes.nome,
    codigo: itemContribuintes.codigo
  ]
  
  # Exibe os dados no console para conferência
  imprimir linha
  
  # Insere a linha na fonte dinâmica
  fonte.inserirLinha(linha)
}

# Retorna a fonte contendo os registros filtrados e processados
retornar fonte
```

## Explicação do Código
- **Definição do esquema**: Cria os campos `id`, `nome` e `codigo`, que representam os dados que serão manipulados.
- **Criação da fonte de dados**: Inicializa uma fonte dinâmica baseada no esquema definido.
- **Fonte de contribuintes**: Define a origem dos dados (`Dados.tributos.v2.contribuintes`).
- **Filtro**: Obtém a lista de contribuintes conforme o `tipoPessoa` selecionado pelo usuário.
- **Busca de dados**: Aplica o filtro à fonte de contribuintes e retorna um conjunto limitado de 10 registros.
- **Laço de repetição**: Percorre os dados filtrados, cria um objeto `linha` e insere cada item na fonte dinâmica.
- **Exibição no console**: Imprime cada linha para conferência.
- **Retorno da fonte**: A função retorna a fonte contendo os dados processados, prontos para serem utilizados no relatório.

📌 **Observação:** A estrutura pode variar conforme a necessidade do relatório e a complexidade da extração de dados.
