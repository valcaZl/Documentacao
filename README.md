# 📚 Documentação de Scripts, Tutoriais e Recursos

Este repositório reúne uma coleção organizada de **scripts**, **casos de uso**, **tutoriais** e **funções utilitárias** para facilitar o desenvolvimento, integração e automação de rotinas em diferentes áreas (Arrecadação, Contratos, Pessoal, JasperSoft etc.).

O objetivo é servir como um guia prático e centralizado para desenvolvedores, analistas e demais usuários que precisem criar, adaptar ou entender soluções já implementadas.

## 📂 Estrutura de Pastas

### **1. Arrecadação**

Esta pasta é dedicada à publicação de conteúdos técnicos voltados ao uso de funções nas ferramentas de extensões, com foco em automações e integrações relacionadas à arrecadação tributária. Aqui você encontrará exemplos e explicações de scripts desenvolvidos em **BFC** e **Groovy**, com o objetivo de facilitar a implementação e a resolução de diferentes casos de uso.

Os conteúdos estão organizados em subpastas temáticas, cada uma abordando um conjunto específico de funcionalidades:

*   **Casos de Uso** — Contém scripts com estrutura consolidada, pensados para serem reutilizados ou adaptados conforme a necessidade. Serve como referência prática no desenvolvimento de extensões. Inclui:
    *   `Extração de dados em CSV.md`: Script para exportar dados de pessoas (ID, nome, CPF/CNPJ) para um arquivo CSV, com opções de configuração de delimitador e encoding. Útil para relatórios e análises externas.
    *   `Horário de funcionamento.md`: Script detalhado para coletar, formatar e exibir horários de funcionamento de estabelecimentos econômicos, tratando horários de segunda a domingo, intrajornada e variações de horário. Essencial para emissão de alvarás com informações precisas de expediente.
    *   `Leitura de arquivos TXT e preenchimento de tabela auxiliar.md`: Script para ler dados de arquivos TXT (com delimitador personalizável) e preencher tabelas auxiliares no sistema. Ideal para importação de dados externos de forma automatizada.
    *   `Script Concede Desconto Débito.md`: Script para aplicar descontos em débitos específicos, utilizando a API REST para atualização de informações financeiras.
    *   `Script Patch utilizando API REST.md`: Exemplo de script para realizar operações de atualização parcial (PATCH) em recursos via API REST, demonstrando a interação com serviços externos.
    *   `Script Post utilizando API REST.md`: Exemplo de script para realizar operações de criação (POST) de novos recursos via API REST, fundamental para integração e envio de dados.
    *   `Script alteração Data de Lançamento Débito.md`: Script para alterar a data de lançamento de débitos, útil para ajustes e correções de registros financeiros.
    *   `Script para preenchimento de Campos Adicionais.md`: Script para preencher campos adicionais no sistema sem a necessidade de API REST, utilizando funções internas para automação de cadastros.
    *   `Script transfere divida entre contribuintes.md`: Script complexo para transferir dívidas entre contribuintes, incluindo tratamento de lotes e consulta de status de processamento, garantindo a integridade dos dados.
    *   `certidãoNegativa.md`: Script para geração de certidões negativas de débitos (CND), avaliando a situação fiscal do contribuinte (dívidas, débitos, parcelamentos) e classificando a certidão (positiva, positiva com efeito negativo, negativa).
    *   `habiteseEmitidos.md`: Script para relacionar documentos, habite-se e obras, gerando uma fonte dinâmica consolidada com informações de obras que possuem Habite-se emitido, incluindo nome do contribuinte e código da obra.
    *   `preenchimentoDeCamposAdicionais.md`: Script para leitura de arquivos CSV e preenchimento automático de campos adicionais (ex: Valor Venal do Terreno), com validação de encoding e tratamento de dados.
    *   `switchCase.md`: Exemplo de implementação de lógica condicional tipo 'switch case' em BFC-Script, útil para diversas situações de ramificação de fluxo.

*   **Script TCE** — Pacote específico para integrações com o Tribunal de Contas do Estado (TCE). Documenta o processo e os scripts utilizados para gerar planilhas com informações detalhadas sobre inscrições imobiliárias, conforme exigências do TCE. Inclui:
    *   **configuração do arquivo csv** — Contém exemplos e instruções sobre como configurar corretamente o arquivo CSV enviado pelo TCE para uso nos scripts.
    *   **Scripts em Python para Facilitar** — Conjunto de scripts auxiliares desenvolvidos em Python para manipulação de dados:
        *   `comparar.py` — Script para comparar o arquivo gerado pelo sistema com o arquivo corrigido, auxiliando na validação de dados.
        *   `corrigir.py` — Script para realizar correções automatizadas nas inscrições imobiliárias fornecidas pelo TCE.
    *   **script** — Contém a documentação principal do `script TCE.md`, que detalha o script para gerar a tabela com as informações solicitadas pelo TCE, com atenção à necessidade de alterar nomes de campos adicionais e entidades.

### **2. Contratos**

Automação, exportação e manipulação de contratos e compras.

*   **Compras**:
    *   `Exclusão de Materiais.md`
    *   `Exportação de Materiais.md`
    *   `Verificar Históricos de Alterações.md`
*   **Contratos**:
    *   `Consulta com Maps - Fontes Diferentes CSV.md`
    *   `Encerrar Contratos.md`
    *   `Script conversão de contratos.md`

### **3. Contábil**

*(Pasta criada, porém atualmente sem arquivos visíveis)*

### **4. Funções**

Funções utilitárias reaproveitáveis em múltiplos projetos:

*   `formatarCpfCnpj.md`
*   `formatarCEP.md`
*   `formatarTelefone.md`
*   `formatarValor.md`
*   `numeroPorExtenso.md`
*   `formatarUtil.md` — Funções de formatação genéricas.

### **5. Pessoal**

Rotinas e instruções ligadas à gestão de pessoal.

*   Contém um `README.md` específico com orientações.

### **6. Tutorias Básicos**

Material educativo com passo a passo para iniciantes.

*   **Extensões**:
    *   `Criar Fonte Dinâmica.md`
    *   `csv.md` — Manipulação de arquivos CSV.
    *   `estruturasCondicionais.md`
    *   `MultiplasFontes.md`
    *   `encontrarDuplicatas.md`
    *   `gerarTxt.md`

### **7. Utilidades JasperSoft**

Recursos e instruções para uso com **JasperSoft**:

*   Configurações, dicas e boas práticas para criação e manutenção de relatórios.

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

