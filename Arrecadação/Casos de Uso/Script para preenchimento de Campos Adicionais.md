## 📄 Script para preenchimento de campos adicionais.

📥 Este script utiliza de uma função interna do sistema, para preenchimento de campos adicionais sem a necessidade de utilização de API REST.


---

## 🧠 Código Completo

```groovy
//-------------------------------------------Fontes---------------------------------------------//
fonteCampoAdicional = Dados.tributos.v2.imovel.campoAdicional;
fonteImoveis = Dados.tributos.v2.imoveis;
filtroImoveis = "codigo in ()"
dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis,campos: "id")

//-------------------------------------------Percorrer-------------------------------------------//
percorrer (dadosImoveis) { itemImoveis ->

//-------------------------------------------Layout----------------------------------------------//
  conteudo = [
    idImovel : ID,
    nomeCampo : "NOMECAMPO",
    valor : VALOR,
    ano : ANO
  ]

//-------------------------------------------Envio-----------------------------------------------//
  envio = Dados.tributos.v2.imovel.campoAdicional.preenche(conteudo: conteudo) 
}
---

```
## 🔍 Explicações das Funções

### 🔄 `FONTES`

        ➡️ Fontes do banco de dados utilizadas para buscar a informação e alimentar a variavel idImovel com os IDs necessarios para alteração.

### 🔄 `nomeCampo`

        ➡️ Nome do campo adicional que deseja alterar.

        
### 🔄 `valor`

        ➡️ Valor inserido no campo adicional, pode ser numeral ou escrito com "".

        ⚠️ Para campos adicionais com Opção, utilizar o ID da opção.


### 🔄 `ano`
  
        ➡️ Ano que deseja inserir a informação no banco de dados.
