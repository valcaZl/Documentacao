# 🕒 Emissão de Alvará com Horário de Funcionamento

Este documento descreve o funcionamento detalhado do script responsável pela coleta, formatação e exibição dos **horários de funcionamento** de estabelecimentos econômicos. O foco principal é garantir que os horários de segunda a domingo sejam tratados adequadamente, com formatação humana e consideração de intrajornada.

---

## ✨ Fontes Utilizadas

| Fonte                                          | Finalidade                       |
| ---------------------------------------------- | -------------------------------- |
| `Dados.tributos.v2.horariosFuncionamento.dias` | Horários por dia da semana       |
| `Dados.tributos.v2.economicos`                 | Dados do econômico               |
| `Dados.tributos.v2.alvara`                     | Dados do alvará                  |
| `Dados.tributos.v2.economico.atividades`       | Lista de atividades do econômico |

---

## 📋 Esquema da Fonte

```groovy
esquema = [
  hrFuncionamento: Esquema.caracter,
  hrFuncionamentoSabado: Esquema.caracter,
  hrFuncionamentoDomingo: Esquema.caracter,
  horaEntrada: Esquema.caracter,
  horaSaida: Esquema.caracter,
  horaIntrajornadaEntrada: Esquema.caracter,
  horaIntrajornadaSaida: Esquema.caracter,
  atividades: Esquema.lista(Esquema.objeto([
    cnae: Esquema.caracter,
    descricaoCnae: Esquema.caracter
  ]))
  // ... outros campos omitidos
]
```

---

## 🌐 Função de Formatação de Horários

Função que trata a remoção de segundos desnecessários e monta os horários com ou sem intervalo intrajornada:

```groovy
def formatarHorasComIntervalo = { entrada, saida, intrajornadaEntrada, intrajornadaSaida ->
  def formatarHora = { hora ->
    if (hora == null) return null;
    def partes = hora.split(":");
    return (partes.size() > 2 && partes[2] == "00") ? "${partes[0]}:${partes[1]}" : hora;
  };

  def ent = formatarHora(entrada);
  def sai = formatarHora(saida);
  def intraEnt = formatarHora(intrajornadaEntrada);
  def intraSai = formatarHora(intrajornadaSaida);

  if (!ent || !sai || !intraEnt || !intraSai) return null;

  return (intraEnt == intraSai) ?
    "${ent} às ${sai}" :
    "${ent} às ${intraSai} - ${intraEnt} às ${sai}";
}
```

---

## 🎓 Agrupamento por Dia da Semana

O script agrupa os registros em um mapa para facilitar o acesso por dia:

```groovy
def horariosPorDia = [:]
todosHorariosDoComercio.each { item ->
  horariosPorDia[item.dia?.valor] = item
}
```

---

## 📅 Segunda a Sexta-feira

Verifica se os horários dos dias úteis são iguais e define o comportamento:

```groovy
def dias = ["SEGUNDA", "TERCA", "QUARTA", "QUINTA", "SEXTA"]
def comum = null

dias.each { dia ->
  def h = horariosPorDia[dia]
  if (h) {
    def f = formatarHorasComIntervalo(h.horaEntrada, h.horaSaida, h.horaIntrajornadaEntrada, h.horaIntrajornadaSaida)
    comum = (comum == null) ? f : (comum == f ? comum : "Variado")
  }
}
```

### Resultado final

* Se comuns: `Segunda à Sexta-feira: 08:00 às 12:00 - 13:30 às 18:00`
* Se variados: `Segunda à Sexta-feira: Horário Variado (verificar)`

---

## 🔻 Sábado e Domingo

```groovy
def sabado = horariosPorDia["SABADO"]
def domingo = horariosPorDia["DOMINGO"]

def hrFuncionamentoSabado = sabado ? "Sábado: ${formatarHorasComIntervalo(...)}" : "Fechado"
def hrFuncionamentoDomingo = domingo ? "Domingo: ${formatarHorasComIntervalo(...)}" : "Fechado"
```

---

## 🔄 Linha final do alvará

```groovy
linha = [
  hrFuncionamento: dadosEconomicos.horarioFuncionamento?.descricao ?: "Horário não Cadastrado!",
  hrFuncionamentoSabado: hrFuncionamentoSabado,
  hrFuncionamentoDomingo: hrFuncionamentoDomingo,
  horaEntrada: horaEntradaPrincipal,
  horaSaida: horaSaidaPrincipal,
  horaIntrajornadaEntrada: horaIntrajornadaEntradaPrincipal,
  horaIntrajornadaSaida: horaIntrajornadaSaidaPrincipal,
  // demais campos...
]
```

---

## ✅ Vantagens

* ✅ Formatação clara e flexível dos horários
* ✅ Considera intrajornada
* ✅ Detecta variações por dia
* ✅ Adapta-se à ausência de dias cadastrados

---

## 🚀 Sugestões Futuras

* Incluir feriados ou exceções pontuais
* Exportação dos horários em tabela por dia
* Permitir múltiplos turnos no mesmo dia

---

> ✊ Documentação inspirada no estilo `valcaZl/Documentacao` ✔️
