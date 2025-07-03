---

# Geração de Certidão Negativa de Débitos com Avaliação de Situação Fiscal

Este script realiza a geração de uma certidão negativa de débitos (CND) a partir da verificação da situação tributária de um contribuinte. O processo é estruturado para determinar a classificação da certidão com base em diversos critérios fiscais (dívidas, débitos e parcelamentos).

---

## 📋 Etapas do Processo

### 1. Definição do Esquema de Dados

Define a estrutura dos dados a serem manipulados pelo sistema dinâmico (`fonte`).

```groovy
esquema = [
  nome: Esquema.caracter,
  cpfCnpj: Esquema.caracter,
  ...
]
```

### 2. Obtenção dos Dados da Certidão

Busca os dados principais relacionados à certidão de um contribuinte via:

```groovy
resposta = Dados.tributos.v2.certidaoNegativa.busca(...)
```

### 3. Coleta de Informações do Contribuinte e Econômico

* Endereço
* Dados econômicos
* Dados do contribuinte

### 4. Consulta de Pendências Fiscais

Realiza metadados para verificar débitos, dívidas e parcelamentos:

```groovy
fonteTributos.debitos.metadados(...)
fonteTributos.dividas.metadados(...)
fonteTributos.parcelamentos.parcelas.metadados(...)
```

---

## 🔄 Classificação da Certidão

A certidão é classificada conforme as pendências encontradas:

```groovy
se(respostaDebitoVencido.quantidade > 0 || respostaDividaVencida.quantidade > 0 || respostaParcelasVencidasParcelamentos.quantidade > 0){
  classificacaoCertidao = "CERTIDAO_POSITIVA"
}senao{
  se(respostaDebitoVencer.quantidade > 0 || respostaParcelasVencerParcelamentos.quantidade > 0){
    classificacaoCertidao = "CERTIDAO_POSITIVA_COM_EFEITO_NEGATIVO"
  }senao{
    se(respostaDividaSuspensa.quantidade > 0){
      classificacaoCertidao = "CERTIDAO_POSITIVA_COM_EFEITO_NEGATIVO_SUSPENSO"
    }senao{
      classificacaoCertidao = "CERTIDAO_NEGATIVA"
    }
  }
}
```

🔍 **Observação:** A lógica encadeada de `se/senao` atua como um `switch case` implícito com diferentes condições para determinar a natureza da certidão.

---

## 📝 Geração do Texto da Certidão

Define o conteúdo textual com base na classificação determinada:

```groovy
if (classificacaoCertidao == "CERTIDAO_POSITIVA" || ...){
  textoDocumento = "...possui DÍVIDAS A VENCER..."
} else {
  textoDocumento = "...NADA DEVE..."
}
```

---

## 📄 Montagem e Retorno do Documento

Os dados são organizados em uma página e inseridos na `fonte` de dados:

```groovy
pagina = [
  nome: nome,
  cpfCnpj: cpfCnpj,
  ...
]

fonte.inserirLinha(pagina)
retornar fonte
```

---

## ✅ Conclusão

Este script é essencial para gerar certidões tributárias, utilizando condições lógicas baseadas em pendências fiscais. A construção condicional (tipo `switch`) para a classificação garante que cada situação seja corretamente avaliada e documentada.