# 📄 Exportação de Imóveis com Campos Adicionais no BFC-SCRIPT

Este script tem como objetivo gerar um arquivo CSV contendo informações detalhadas sobre os imóveis, enriquecidas com dados dos **campos adicionais**. A funcionalidade central é a **extração estruturada de atributos** por meio de um `switch case`, que associa dinamicamente os títulos dos campos adicionais às propriedades do imóvel.

---

## 🧭 Etapas do Script

1. **Busca de Imóveis**: Utiliza um filtro opcional por código e obtém uma lista de imóveis com atributos principais.
2. **Mapeamento Inicial**: Cria um `map` com os imóveis e inicializa os campos adicionais como vazios.
3. **Busca de Campos Adicionais**: Para os imóveis encontrados, busca os valores de campos adicionais como "Valor Venal", "Uso", "Área do Lote", etc.
4. **Switch Case**: Responsável por atualizar dinamicamente os campos do `map` de imóveis com base no título de cada campo adicional.
5. **Geração de Arquivo CSV**: Escreve todos os dados mapeados em um arquivo `.csv`, pronto para exportação.

---

## 🔀 Switch Case: Mapeamento Inteligente de Campos

A estrutura `switch case` do Groovy é usada aqui para avaliar o título do campo adicional e, com base nisso, atualizar a propriedade correspondente do imóvel dentro do mapa. Veja o trecho abaixo:

```groovy
switch(itemCamposAdicionais.campoAdicional.titulo){
  case "VALOR VENAL DO TERRENO": 
    mapImoveis[itemCamposAdicionais.idImovel].valorVenal = itemCamposAdicionais.vlCampo
    break
  case "Utilização": 
    mapImoveis[itemCamposAdicionais.idImovel].uso = itemCamposAdicionais.opcoes
    break
  case "Tipo": 
    mapImoveis[itemCamposAdicionais.idImovel].tipo = itemCamposAdicionais.opcoes
    break
  case "AREA DO LOTE": 
    mapImoveis[itemCamposAdicionais.idImovel].areaLote = itemCamposAdicionais.vlCampo
    break
  case "AREA TOTAL CONSTRUIDA": 
    mapImoveis[itemCamposAdicionais.idImovel].areaConstruida = itemCamposAdicionais.vlCampo
    break
  case "VALOR VENAL DO IMOVEL": 
    mapImoveis[itemCamposAdicionais.idImovel].valortTotalImovel = itemCamposAdicionais.vlCampo
    break
}
```

Essa abordagem torna o código mais legível, organizado e escalável, permitindo a inclusão de novos tipos de campos com facilidade.

---

## 📁 Estrutura do Arquivo CSV

As colunas do arquivo incluem:

* Código do imóvel
* Unidade
* Tipo do imóvel
* Matrícula
* Informações de endereço
* Inscrição imobiliária
* Valor venal
* Uso
* Área do lote
* Área construída
* Valor total do imóvel

---

## ✅ Considerações Finais

* O `switch case` é essencial para transformar dinamicamente os dados dos campos adicionais em colunas úteis no relatório.
* A separação das buscas (imóveis e campos adicionais) melhora o desempenho e organização.
* A estrutura com `mapImoveis` permite montar facilmente um relatório consolidado, linha a linha.

---

> 💡 **Dica**: Esse padrão pode ser reutilizado para outros módulos, como dados econômicos ou empresas, bastando adaptar os campos e filtros.
