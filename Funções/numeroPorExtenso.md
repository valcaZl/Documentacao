# 🔢 Conversão de Valores Numéricos para Extenso no BFC-SCRIPT

Ao gerar documentos como certidões ou guias de pagamento, é comum a necessidade de apresentar valores monetários por extenso. A função abaixo converte um valor numérico (com ou sem centavos) em sua representação textual completa, respeitando a gramática da língua portuguesa.

---

## 🧠 Lógica Geral da Função

A função `valor_extenso` recebe um valor numérico (ex: `1234.56`) e retorna a string correspondente ao valor por extenso (ex: *"mil duzentos e trinta e quatro reais e cinquenta e seis centavos"*). Ela considera:

* Separação entre parte inteira e decimal;
* Casos especiais como "cem" ao invés de "cento";
* Diferença entre singular e plural ("milhão" vs. "milhões");
* Montantes de até 999 trilhões;
* Formatação de centavos (ex: 0,01 → "um centavo").

---

## 🧾 Exemplo de Uso

```bfc-script
def extenso = valor_extenso(1234.56)
imprimir extenso // Saída: "mil duzentos e trinta e quatro reais e cinquenta e seis centavos"
```

---

## 🧩 Estrutura Interna do Código

```bfc-script
def valor_extenso = { valor ->
  def vlr = 0
  if (valor != null) {
    vlr = Numeros.absoluto(valor)
  }
  if (vlr == 0){
    return "zero"
  }

  long inteiro = Math.abs(vlr).toLong()
  double resto = vlr - inteiro

  String vlrS = String.valueOf(inteiro)
  if (vlrS.length() > 15){ return("Erro: valor superior a 999 trilhões.") }

  s = ""
  centavos = String.valueOf(Math.round(resto * 100))

  String[] unidade = [...]
  String[] centena = [...]
  String[] dezena = [...]
  String[] qualificaS = ["", "mil", "milhão", "bilhão", "trilhão"]
  String[] qualificaP = ["", "mil", "milhões", "bilhões", "trilhões"]

  // Laço principal para processar cada grupo de milhar
  while (!vlrS.equals("0")) {
    // Separa e processa grupos de 3 dígitos...
    // Constrói trecho textual para cada grupo
    // Define qualificador correto (mil, milhão, etc.)
  }

  // Complementa com centavos
  if (!centavos.equals("0")) {
    // Lógica de extenso para centavos
  }

  return(s)
}
```

---

## 🧠 Considerações Técnicas

1. **Segmentação**: Divide o número em blocos de três dígitos da direita para a esquerda (centenas, milhares, milhões etc.).
2. **Qualificadores**: Usa plural/singular dependendo do número (ex: "milhão" ou "milhões").
3. **Tratamento especial para "100"**: Escrito como "cem" se estiver isolado.
4. **Centavos**: Se o valor tiver parte decimal, é lida separadamente.
5. **Limite**: A função não aceita valores com mais de 15 dígitos inteiros (maior que 999 trilhões).

---

## 📌 Conclusão

Essa função é essencial para garantir clareza e conformidade legal em documentos fiscais, permitindo a exibição de valores por extenso de forma automatizada no **BFC-SCRIPT**. Ela pode ser facilmente adaptada para outros idiomas ou formatos se necessário. ✅
