# 📄 Documentação: Formatação de Inscrição Imobiliária (Máscara Padrão)

Esta documentação descreve a funcionalidade da função Groovy utilizada em scripts da plataforma **Betha Sistemas** para padronizar a exibição de inscrições imobiliárias. A função aplica uma máscara específica, garantindo que cada componente do código do imóvel possua o número correto de dígitos através do preenchimento com zeros à esquerda.

---

## 📝 Descrição

A função `formatInscricaoImobiliaria` tem como objetivo receber uma string de inscrição imobiliária (geralmente separada por pontos) e formatá-la em um padrão estruturado de 6 partes:

* **Distrito**
* **Setor**
* **Quadra**
* **Lote**
* **Edificação**
* **Unidade**

Ela é essencial para garantir a integridade visual em relatórios, carnês de IPTU e consultas, onde a precisão dos dígitos de cada setor da inscrição é mandatória para a identificação correta do imóvel.

---

## 🛠️ Requisitos e Contexto

* **Plataforma:** Betha Sistemas (Módulo Tributos)
* **Aplicação:** Scripts de Relatórios, Fontes de Dados Dinâmicas ou Extensões de UI
* **Entrada:** Uma `String` contendo a inscrição separada por pontos (ex: `1.2.3.4.5.6`)
* **Saída:** Uma `String` formatada (ex: `001.02.003.0004.005.006`)

---

## 🧠 Código Completo (Groovy)

```groovy
/**
 * Formata a inscrição imobiliária para o padrão de máscara municipal.
 *
 * @param inscricao String original da inscrição imobiliária.
 * @return String formatada com preenchimento de zeros à esquerda.
 */
def String formatInscricaoImobiliaria(String inscricao) {

    if (!inscricao) {
        return inscricao
    }

    // Divide a inscrição em partes com base no ponto
    def partes = inscricao.split(/\./)

    // Verifica se a inscrição possui as 6 partes padrão
    if (partes.size() == 6) {

        return "${partes[0].padLeft(3,'0')}." +  // Distrito (3 dígitos)
               "${partes[1].padLeft(2,'0')}." +  // Setor (2 dígitos)
               "${partes[2].padLeft(3,'0')}." +  // Quadra (3 dígitos)
               "${partes[3].padLeft(4,'0')}." +  // Lote (4 dígitos)
               "${partes[4].padLeft(3,'0')}." +  // Edificação (3 dígitos)
               "${partes[5].padLeft(3,'0')}"     // Unidade (3 dígitos)
    }

    // Caso a estrutura seja diferente do esperado, retorna a string original
    return inscricao
}
```

---

## 🔍 Explicação Técnica

### ✔ Validação Inicial

A função verifica se a string não é nula ou vazia.

### ✔ Quebra de String (`split`)

Utiliza a expressão regular `/\./` para decompor a inscrição em um array de partes.

### ✔ Lógica de Preenchimento (`padLeft`)

Cada parte é tratada individualmente para atingir o tamanho fixo definido pela regra de negócio municipal.

Exemplo:

* No campo **Lote**, `partes[3].padLeft(4,'0')` transforma o valor `4` em `0004`.

### ✔ Segurança

Se a inscrição não possuir exatamente 6 partes, o script retorna o valor original para evitar erros de execução (Exceptions) ou quebra de layout inesperada.