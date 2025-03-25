# ⚡ Estruturas Condicionais no BFC-SCRIPT

As estruturas condicionais são fundamentais para a lógica de programação, permitindo a execução de diferentes blocos de código com base em condições específicas. No **BFC-SCRIPT** podemos utilizar `se` e `senao`; em **GROOVY** podemos utilizar `if`, `else` e o **operador ternário** para estruturar essas decisões de forma clara e eficiente.

## 🔀 `if` e `else`

A estrutura `if` e `else` é usada para executar um bloco de código apenas se determinada condição for verdadeira. Caso contrário, um segundo bloco de código pode ser executado.

## 🎭 O Operador Ternário
O operador ternário é uma forma mais compacta de escrever estruturas condicionais simples. Ele segue a sintaxe:

```bfc-script
variavel = (condicao) ? valor_se_verdadeiro : valor_se_falso
```

### 💡 Exemplo de Uso:

```bfc-script
esquema = [
  id: Esquema.numero,
  nome: Esquema.caracter,
  codigo: Esquema.caracter
]

fonte = Dados.dinamico.v2.novo(esquema);
fonteContribuintes = Dados.tributos.v2.contribuintes;

p_tipoPessoa = parametros.tipoPessoa?.selecionado?.valor

linha = []

if (p_tipoPessoa){
  filtroContribuintes = "tipoPessoa = '${p_tipoPessoa}'"
  dadosContribuintes = fonteContribuintes.busca(criterio: filtroContribuintes,campos: "id, codigo, nome")
} else{
  dadosContribuintes = fonteContribuintes.busca(campos: "id, codigo, nome")
}

percorrer (dadosContribuintes) { itemContribuintes ->  
  linha = [
    id: itemContribuintes.id,
    nome: itemContribuintes.nome,
    codigo: itemContribuintes.codigo
  ]
  
  imprimir linha
  
  fonte.inserirLinha(linha)
}
retornar fonte
```

## ⚡ Explicação do Código
- **Definição do esquema**: Cria os campos `id`, `nome` e `codigo`.
- **Criação da fonte de dados**: Inicializa uma fonte dinâmica.
- **Recuperação do parâmetro**: Obtém `tipoPessoa`, garantindo que o valor não seja `null` antes de acessá-lo (`?.`).
- **Uso do `if` e `else`**: 
  - Se `p_tipoPessoa` estiver definido, aplica um filtro para buscar apenas os contribuintes do tipo informado.
  - Caso contrário, busca todos os contribuintes sem filtro.
- **Laço de repetição**: Percorre os dados obtidos e insere na fonte dinâmica.
