# 🧾 Leitura de Arquivo CSV para Preenchimento de Campos Adicionais no BFC-SCRIPT

Este script tem como objetivo realizar a **leitura de arquivos CSV** e utilizar seus dados para **preencher automaticamente campos adicionais** no sistema de tributos, como o **Valor Venal do Terreno**. Esse processo é útil para agilizar o cadastro em massa de informações complementares no sistema.

## 🧪 Validação de Encoding

O script testa diferentes codificações (UTF-8, ASCII, Windows-1252 e ISO-8859-1) até encontrar uma que permita ler corretamente o conteúdo do arquivo:

```bfc-script
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
```

## 📄 Leitura do CSV e Preenchimento dos Dados

Após validar o encoding, o script percorre cada linha do arquivo CSV, extrai o código do imóvel e o valor informado, e preenche um campo adicional no cadastro do imóvel correspondente.

```bfc-script
csv = validEncoding(parametros.arquivo.valor)

while(csv.contemProximaLinha()) {
  linha = csv.lerLinha().split(";")
  idImovel = linha[0]

  // Ignora cabeçalho
  if(idImovel.toString() == '"i_imoveis"' || idImovel.toString() == 'i_imoveis') {
    continue   
  }

  valorCampo = linha[1].substituir('.', '').substituir(',', '.').toBigDecimal()

  fonteImoveis = Dados.tributos.v2.imoveis
  FonteTributos = Dados.tributos.v2
  fonteCamposAdicionais = Dados.tributos.v2.imovel.camposAdicionais

  filtroImoveis = "codigo = ${idImovel} and situacao = 'DESATIVADO'"
  dadosImoveis = fonteImoveis.busca(criterio: filtroImoveis)

  percorrer (dadosImoveis) { itemImoveis ->
    conteudo = [        
      idImovel: itemImoveis.id,
      nomeCampo: 'Valor Venal do Terreno',
      valor: valorCampo,
      ano: 2025
    ]

    imprimir "qwpieu: " + itemImoveis.codigo + ' - ' + conteudo
    retorno = FonteTributos.imovel.campoAdicional.preenche(conteudo: conteudo, primeiro: true)
  }
}
```

## 📌 Explicação do Código

1. **Função `validEncoding`**: Tenta abrir o arquivo com diferentes encodings até conseguir ler uma linha válida.
2. **Ignorar cabeçalho**: Pula a primeira linha, que contém o cabeçalho do arquivo.
3. **Conversão do valor**: Transforma o número do formato brasileiro para o formato decimal padrão (`BigDecimal`).
4. **Busca do imóvel**: Apenas imóveis com `situacao = 'DESATIVADO'` e com o código informado são considerados.
5. **Preenchimento do campo adicional**: Envia os dados para a API de `campoAdicional.preenche`, registrando o valor para o ano de 2025.

## 📦 Considerações

* O foco do script é importar de forma automatizada os valores de campo adicional a partir de um CSV.
* Permite padronizar e agilizar cadastros em massa de informações complementares.
* Pode ser adaptado para aceitar mais campos, validar colunas extras ou utilizar parâmetros dinâmicos (como o ano).
* Recomendado para situações onde há muitos registros a serem inseridos com base em uma planilha externa.

---

> 🔐 **Atenção**: Certifique-se de que o usuário tenha permissão de escrita sobre os imóveis e campos adicionais antes de executar este script.

---

Se desejar expandir este exemplo para incluir outros campos adicionais, múltiplos anos ou lógicas condicionais, entre em contato com o time de desenvolvimento.
