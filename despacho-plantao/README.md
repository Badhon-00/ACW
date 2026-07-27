# despacho-plantao

> Emite o rascunho do despacho decisório do Delegado de Polícia de plantão a partir de um fato narrado, no padrão real da Delegacia de Alta Floresta/MT.

## O que faz

A skill simula a atuação do Delegado de Polícia de plantão: recebe um fato (ocorrência, abordagem, prisão, flagrante) e devolve um **despacho decisório** completo, na fraseologia real da unidade. O usuário é o Delegado Titular; a skill produz o rascunho que ele revisaria e assinaria.

O fluxo de trabalho cobre toda a decisão de plantão:

- Extração dos elementos do fato (conduzidos, vítima, objetos apreendidos, vida pregressa);
- Avaliação da situação flagrancial nas modalidades do art. 302 do CPP, inclusive hipóteses de afastamento (apresentação espontânea, decurso de tempo, dúvida sobre autoria);
- Tipificação em tese, com verificação de condição de procedibilidade, incidência da Lei 11.340/2006 e concurso de crimes;
- Escolha entre seis desfechos típicos da unidade: APF, APF com representação pela preventiva, TCO, BOC (ato infracional), instauração de IP ou não instauração — tratando cada envolvido separadamente quando o caso comporta desfechos distintos;
- Providências de Polícia Judiciária numeradas (perícias, FONAR, oitivas, apreensões, checagem de mandados etc.).

Aplica regras críticas de plantão, como a vedação de fiança em violência doméstica (Enunciado 06 da COPEVID) e a exigência de violência baseada no gênero para incidência da Maria da Penha. Ao final, entrega "Notas ao Delegado" com premissas assumidas, pontos de atenção jurídica e diligências pendentes.

## Quando usar

- "Despacha esse flagrante" / "monta o despacho de plantão";
- "Qual o encaminhamento?" / "Ratifico a voz de prisão?";
- "Cabe representação pela preventiva?";
- "Esse caso é Maria da Penha?" / "Deixo de instaurar?";
- Qualquer ocorrência, prisão ou abordagem em que se precise decidir entre APF, TCO, BOC, instauração de IP ou liberação.

Cobre violência doméstica, medidas protetivas, lesão, ameaça, estupro de vulnerável, drogas, arma, roubo, furto, extorsão e crimes em geral. Não use para relatório final de inquérito (skill `relatorio-final-ip`) nem para representações cautelares completas (skill `representacao-cautelar`).

## Como usar

> "Despacha esse flagrante: PM conduziu Fulano por tráfico, apreendidos 50g de cocaína e balança de precisão, BO nº 2026.12345."

> "GUPM apresentou conduzido por descumprimento de medida protetiva; a vítima quer representar. Qual o encaminhamento?"

> "Adolescente de 16 anos apreendido com moto furtada e um maior na garupa. Monta o despacho de plantão para os dois."

> "Vítima mulher agrediu e foi agredida pelo companheiro, versões conflitantes. Esse caso é Maria da Penha? Cabe APF?"

> "Suspeito de furto se apresentou espontaneamente no quartel dois dias depois do fato. Ratifico a voz de prisão?"

## O que a skill entrega

- **Padrão: texto formatado direto no chat**, pronto para revisar e colar, com a estrutura real da unidade (abertura, síntese do fato, tipificação, situação flagrancial, decisão de mérito, providências numeradas e fecho);
- Seção separada de **Notas ao Delegado** (premissas, pontos de atenção, diligências dependentes de dado faltante);
- Arquivo **.docx** apenas se o usuário pedir expressamente (aciona a skill `docx`).

## Estrutura da pasta

| Item | Papel |
|---|---|
| `SKILL.md` | Instruções completas: fluxo em 7 passos, tabela de desfechos, regras críticas e estilo da casa |
| `references/modelos.md` | Tabelas de tipos penais, fundamentos recorrentes e fraseologia real dos despachos da unidade |

## Requisitos

Nenhum além do Claude Code. Não há scripts nem dependências de Python. Entrada esperada: relato do fato em texto livre; opcionalmente BO, termos ou transcrições anexados, que a skill lê antes de despachar.

## Avisos

- **A minuta exige revisão da Autoridade Policial**: a skill produz rascunho fundamentado; a decisão e a assinatura são sempre do Delegado.
- **Dados sigilosos** de ocorrências, vítimas e investigados não devem ser colados em ambientes não autorizados pela instituição.
- Tratamento de dados pessoais sujeito à **LGPD** (Lei 13.709/2018) e ao sigilo funcional: compile apenas o que o fato exige.
- A skill segue as convenções, a fraseologia e os desfechos típicos da **Delegacia de Alta Floresta/MT**; o uso em outras unidades exige adaptação de modelos e rotinas.
- Jurisprudência e súmulas citadas devem ser conferidas; na dúvida, a própria skill sinaliza a incerteza em vez de afirmar com falsa confiança.
