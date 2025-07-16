# 🏗️ Utilização de Múltiplas Fontes no BFC-SCRIPT

Ao desenvolver relatórios no **BFC-SCRIPT**, muitas vezes é necessário utilizar múltiplas fontes de dados para obter informações completas. Para isso, precisamos identificar um **campo em comum** entre as fontes para que os dados possam ser relacionados corretamente.

## 🔗 Relacionando Fontes de Dados

No exemplo abaixo, utilizamos **duas fontes de dados distintas**:
- `imoveis.busca`: Traz informações dos imóveis.
- `imoveisCamposAdicionais.busca`: Obtém os campos adicionais do cadastro de imóveis.

O campo em comum entre essas fontes é **`idImovel`**. No caso da fonte `imoveis`, esse campo é representado por `id`, enquanto na fonte `camposAdicionais` ele é referenciado como `idImovel`. Isso permite que os dados das duas fontes sejam conectados e processados simultaneamente.

## 💡 Exemplo de Uso

```bfc-script
esquema = [
  id: Esquema.numero,
  nome: Esquema.caracter,
  codigo: Esquema.caracter,
  tipoConstrucao: Esquema.caracter,
  testeFELIPE: Esquema.caracter
]

p_situacao = parametros.situacao?.selecionado?.valor  // Parâmetro opcional, pode não estar presente

fonte = Dados.dinamico.v2.novo(esquema);
fonteImoveis = Dados.tributos.v2.imoveis;

// Inicialização das variáveis
idImovel        = 0
codigoImovel    = 0
responsavelNome = ''
tipoConstrucao  = ''
testeFELIPE     = ''
linha           = []

// Verifica se o parâmetro 'situacao' foi informado para aplicar filtro
if (p_situacao){
  filtroImoveis = "situacao = '${p_situacao}'"
  dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis,campos: "id, codigo, responsavel(nome)").take(10)
} else{
  dadosImoveis = fonteImoveis.busca(campos: "id, codigo, responsavel(nome)").take(10)   
}

// Percorre os imóveis encontrados
percorrer (dadosImoveis) { itemImoveis ->
  
  // Define o filtro para buscar os campos adicionais do imóvel
  filtroCamposAdicionais = "idImovel = ${itemImoveis.id} and ano = 2025"
  
  // Busca os campos adicionais relacionados ao imóvel
  dadosCamposAdicionais = Dados.tributos.v2.imoveis.camposAdicionais.busca(criterio: filtroCamposAdicionais, campos: "vlCampo, texto, opcoes, areaTexto, dhCampo")
  
  // Percorre os campos adicionais e associa os valores às variáveis correspondentes
  percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
    idImovel        = itemImoveis.id
    codigoImovel    = itemImoveis.codigo
    responsavelNome = itemImoveis.responsavel.nome
    tipoConstrucao  = itemCamposAdicionais.opcoes  // Informação da construção
    testeFELIPE     = itemCamposAdicionais.texto   // Informação complementar
  }  
  
  // Monta a linha com os dados coletados
  linha = [
    idImovel         : idImovel,
    codigoImovel     : codigoImovel,
    responsavelNome  : responsavelNome,
    tipoConstrucao   : tipoConstrucao,
    testeFELIPE      : testeFELIPE
  ]
  
  // Insere a linha na fonte dinâmica
  fonte.inserirLinha(linha)
  
  // Imprime a linha para depuração
  imprimir linha
}

// Retorna a fonte dinâmica com os dados coletados
retornar fonte
```

## 📌 Explicação do Código

1. **Definição do esquema**: Criamos os campos que serão armazenados na fonte dinâmica.
2. **Recuperação do parâmetro `situacao`**: Como esse parâmetro não é obrigatório, utilizamos `?.` para evitar erros caso ele não esteja definido.
3. **Busca de imóveis**:
   - Se `situacao` estiver definido, aplicamos um filtro para buscar apenas os imóveis com essa condição.
   - Caso contrário, buscamos todos os imóveis sem restrição.
4. **Percorrendo os imóveis**:
   - Para cada imóvel encontrado, buscamos seus **campos adicionais** utilizando o `id` do imóvel como filtro.
   - Esses dados são armazenados nas variáveis `tipoConstrucao` e `testeFELIPE`.
5. **Criação e inserção da linha na fonte**:
   - Os dados coletados são organizados em um mapa (`linha`) e inseridos na fonte dinâmica.
   - A linha é impressa para depuração.

## 🎯 Conclusão

Utilizando múltiplas fontes de dados no **BFC-SCRIPT**, conseguimos enriquecer os relatórios com informações complementares. A chave para integrar corretamente os dados é garantir que exista um **campo comum** entre as fontes, permitindo que sejam percorridas e relacionadas corretamente. 🚀
