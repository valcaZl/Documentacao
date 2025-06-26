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
  
  long inteiro = Math.abs(vlr).toLong() // parte inteira do valor
  double resto = vlr - inteiro       // parte fracionária do valor
  
  String vlrS = String.valueOf(inteiro)
  
  if (vlrS.length() > 15){
    return("Erro: valor superior a 999 trilhões.")
  }
  
  s = ""
  centavos = String.valueOf(Math.round(resto * 100))
  
  String[] unidade = ["", "um", "dois", "três", "quatro", "cinco",
                      "seis", "sete", "oito", "nove", "dez", "onze",
                      "doze", "treze", "quatorze", "quinze", "dezesseis",
                      "dezessete", "dezoito", "dezenove"]
  
  String[] centena = ["", "cento", "duzentos", "trezentos",
                      "quatrocentos", "quinhentos", "seiscentos",
                      "setecentos", "oitocentos", "novecentos"]
  String[] dezena = ["", "", "vinte", "trinta", "quarenta", "cinquenta",
                     "sessenta", "setenta", "oitenta", "noventa"]
  
  String[] qualificaS = ["", "mil", "milhão", "bilhão", "trilhão"]
  
  String[] qualificaP = ["", "mil", "milhões", "bilhões", "trilhões"]
  
  // definindo o extenso da parte inteira do valor
  int n, unid, dez, cent, tam, i = 0
  
  boolean umReal = false, tem = false
  
  while (!vlrS.equals("0")){
    tam = vlrS.length()
    
    // retira do valor a 1a. parte, 2a. parte, por exemplo, para 123456789:
    // 1a. parte = 789 (centena)
    // 2a. parte = 456 (mil)
    // 3a. parte = 123 (milhões)
    if (tam > 3){
      vlrP = vlrS.substring(tam-3, tam)
      vlrS = vlrS.substring(0, tam-3)
    }
    
    else { // última parte do valor
      vlrP = vlrS
      vlrS = "0"
    }
    if (!vlrP.equals("000")) {
      saux = ""
      if (vlrP.equals("100"))
      saux = "cem"
      else {
        n = Integer.parseInt(vlrP, 10)  // para n = 371, tem-se:
        cent = n / 100                  // cent = 3 (centena trezentos)
        dez = (n % 100) / 10            // dez  = 7 (dezena setenta)
        unid = (n % 100) % 10           // unid = 1 (unidade um)
        if (cent != 0)
        saux = centena[cent]
        if ((n % 100) <= 19) {
          if (saux.length() != 0)
          saux = saux + " e " + unidade[n % 100]
          else saux = unidade[n % 100]
        }
        else {
          if (saux.length() != 0)
          saux = saux + " e " + dezena[dez]
          else saux = dezena[dez]
          if (unid != 0) {
            if (saux.length() != 0)
            saux = saux + " e " + unidade[unid]
            else saux = unidade[unid]
          }
        }
      }
      if (vlrP.equals("1") || vlrP.equals("001")) {
        if (i == 0) // 1a. parte do valor (um real)
        umReal = true
        else saux = saux + " " + qualificaS[i]
      }
      else if (i != 0)
      saux = saux + " " + qualificaP[i]
      if (s.length() != 0)
      s = saux + ", " + s
      else s = saux
    }
    
    if (((i == 0) || (i == 1)) && s.length() != 0)
    tem = true // tem centena ou mil no valor
    i = i + 1  // próximo qualificador: 1- mil, 2- milhão, 3- bilhão, ...
  }
  
  if (s.length() != 0) {
    if (umReal) {
      s = s + " real"
    } else if (tem) {
      s = s + " reais"
    } else { s = s + " de reais" }
  }
  
  // definindo o extenso dos centavos do valor
  if (!centavos.equals("0")) { // valor com centavos
    if (s.length() != 0) // se não é valor somente com centavos
    s = s + " e "
    if (centavos.equals("1"))
    s = s + "um centavo"
    else {
      n = Integer.parseInt(centavos, 10)
      if (n <= 19)
      s = s + unidade[n]
      else {             // para n = 37, tem-se:
        unid = n % 10    // unid = 37 % 10 = 7 (unidade sete)
        dez = n / 10     // dez  = 37 / 10 = 3 (dezena trinta)
        s = s + dezena[dez]
        if (unid != 0)
        s = s + " e " + unidade[unid]
      }
      s = s + " centavos"
    }
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
