# 📞 formatTelefone

Formata um número de telefone brasileiro (com DDD), aplicando parênteses e hífen.

Suporta números com **10 ou 11 dígitos**, retornando o valor no formato:

- 📱 **(XX) XXXXX-XXXX** → para celulares (11 dígitos)  
- ☎️ **(XX) XXXX-XXXX** → para fixos (10 dígitos)

---

### 📟 Assinatura

```groovy
String formatTelefone(String numero)
```

---

### 📅 Parâmetros

| Nome    | Tipo   | Obrigatório | Descrição                                                     |
|---------|--------|-------------|----------------------------------------------------------------|
| numero  | String | Sim         | Número contendo apenas os dígitos (com DDD). Aceita 10 ou 11 dígitos. |

---

### 📄 Retorno

| Tipo   | Descrição                                                                 |
|--------|--------------------------------------------------------------------------|
| String | Número formatado com DDD entre parênteses e separador `-` entre blocos.  |

- Se o número tiver **11 dígitos**, aplica o padrão: `(XX) XXXXX-XXXX`
- Se o número tiver **10 dígitos**, aplica o padrão: `(XX) XXXX-XXXX`
- Se não tiver 10 ou 11 dígitos, retorna o valor **sem alterações**

---

### 🧬 Implementação

```groovy
def String formatTelefone(String numero){
    // Remove espaços em branco antes/depois
    numero = numero.trim()

    if (numero.size() == 11) {
        // Formato celular: (XX) XXXXX-XXXX
        return numero.replaceAll(/(\d{2})(\d{5})(\d{4})/) { match ->
            "(${match[1]}) ${match[2]}-${match[3]}"
        }
    } else if (numero.size() == 10) {
        // Formato fixo: (XX) XXXX-XXXX
        return numero.replaceAll(/(\d{2})(\d{4})(\d{4})/) { match ->
            "(${match[1]}) ${match[2]}-${match[3]}"
        }
    } else {
        // Número fora do padrão
        return numero
    }
}
```

---

### 🥪 Exemplo de uso

```groovy
formatTelefone("48998567382")
formatTelefone("4832651234")
formatTelefone("998567382")
```

---

### ✅ Resultado esperado

```groovy
(48) 99856-7382
(48) 3265-1234
998567382
```

---

### 💬 Observações

- A função **não limpa** caracteres especiais. Ela espera uma string contendo **apenas números**.
- Se necessário, utilize `.replaceAll(/\D/, "")` antes de passar para a função, para remover pontos, traços, espaços, etc.
- Números com menos de 10 ou mais de 11 dígitos são retornados **sem formatação**.

---

### 📂 Origem

Função auxiliar para formatação de dados em scripts Groovy utilizados em fontes dinâmicas, extensões ou relatórios.
