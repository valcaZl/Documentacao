# 🧾 formatCNPJ, formatCPF e formatCpfCnpj

Funções auxiliares para formatação de **CPF** e **CNPJ** brasileiros em seus respectivos padrões oficiais, aplicando separadores como ponto (`.`), hífen (`-`) e barra (`/`).

As três funções abaixo permitem tratar esses dados separadamente ou de forma unificada.

---

## 🔹 1. `formatCNPJ(String cnpj)`

Formata um CNPJ bruto (somente números) para o padrão:

📌 **`XX.XXX.XXX/XXXX-XX`**

### 🧾 Assinatura
```groovy
def String formatCNPJ(String cnpj)
```

### 📥 Parâmetro
| Nome | Tipo   | Obrigatório | Descrição                       |
|------|--------|-------------|----------------------------------|
| cnpj | String | Sim         | CNPJ com 14 dígitos numéricos.   |

### 🔁 Implementação
```groovy
def String formatCNPJ(String cnpj) {
    return cnpj.trim().take(14).replaceAll(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/) { match ->
        "${match[1]}.${match[2]}.${match[3]}/${match[4]}-${match[5]}"
    }
}
```

### ✅ Exemplo
```groovy
formatCNPJ("12332112332112")
// → 12.332.112/3321-12
```

---

## 🔹 2. `formatCPF(String cpf)`

Formata um CPF bruto para o padrão:

📌 **`XXX.XXX.XXX-XX`**

### 🧾 Assinatura
```groovy
def String formatCPF(String cpf)
```

### 📥 Parâmetro
| Nome | Tipo   | Obrigatório | Descrição                     |
|------|--------|-------------|-------------------------------|
| cpf  | String | Sim         | CPF com 11 dígitos numéricos. |

### 🔁 Implementação
```groovy
def String formatCPF(String cpf) {
    return cpf.trim().take(11).replaceAll(/(\d{3})(\d{3})(\d{3})(\d{2})/) { match ->
        "${match[1]}.${match[2]}.${match[3]}-${match[4]}"
    }
}
```

### ✅ Exemplo
```groovy
formatCPF("12332112331")
// → 123.321.123-31
```

---

## 🔹 3. `formatCpfCnpj(String cpfCnpj)`

Função **inteligente** que detecta automaticamente se a string recebida é um CPF (11 dígitos) ou um CNPJ (14 dígitos), e formata adequadamente.

### 🧾 Assinatura
```groovy
def String formatCpfCnpj(String cpfCnpj)
```

### 📥 Parâmetro
| Nome     | Tipo   | Obrigatório | Descrição                                    |
|----------|--------|-------------|-----------------------------------------------|
| cpfCnpj  | String | Sim         | Sequência numérica com 11 (CPF) ou 14 (CNPJ). |

### 🔁 Implementação
```groovy
def String formatCpfCnpj(String cpfCnpj) {
    if(cpfCnpj.trim().size() == 11) {
        return cpfCnpj.trim().take(11).replaceAll(/(\d{3})(\d{3})(\d{3})(\d{2})/) { match ->
            "${match[1]}.${match[2]}.${match[3]}-${match[4]}"
        }
    } else if (cpfCnpj.trim().size() == 14) {
        return cpfCnpj.trim().take(14).replaceAll(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/) { match ->
            "${match[1]}.${match[2]}.${match[3]}/${match[4]}-${match[5]}"
        }
    } else {
        return cpfCnpj;
    }
}
```

### ✅ Exemplos
```groovy
formatCpfCnpj("12345678910")
// → 123.456.789-10

formatCpfCnpj("12345678910123")
// → 12.345.678/9101-23
```

---

## 💬 Observações gerais

- Nenhuma das funções valida se o CPF ou CNPJ é **real ou válido**, apenas aplica a **máscara de formatação**.
- As funções usam `.trim()` para ignorar espaços antes/depois.
- O uso de `.take(n)` garante que apenas os dígitos esperados (11 ou 14) sejam utilizados.
- Para garantir funcionamento correto, **limpe a string** antes de passar como parâmetro, se necessário:

```groovy
cpfCnpj.replaceAll(/\D/, "") // remove tudo que não for número
```

---

## 📂 Origem

Funções utilitárias Groovy para padronização de documentos brasileiros em fontes dinâmicas, scripts e relatórios.
