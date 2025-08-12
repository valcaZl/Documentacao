# 📚 Documentação de Scripts, Tutoriais e Recursos

Este repositório reúne uma coleção organizada de **scripts**, **casos de uso**, **tutoriais** e **funções utilitárias** para facilitar o desenvolvimento, integração e automação de rotinas em diferentes áreas (Arrecadação, Contratos, Pessoal, JasperSoft etc.).

O objetivo é servir como um guia prático e centralizado para desenvolvedores, analistas e demais usuários que precisem criar, adaptar ou entender soluções já implementadas.

## 📂 Estrutura de Pastas

### **1. Arrecadação**

Esta pasta é dedicada à publicação de conteúdos técnicos voltados ao uso de funções nas ferramentas de extensões, com foco em automações e integrações relacionadas à arrecadação tributária. Aqui você encontrará exemplos e explicações de scripts desenvolvidos em **BFC** e **Groovy**, com o objetivo de facilitar a implementação e a resolução de diferentes casos de uso.

Os conteúdos estão organizados em subpastas temáticas, cada uma abordando um conjunto específico de funcionalidades:

*   **Casos de Uso** — Contém scripts com estrutura consolidada, pensados para serem reutilizados ou adaptados conforme a necessidade. Serve como referência prática no desenvolvimento de extensões. Inclui:
    *   [`Extração de dados em CSV.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/Extra%C3%A7%C3%A3o%20de%20dados%20em%20CSV.md): Script para exportar dados de pessoas (ID, nome, CPF/CNPJ) para um arquivo CSV, com opções de configuração de delimitador e encoding. Útil para relatórios e análises externas.
    *   [`Horário de funcionamento.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/Hor%C3%A1rio%20de%20funcionamento.md): Script detalhado para coletar, formatar e exibir horários de funcionamento de estabelecimentos econômicos, tratando horários de segunda a domingo, intrajornada e variações de horário. Essencial para emissão de alvarás com informações precisas de expediente.
    *   [`Leitura de arquivos TXT e preenchimento de tabela auxiliar.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/Leitura%20de%20arquivos%20TXT%20e%20preenchimento%20de%20tabela%20auxiliar.md): Script para ler dados de arquivos TXT (com delimitador personalizável) e preencher tabelas auxiliares no sistema. Ideal para importação de dados externos de forma automatizada.
    *   [`Script Concede Desconto Débito.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/Script%20Concede%20Desconto%20D%C3%A9bito.md): Script para aplicar descontos em débitos específicos, utilizando a API REST para atualização de informações financeiras.
    *   [`Script Patch utilizando API REST.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/Script%20Patch%20utilizando%20API%20REST.md): Exemplo de script para realizar operações de atualização parcial (PATCH) em recursos via API REST, demonstrando a interação com serviços externos.
    *   [`Script Post utilizando API REST.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/Script%20Post%20utilizando%20API%20REST.md): Exemplo de script para realizar operações de criação (POST) de novos recursos via API REST, fundamental para integração e envio de dados.
    *   [`Script alteração Data de Lançamento Débito.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/Script%20altera%C3%A7%C3%A3o%20Data%20de%20Lan%C3%A7amento%20D%C3%A9bito.md): Script para alterar a data de lançamento de débitos, útil para ajustes e correções de registros financeiros.
    *   [`Script para preenchimento de Campos Adicionais.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/Script%20para%20preenchimento%20de%20Campos%20Adicionais.md): Script para preencher campos adicionais no sistema sem a necessidade de API REST, utilizando funções internas para automação de cadastros.
    *   [`Script transfere divida entre contribuintes.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/Script%20transfere%20divida%20entre%20contribuintes.md): Script complexo para transferir dívidas entre contribuintes, incluindo tratamento de lotes e consulta de status de processamento, garantindo a integridade dos dados.
    *   [`certidãoNegativa.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/certid%C3%A3oNegativa.md): Script para geração de certidões negativas de débitos (CND), avaliando a situação fiscal do contribuinte (dívidas, débitos, parcelamentos) e classificando a certidão (positiva, positiva com efeito negativo, negativa).
    *   [`habiteseEmitidos.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/habiteseEmitidos.md): Script para relacionar documentos, habite-se e obras, gerando uma fonte dinâmica consolidada com informações de obras que possuem Habite-se emitido, incluindo nome do contribuinte e código da obra.
    *   [`preenchimentoDeCamposAdicionais.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/preenchimentoDeCamposAdicionais.md): Script para leitura de arquivos CSV e preenchimento automático de campos adicionais (ex: Valor Venal do Terreno), com validação de encoding e tratamento de dados.
    *   [`switchCase.md`](https://github.com/valcaZl/Documentacao/blob/main/Arrecada%C3%A7%C3%A3o/Casos%20de%20Uso/switchCase.md): Exemplo de implementação de lógica condicional tipo 'switch case' em BFC-Script, útil para diversas situações de ramificação de fluxo.

*   **Script TCE** — Pacote específico para integrações com o Tribunal de Contas do Estado (TCE). Documenta o processo e os scripts utilizados para gerar planilhas com informações detalhadas sobre inscrições imobiliárias, conforme exigências do TCE. Inclui:
    *   **configuração do arquivo csv** — Contém exemplos e instruções sobre como configurar corretamente o arquivo CSV enviado pelo TCE para uso nos scripts.
    *   **Scripts em Python para Facilitar** — Conjunto de scripts auxiliares desenvolvidos em Python para manipulação de dados:
        *   `comparar.py` — Script para comparar o arquivo gerado pelo sistema com o arquivo corrigido, auxiliando na validação de dados.
        *   `corrigir.py` — Script para realizar correções automatizadas nas inscrições imobiliárias fornecidas pelo TCE.
    *   **script** — Contém a documentação principal do `script TCE.md`, que detalha o script para gerar a tabela com as informações solicitadas pelo TCE, com atenção à necessidade de alterar nomes de campos adicionais e entidades.

### **2. Contratos**

Esta pasta contém scripts e documentações relacionadas à automação, exportação e manipulação de dados de contratos e compras. Ela é dividida em duas subpastas principais:

*   **Compras** — Focada em operações relacionadas a materiais e compras:
    *   [`Exclusão de Materiais.md`](https://github.com/valcaZl/Documentacao/blob/main/Contratos/Compras/Exclus%C3%A3o%20de%20Materiais.md): Documenta um script Groovy para exclusão em massa de materiais via API REST, lendo IDs de um arquivo CSV e realizando requisições DELETE.
    *   [`Exportação de Materiais.md`](https://github.com/valcaZl/Documentacao/blob/main/Contratos/Compras/Exporta%C3%A7%C3%A3o%20de%20Materiais.md): Descreve um script Groovy que extrai, limpa e formata dados de materiais (ID, descrição, código) de uma fonte e os exporta para um arquivo CSV, com tratamento de caracteres especiais.
    *   [`Verificar Históricos de Alterações.md`](https://github.com/valcaZl/Documentacao/blob/main/Contratos/Compras/Verificar%20Hist%C3%B3ricos%20de%20Altera%C3%A7%C3%B5es.md): Detalha um script Groovy que busca informações de materiais por código e gera um log (`.txt`) com dados de criação e última alteração, útil para auditoria.
*   **Contratos** — Contém scripts e documentações específicas para a gestão de contratos:
    *   [`Consulta com Maps - Fontes Diferentes CSV.md`](https://github.com/valcaZl/Documentacao/blob/main/Contratos/Contratos/Consulta%20com%20Maps%20-%20Fontes%20Diferentes%20CSV.md): Documenta um script Groovy que coleta informações de materiais e suas especificações de diferentes fontes, estrutura-as em um objeto e as exporta para um arquivo CSV, incluindo IDs de especificações.
    *   [`Encerrar Contratos.md`](https://github.com/valcaZl/Documentacao/blob/main/Contratos/Contratos/Encerrar%20Contratos.md): Documenta um script para encerrar contratos, incluindo detalhes sobre o processo e os parâmetros necessários.    *   [`Script conversão de contratos.md`](https://github.com/valcaZl/Documentacao/blob/main/Contratos/Contratos/Script%20convers%C3%A3o%20de%20contratos.md): Documenta um script para converter contratos, detalhando o processo de transformação de dados e formatos.
### **3. Contábil**

*(Pasta criada, porém atualmente sem arquivos visíveis)*

### **4. Funções**

Esta pasta contém um conjunto de **funções utilitárias em Groovy** projetadas para serem reutilizadas em diversos projetos e scripts. Elas oferecem soluções padronizadas para formatação e manipulação de dados comuns no contexto brasileiro, como documentos, valores monetários e números por extenso. O objetivo é centralizar e facilitar o uso dessas funcionalidades, promovendo a consistência e a eficiência no desenvolvimento.

Os arquivos nesta pasta incluem:

*   [`formatarCEP.md`](https://github.com/valcaZl/Documentacao/blob/main/Fun%C3%A7%C3%B5es/formatarCEP.md): Função que formata um CEP (Código de Endereçamento Postal) brasileiro, adicionando o hífen no formato `XXXXX-XXX`.
*   [`formatarCpfCnpj.md`](https://github.com/valcaZl/Documentacao/blob/main/Fun%C3%A7%C3%B5es/formatarCpfCnpj.md): Contém três funções (`formatCNPJ`, `formatCPF` e `formatCpfCnpj`) para formatar CPFs e CNPJs brasileiros, aplicando os padrões oficiais (ex: `XXX.XXX.XXX-XX` para CPF e `XX.XXX.XXX/XXXX-XX` para CNPJ). A função `formatCpfCnpj` é inteligente e detecta automaticamente o tipo de documento.
*   [`formatarTelefone.md`](https://github.com/valcaZl/Documentacao/blob/main/Fun%C3%A7%C3%B5es/formatarTelefone.md): Função para formatar números de telefone brasileiros (com DDD), adaptando-se a números de 10 ou 11 dígitos e aplicando parênteses e hífen (ex: `(XX) XXXXX-XXXX`).
*   [`formatarUtil.md`](https://github.com/valcaZl/Documentacao/blob/main/Fun%C3%A7%C3%B5es/formatarUtil.md): Uma função utilitária genérica que atua como um "hub" de formatação. Ela direciona a chamada para outras funções de formatação específicas (como CPF, CNPJ, CEP, TELEFONE, VALOR, EXTENSO) com base no tipo de formatação desejado, tornando o código mais limpo e fácil de manter.
*   [`formatarValor.md`](https://github.com/valcaZl/Documentacao/blob/main/Fun%C3%A7%C3%B5es/formatarValor.md): Função que formata um valor numérico para o padrão monetário brasileiro, utilizando vírgula como separador decimal e ponto como separador de milhares (ex: `1.234,56`).
*   [`numeroPorExtenso.md`](https://github.com/valcaZl/Documentacao/blob/main/Fun%C3%A7%C3%B5es/numeroPorExtenso.md): Função que converte valores numéricos (com ou sem centavos) para sua representação por extenso em português, útil para documentos como certidões e guias de pagamento.

### **5. Pessoal**

Esta pasta é destinada à publicação de todo o conteúdo técnico gerado pela vertical Pessoal. Seu objetivo é documentar materiais considerados facilitadores no processo de aprendizado e na melhoria da produtividade.

### **6. Tutorias Básicos**

Esta pasta é destinada à publicação de conteúdos técnicos introdutórios voltados ao uso de Fontes Dinâmicas, Scripts, Fórmulas e outros recursos relacionados às extensões. É ideal para quem está começando a explorar a criação de extensões e precisa de uma base prática e acessível para seus primeiros passos.

Os conteúdos estão organizados em subpastas temáticas. Para consultar os detalhes completos de cada item, é essencial acessar diretamente a respectiva pasta.

*   **Extensões** — Contém tutoriais básicos sobre o desenvolvimento de scripts, fontes dinâmicas e fórmulas. Inclui:
    *   [`Criar Fonte Dinâmica.md`](https://github.com/valcaZl/Documentacao/blob/main/Tutorias%20B%C3%A1sicos/Extens%C3%B5es/Criar%20Fonte%20Din%C3%A2mica.md): Tutorial sobre como criar uma fonte dinâmica.
    *   [`csv.md`](https://github.com/valcaZl/Documentacao/blob/main/Tutorias%20B%C3%A1sicos/Extens%C3%B5es/csv.md): Tutorial sobre manipulação de arquivos CSV.
    *   [`estruturasCondicionais.md`](https://github.com/valcaZl/Documentacao/blob/main/Tutorias%20B%C3%A1sicos/Extens%C3%B5es/estruturasCondicionais.md): Tutorial sobre estruturas condicionais.
    *   [`MultiplasFontes.md`](https://github.com/valcaZl/Documentacao/blob/main/Tutorias%20B%C3%A1sicos/Extens%C3%B5es/MultiplasFontes.md): Tutorial sobre como usar múltiplas fontes.
    *   [`encontrarDuplicatas.md`](https://github.com/valcaZl/Documentacao/blob/main/Tutorias%20B%C3%A1sicos/Extens%C3%B5es/encontrarDuplicatas.md): Tutorial sobre como encontrar duplicatas.
    *   [`gerarTxt.md`](https://github.com/valcaZl/Documentacao/blob/main/Tutorias%20B%C3%A1sicos/Extens%C3%B5es/gerarTxt.md): Tutorial sobre como gerar arquivos TXT.

### **7. Utilidades JasperSoft**

Esta pasta está destinada a conteúdos relacionados com funções e outras ferramentas destinadas para utilidades dentro do **TIBCO JASPERSOFT STUDIO**. Ela serve como um repositório de recursos e instruções para otimizar o uso do JasperSoft, incluindo configurações, dicas e boas práticas para a criação e manutenção de relatórios.

## 🚀 Como Navegar e Utilizar

1.  **Identifique a área** do seu interesse (ex.: arrecadação, contratos, funções utilitárias).
2.  **Abra o README.md interno** da pasta (quando disponível) para orientações detalhadas.
3.  **Siga os tutoriais passo a passo** quando aplicável.
4.  Utilize as **Funções** como biblioteca de apoio para outros scripts.
5.  Para integrações com JasperSoft, consulte a pasta **Utilidades JasperSoft**.

## 📌 Boas Práticas

*   **Leia sempre a documentação** antes de executar um script.
*   Ao criar novos conteúdos, siga a estrutura existente.
*   Mantenha nomes claros e descritivos para arquivos.
*   Inclua comentários e instruções de uso nos scripts.

## 🤝 Contribuição

Sinta-se à vontade para contribuir com melhorias, novos scripts e tutoriais. Me chame no chat para podermos alinhar os conteudos a serem publicados.

_Vitor V R Martins_

