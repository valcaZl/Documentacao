## 📄 Script para Conceder um Desconto para Débito


---

## 🧠 Código Completo

```groovy
//-------------------------------------------Fontes-------------------------------------------//
valorDesconto = parametros.desconto?.valor
CodLancamento = parametros.CodLancamento?.valor
filtroDebitos = "debito.idLancamento = ${CodLancamento} and debito.situacao = 'ABERTO'";
dadosDebitos = Dados.tributos.v2.debitos.receitas.busca(criterio: filtroDebitos,primeiro: true);
chaveIntegracao = Variavel.CHAVE_INTEGRACAO

//-------------------------------------------Layout-------------------------------------------//
Deb = [];
Deb << [
  idIntegracao: 'PATCH ' + dadosDebitos.id,
  guiasReceitas: [
    idGerado: [
      id: dadosDebitos.id
    ],
    valorDesconto: valorDesconto
  ]
] 
imprimir Deb

//-------------------------------------------Parametros-------------------------------------------//
json = Http.servico("URL_API")
      .chaveIntegracao(chaveIntegracao)
      .PATCH(Deb,Http.JSON);


//-------------------------------------------Retorno-------------------------------------------//
imprimir json.codigo() + ' - ' + json.conteudo()

se (json.codigo() == 200){
  Notificacao.nova('Desconto Enviado para Processamento !')
  .para(usuario.id)
  .enviar()
}senao{
  Notificacao.nova('Erro ao enviar o Desconto Enviado para Processamento !')
  .para(usuario.id)
  .enviar()
}
---

```
## 🔍 Explicações das Funções

### 🔄 `URL_API`

        ➡️ Criar os parametros CodLancamento(Numero) e valorDesconto(Numero)
        ⚠️ utilizar /guiasReceitas com o URL disponibilizado em documentação


### 🔄 `chaveIntegracao`

        ➡️ Criar variavel de ambiente com o nome chaveIntegracao, contendo o token da entidade.
