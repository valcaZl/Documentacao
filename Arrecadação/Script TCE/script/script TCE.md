# 📄 Validação de Encoding e Geração de CSV com Informações de Imóveis

Este script foi desenvolvido para processar um arquivo CSV de entrada com inscrições imobiliárias, validar seu encoding, buscar os dados correspondentes em fontes tributárias e gerar um novo arquivo CSV contendo informações detalhadas dos imóveis, como município, CPF e nome do titular, valor venal, situação atual, entre outros.

---

## 🧠 Código Completo

```groovy
def validEncoding (archive) {
  encodingsList = ['UTF-8', 'ASCII', 'Windows-1252', 'ISO-8859-1']
  for (def encoding in encodingsList) {
    validArchive = Arquivo.ler(archive, 'csv', [encoding: encoding])
    try {
      if (validArchive.contemProximaLinha()) return validArchive
    } catch(ignore) {}
  }

  message = "O encoding do arquivo solicitado não é suportado pelo script para a importação."
  Notificacao.nova(message).para(usuario.id).enviar()
  suspender message
}

def String formatValor(BigDecimal valorInicial) {
  def valor = String.format("%.2f", valorInicial).replace('.', ',')
  
  def partes = valor.split(',')
  def parteInteira = partes[0]
  def parteDecimal = partes[1]
  def parteInteiraInvertida = parteInteira.reverse()
  def parteInteiraComPontos = parteInteiraInvertida.replaceAll(/(\d{3})/, '$1.').reverse()

  if (parteInteiraComPontos.startsWith('.')) {
    parteInteiraComPontos = parteInteiraComPontos.substring(1)
  }

  def valorFormatado = "R\$${parteInteiraComPontos},${parteDecimal}"
  return valorFormatado
}

arquivo = Arquivo.novo('imoveis' + Datas.formatar(Datas.hoje(), 'yyyy_MM_dd')+'.csv', 'csv', [encoding: 'UTF-8', delimitador: ";"]);

cabecalho = ['Município imovel', 'Inscrição imobiliária', 'CPF titular', 'Nome titular', 'valor venal em 2024', 'Situação atual', 'Observação']
arquivo.escrever(cabecalho.join(';'))
arquivo.novaLinha()

csv =  validEncoding(parametros.arquivo.valor)
while(csv.contemProximaLinha()) {
  linha = csv.lerLinha().split(";")
  inscricaoImobiliaria = linha[1]

  if(inscricaoImobiliaria.toString() == ' Inscrição imobiliária'||inscricaoImobiliaria.toString() == 'Inscrição imobiliária '){
    continue   
  }
  imprimir "inscricaoImobiliaria: " + inscricaoImobiliaria

  fonteImoveis = Dados.tributos.v2.imoveis;
  filtroImoveis = "inscricaoImobiliariaFormatada = '${inscricaoImobiliaria}' or inscricaoIncra = '${inscricaoImobiliaria}'"
  dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis)

  percorrer (dadosImoveis) { itemImoveis ->
    valorVenal = 0
    fonteCamposAdicionais = Dados.tributos.v2.imovel.camposAdicionais;
    filtroCamposAdicionais = "campoAdicional.titulo = 'VALOR VENAL DO IMÓVEL'"
    dadosCamposAdicionais = fonteCamposAdicionais.busca(criterio: filtroCamposAdicionais,parametros:["idImovel":itemImoveis.id])

    percorrer (dadosCamposAdicionais) { itemCamposAdicionais ->
      valorVenal = itemCamposAdicionais.vlCampo
    }

    imprimir itemImoveis
    linhadoArquivo = []
    linhadoArquivo.add('SALTINHO');
    linhadoArquivo.add(itemImoveis.inscricaoImobiliariaFormatada);
    linhadoArquivo.add(itemImoveis.responsavel.cpfCnpj);
    linhadoArquivo.add(itemImoveis.responsavel.nome);
    linhadoArquivo.add(formatValor(valorVenal));
    linhadoArquivo.add(itemImoveis.situacao.valor);

    arquivo.escrever(linhadoArquivo.join(';'))
    arquivo.novaLinha()
  }
}

Resultado.arquivo(arquivo)
```

---

## 🔍 Explicações das Funções

### 🔄 `validEncoding(archive)`

📥 Função que tenta ler o arquivo CSV em diversos formatos de encoding (`UTF-8`, `ASCII`, `Windows-1252`, `ISO-8859-1`).
✅ Retorna o primeiro formato válido.
⚠️ Caso nenhum funcione, notifica o usuário e suspende a execução.

---

### 💰 `formatValor(BigDecimal valorInicial)`

💵 Formata o número decimal recebido para o padrão monetário brasileiro.
➡️ Exemplo: `1234.56` vira `R$1.234,56`.

---

### 📂 Criação do Arquivo de Saída

```groovy
arquivo = Arquivo.novo(...)
```

📝 Cria um arquivo CSV com o nome incluindo a data atual, utilizando UTF-8 e ponto e vírgula como delimitador.

---

### 🧾 Escrita do Cabeçalho

```groovy
cabecalho = [...]
```

🧷 Define os títulos das colunas do CSV de saída.

---

### 📑 Leitura e Processamento do CSV

```groovy
csv = validEncoding(...)
while(csv.contemProximaLinha()) {...}
```

🔁 Lê o arquivo linha a linha, ignorando cabeçalhos que possam ter sido repetidos, e imprime a inscrição para depuração.

---

### 🏠 Consulta de Dados do Imóvel

```groovy
fonteImoveis.busca(...)
```

🔎 Realiza a busca do imóvel pela inscrição usando a fonte `Dados.tributos.v2.imoveis`.
💡 Depois busca o valor venal na fonte `camposAdicionais`.

---

### ✍️ Escrita das Informações no Arquivo Final

```groovy
arquivo.escrever(...)
```

📤 Preenche os dados no arquivo CSV final linha a linha, com os campos formatados e validados.

---

### 📦 Finalização

```groovy
Resultado.arquivo(arquivo)
```

🎯 Retorna o arquivo gerado como resultado da execução do script.

---

💡 **Dica:** Esse script é muito útil para transformar um simples arquivo com inscrições em um relatório fiscal completo com dados confiáveis e formatados automaticamente. Ideal para uso em prefeituras ou instituições que lidam com tributos imobiliários!
