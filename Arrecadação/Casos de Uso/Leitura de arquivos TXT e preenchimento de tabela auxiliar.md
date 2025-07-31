## 📄 Script para Leitura de arquivos em formato TXT e preenchimento de tabela auxiliar dentro do sistema.

---

## 🧠 Código Completo

```groovy
//-------------------------------------------PARAMETROS-------------------------------------------//
paramArquivo = parametros.arquivo.valor
fonteTributos = Dados.tributos.v2
arquivo = Arquivo.ler(paramArquivo, 'txt');

//-------------------------------------------LAYOUT-------------------------------------------//
percorrer(enquanto: { arquivo.contemProximaLinha() }) {
  linha  = arquivo.lerLinha().dividir(~/\|/)
  dados = [
    campo1 : linha[1],
    campo2 : linha[4]
  ]
  tentar{
    retorno = fonteTributos.tabelaAuxiliar.registros.cria(parametros: [codigoTabelaAuxiliar: 20], conteudo: dados)
  }tratar{
    esperar 2.segundo 
    retorno = fonteTributos.tabelaAuxiliar.registros.cria(parametros: [codigoTabelaAuxiliar: 20], conteudo: dados)
  }
}
---

```
## 🔍 Explicações das Funções

### 🔄 `PARAMETROS`

        ➡️ Parametrização do arquivo para leitura em TXT.

        ⚠️ Caso o arquivo esteja em outro formato, é possivel a alteração nesta parametrização, porem, sera necessario alteração no layout da leitura.

### 🔄 `LAYOUT`

        ➡️ Local onde é delimitado os campos da leitura e suas divisões, para em seguida alimentar em uma tabela auxiliar a sua escolha.
