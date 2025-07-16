# Documentação de Utilitários - CSV e Scripts Python

Este repositório foi criado para organizar e documentar o processo realizado nos chamados relacionados ao script de leitura de arquivo para busca de inscrições mobiliárias que foram solicitadas pelo TCE.

## Estrutura de Pastas

### 📁 configuração do arquivo csv
Contém exemplos e instruções sobre como configurar corretamente o arquivo enviado pelo TCE em formato `.csv` para poder utiliza-lo no script configurado na base do cliente.

### 📁 script
Registro do script para gerar a tabela com as informações solicitadas pelo TCE.

**ATENÇÃO**
**É NECESSÁRIO ALTERAR O NOME DOS CAMPOS ADICIONAIS NOS FILTROS DO SCRIPT, ASSIM COMO O NOME DA ENTIDADE NO CAMPO QUE IRÁ ENVIAR A INFORMAÇÃO DO ARQUIVO**

### 📁 Scripts em Python para Facilitar
Conjunto de scripts auxiliares desenvolvidos para:
- Corrigir as inscrições imobiliárias enviadas pelo TCE;
- Comparar o arquivo gerado pelo script com o arquivo que foi corrigido;

## Requisitos
- Python 3.13 (Baixe na Microsoft Store do seu Notebook)
- Biblioteca Necessária: `pandas`

### Instalando a biblioteca pandas
Para instalar a biblioteca pandas no Visual Studio Code, abre o terminal no arquivo do código `python` e utilize o comando `pip install pandas`.

### Vídeo de exemplo
https://www.youtube.com/watch?v=7u_3MYoB3T8

## Como usar
1. Clone este repositório ou baixe o conteúdo da pasta.
2. Acesse a pasta desejada.
3. Execute os scripts conforme instruções incluídas em cada subdiretório.

## Contribuições
Sugestões de melhoria, novas ideias de automações ou correções são bem-vindas. Sinta-se à vontade para contribuir.
---