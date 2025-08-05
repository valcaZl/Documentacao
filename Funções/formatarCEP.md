# 🏷️ formatCEP

Formata um CEP brasileiro, aplicando o hífen entre o quinto e sexto dígitos.

---

### 🧾 Assinatura

```groovy
String formatCEP(String cep)
```

---

### 📥 Parâmetros

| Nome | Tipo   | Obrigatório | Descrição                        |
|------|--------|-------------|---------------------------------|
| cep  | String | Sim         | CEP contendo 8 dígitos numéricos |

---

### 📤 Retorno

| Tipo   | Descrição                       |
|--------|--------------------------------|
| String | CEP formatado no padrão `XXXXX-XXX` |

---

### 🧬 Implementação

```groovy
/*
Recebe um CEP e formata adicionando o '-'
*/
def String formatCEP(String cep) {
    // cep: deve conter 8 caracteres numéricos
    return cep.trim().take(8).replaceAll(/(\d{5})(\d{3})/) { match ->
        "${match[1]}-${match[2]}"
    }
}
```

Esta função recebe uma string numérica que representa um CEP (Código de Endereçamento Postal) brasileiro.  
Primeiro, ela remove espaços em branco extras com `.trim()` e garante que a string tenha no máximo 8 caracteres com `.take(8)`.  
Depois, usa uma expressão regular para dividir o CEP em dois grupos: os primeiros 5 dígitos e os últimos 3 dígitos, e insere um hífen (`-`) entre eles.  
Assim, converte o CEP para o formato padrão `XXXXX-XXX`.

---

### 🧪 Exemplo de uso

```groovy
formatCEP("77741526")
```

---

### ✅ Resultado esperado

```
77741-526
```

---

### 💬 Observações

- A função espera uma string contendo **apenas números**; se tiver outros caracteres, limpe antes usando `.replaceAll(/\D/, "")`.  
- Não valida se o CEP existe, apenas formata o texto.  
- Usa `.trim()` para evitar erros causados por espaços extras.  
- `.take(8)` protege contra entradas maiores que 8 caracteres.  

---

### 📂 Origem

Função utilitária para formatação de CEPs em scripts Groovy para fontes dinâmicas e relatórios.