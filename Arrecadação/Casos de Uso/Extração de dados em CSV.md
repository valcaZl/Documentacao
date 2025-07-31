## 📄 Script para Extração de dados em CSV



---

## 🧠 Código Completo

```groovy
//-------------------------------------------Fontes-------------------------------------------//
fontePessoa = Dados.gestaoFiscal.v1.pessoa;
arquivo = Arquivo.novo("PessoasGestao", 'csv', [delimitador: ';', entreAspas: 'N', encoding: 'iso-8859-1']);

dadosPessoa = fontePessoa.busca(campos: "id, nome, cpfCnpj")
arquivo.escrever('idContribuinte:'); arquivo.escrever('NomeContribuinte:'); arquivo.escrever('CpfCnpj:');
arquivo.novaLinha()

//-------------------------------------------Percorrer-------------------------------------------//
percorrer (dadosPessoa) { itemPessoa ->
    arquivo.escrever(itemPessoa.id); arquivo.escrever(itemPessoa.nome); arquivo.escrever(itemPessoa.cpfCnpj);
    arquivo.novaLinha()
  
}
//-------------------------------------------Retorno-------------------------------------------//
Resultado.arquivo(arquivo)

---

```
## 🔍 Explicações das Funções

### 🔄 `FONTES`

        ➡️ Fontes do banco de dados utilizadas para buscar a informação e alimentar o arquivo com os dados para extração.

        
### 🔄 `Arquivo.novo`

        ➡️ Nesta linha é delimitado o nome do arquivo e o formato ao qual ele será gerado, neste caso CSV. 
        ⚠️ Caso precise de um arquivo em TXT, basta alterar nesta linha o formato.
