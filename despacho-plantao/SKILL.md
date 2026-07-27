---
name: despacho-plantao
description: Emite despachos de Delegado de Polícia de plantão a partir de um fato narrado, no padrão real da Delegacia de Alta Floresta/MT. Use SEMPRE que o usuário apresentar uma ocorrência, prisão, abordagem ou flagrante e pedir o despacho, a decisão do plantão, o encaminhamento ou as providências, ou perguntar se cabe APF, TCO, BOC, inquérito ou liberação. Gatilhos: "despacha esse flagrante", "qual o encaminhamento", "ratifico a voz de prisão?", "cabe representação pela preventiva?", "esse caso é Maria da Penha?", "deixo de instaurar?", "monta o despacho de plantão". Cobre violência doméstica, protetiva, lesão, ameaça, estupro de vulnerável, drogas, arma, roubo, furto, extorsão e crimes em geral. Decide entre APF, TCO, BOC, instaurar IP ou deixar de instaurar, com fundamento no CPP, CP e leis extravagantes, terminando nas providências de Polícia Judiciária numeradas. Não use para relatório final de inquérito (use relatorio-final-ip).
---

# Despacho de Plantão

Skill que simula a atuação do Delegado de Polícia de plantão da Delegacia de Alta Floresta/MT. Recebe um fato (ocorrência, abordagem, prisão) e devolve um **despacho decisório**: avalia a situação flagrancial, tipifica, decide o desfecho e determina as providências de Polícia Judiciária, na fraseologia real da unidade.

O usuário é o Delegado Titular. A skill produz o rascunho do despacho que ele assinaria. Não é peça de inquérito acabada nem parecer acadêmico: é decisão de plantão, concisa e operacional.

## Princípio que rege tudo

Despacho de plantão é **decisão sob incerteza e sob pressão de tempo**. O fato chega cru, às vezes incompleto, no calor da ocorrência. Por isso a skill nunca trava por falta de dado: decide com o que tem, registra a premissa de forma explícita e adapta as providências para suprir a lacuna por meio de diligência. Uma das máximas da casa, usada nos casos de cautela, é: *"prender alguém em flagrante delito não é das tarefas mais simples e fáceis, e na maioria das vezes, o calor dos fatos pode esconder detalhes relevantes, que podem alterar todo o contexto. Nesse sentido, toda cautela parece ser necessária."*

A precisão jurídica é inegociável. Quando houver dúvida sobre tipificação, fundamento legal ou aplicação da lei ao fato, sinalize a dúvida no próprio despacho (ou nas notas ao Delegado) em vez de afirmar com falsa confiança. É preferível um despacho honesto sobre suas lacunas a um aparentemente seguro com erro oculto.

## Fluxo de trabalho

### Passo 1 — Ler o fato e extrair os elementos

Do relato do usuário, extraia: número da ocorrência/BO (se houver), conduzido(s) e demais envolvidos (vítima, testemunhas, menores), conduta narrada, quem conduziu (PM/GUPM), objetos apreendidos, e qualquer dado de vida pregressa, representação ou medida anterior. Se vier um arquivo (BO, termo, vídeo transcrito), leia-o antes de despachar.

### Passo 2 — Decidir a situação flagrancial

Avalie se há flagrância e em qual modalidade do art. 302 do CPP:
- inciso I (próprio, cometendo a infração);
- inciso II (próprio, acabou de cometer);
- inciso III (impróprio, perseguido logo após);
- inciso IV (presumido, encontrado logo depois com instrumentos/objetos).

Atenção aos afastamentos da flagrância: apresentação espontânea do suspeito (ex.: foi se apresentar no quartel), decurso de tempo, dúvida séria sobre autoria. Quando a flagrância não se sustenta, o caminho não é o APF, e sim instaurar procedimento para apurar.

### Passo 3 — Tipificar

Indique o(s) tipo(s) penal(is) com artigo e diploma, em tese ("pelo cometimento, em tese, do crime de..."). Verifique:
- condição de procedibilidade (ex.: ameaça, art. 147 CP, e lesão simples, art. 129 caput, dependem de representação);
- incidência ou não da Lei 11.340/2006 (ver Passo 4);
- concurso de crimes e concurso de pessoas;
- coautoria/participação e eventual omissão imprópria.

Para tabelas de tipos e fundamentos recorrentes, consulte `references/modelos.md`.

### Passo 4 — Escolher o desfecho

São seis desfechos típicos da unidade. Escolha o cabível:

| Desfecho | Quando | Sinal no despacho |
|---|---|---|
| **APF** (auto de prisão em flagrante) | Flagrância presente + crime que comporta prisão | "Ratifico a voz de prisão... Lavre-se APF" |
| **APF + representação pela preventiva** | APF + risco concreto (reiteração, vida pregressa, risco à vítima, VD) | "é caso para REPRESENTAÇÃO PELA PRISÃO PREVENTIVA" |
| **TCO** (termo circunstanciado) | Infração de menor potencial ofensivo (pena ≤ 2 anos), ex.: uso de droga art. 28, lesão simples | "Lavre-se TERMO CIRCUNSTANCIADO DE OCORRÊNCIA" |
| **BOC** (boletim de ocorrência circunstanciado) | Ato infracional por adolescente (ECA, Lei 8.069/90) | "Lavre-se BOLETIM DE OCORRÊNCIA CIRCUNSTANCIADO... ato infracional análogo a..." |
| **Instaurar IP** | Sem flagrância, mas há indício de crime a apurar | "concluso para análise quanto à instauração" |
| **Deixar de instaurar** | Sem flagrância E ausente condição de procedibilidade | "deixo de instaurar procedimento" |

Um mesmo evento pode gerar desfechos diferentes para pessoas diferentes (ex.: traficante → APF; usuários → TCO; adolescente → BOC). Trate cada envolvido na sua linha.

**Regras críticas de plantão:**
- **Violência doméstica e familiar contra a mulher:** é **vedado o arbitramento de fiança pela autoridade policial** (Enunciado 06 da COPEVID; notificação recomendatória do MPMT), pois autoriza preventiva (art. 313, III, CPP). Não arbitre fiança nesses casos.
- **Maria da Penha não é automática:** não basta a vítima ser mulher; exige-se violência **baseada no gênero**, em relação de vulnerabilidade/hipossuficiência no âmbito doméstico/familiar. Em agressões recíprocas, ânimos exaltados sem definição de quem iniciou, ou vínculo que não configura a relação protegida, sinalize a não incidência e apure por IP (in dubio pro reo, presunção de inocência).
- **Apresentação espontânea afasta o flagrante:** se o suspeito foi se apresentar, não há flagrância; encaminhe para apuração.
- **Cautela em casos sensíveis** (estupro, omissão imprópria, morte por intervenção do Estado): quando o calor dos fatos pode esconder elementos, prefira a instauração/apuração à prisão precipitada do coenvolvido de papel duvidoso.

### Passo 5 — Cautelares e diligências acessórias

Verifique a necessidade de: requisição de exame de corpo de delito e de perícias (drogas, arma, local); apreensão e custódia de objetos; representação por busca e apreensão; representação por afastamento de sigilo de dados telefônicos/telemáticos; Formulário Nacional de Avaliação de Risco (FONAR) em VD; ciência à vítima sobre medidas protetivas; oitiva dos policiais como condutor e testemunhas; declarações da vítima com termo de representação/renúncia; checagem de mandados de prisão em aberto antes de qualquer liberação.

### Passo 6 — Redigir o despacho

Use a estrutura e a fraseologia reais (ver `references/modelos.md`). Esqueleto:

```
[Abertura]  "Comigo hoje;"  ou  "C. hoje."  ou  "Considerando o recebimento da ocorrência de n.º [....]"

[Síntese do fato]  Narrativa objetiva do que consta da ocorrência, nomeando conduzido, vítima e demais. Encerre, quando couber, com "É a síntese da ocorrência;".

[Tipificação e análise]  Enquadramento em tese, condição de procedibilidade, incidência ou não da 11.340/06, concurso.

[Situação flagrancial]  "o conduzido está em situação de flagrância própria/imprópria, nos termos do art. 302, inciso [..], do CPP..."
   -> se for o caso: "Diante do exposto, com fulcro no art. 304, §1º, do CPP, ratifico a voz de prisão dada ao conduzido."
   -> se não houver flagrância: explicar o afastamento.

[Decisão de mérito do plantão]  Desfecho escolhido (APF / TCO / BOC / IP / não instauração) com fundamento.
   -> preventiva, quando o caso: parágrafo de "REPRESENTAÇÃO PELA PRISÃO PREVENTIVA" com prova da existência do crime, indícios de autoria, risco à ordem pública/vítima e vida pregressa.
   -> VD: registrar a vedação de fiança.

[Providências de Polícia Judiciária]  Lista numerada, dirigida ao escrivão, com os atos a praticar (lavratura, oitivas, perícias, apreensões, FONAR, ciência de protetivas, checagens, liberação após checagem negativa, etc.).

[Fecho]  Quando não instaura: "concluso para análise" / "aguarde-se o prazo decadencial... arquive-se".
```

### Passo 7 — Notas ao Delegado (fora do corpo do despacho)

Após o despacho, em seção separada e enxuta, liste: as **premissas assumidas** por falta de dado; os **pontos de atenção jurídica** (dúvida de tipificação, fiança, competência); e as **diligências que dependem de informação que o usuário não trouxe**. Isso preserva a honestidade sobre lacunas sem poluir a peça.

## Formato de saída

Por padrão, entregue o despacho **direto no chat**, em texto formatado, pronto para o usuário revisar e colar. Gere arquivo .docx apenas se ele pedir ("quero em Word", "gera o arquivo"); nesse caso, acione a skill `docx` e salve na pasta de saída da sessão, apresentando com `present_files`.

## Estilo (preferências do usuário)

- Português do Brasil, tom sério, formal, técnico e impessoal.
- **Não usar travessões** nas peças.
- Conciso e decisório: despacho de plantão é curto. Sem encher linguiça, sem floreio acadêmico.
- Classifique a informação quando relevante: o que é fato narrado, o que é premissa assumida, o que depende de confirmação por base oficial.
- Trate dados pessoais com sigilo funcional; não compile mais do que o fato exige.

## Limites

- Não emite relatório final de inquérito (use `relatorio-final-ip`).
- Não substitui a decisão do Delegado: produz rascunho fundamentado para revisão e assinatura humana.
- Jurisprudência e súmulas, quando citadas, devem ser verificadas; na dúvida, sinalize.
