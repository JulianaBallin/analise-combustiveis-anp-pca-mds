# Apresentação: Comparação de Ferramentas AutoML
## Equipe 9 - FLAML e LightAutoML
### Disciplina: Ciência de Dados - UEA

---

## Slide 1 - Capa

**Título:** Comparação de Ferramentas AutoML: FLAML e LightAutoML

**Subtítulo:** Aplicadas ao Dataset de Combustíveis ANP (2021-2025)

**Equipe 9:**
- Ana Beatriz Maciel Nunes
- Fernando Luiz Da Silva Freire
- Juliana Ballin Lima

> **Print sugerido:** logo da UEA e logo do projeto ANP

---

## Slide 2 - Parte 1: O que é AutoML?

**Ponto principal:** AutoML automatiza etapas repetitivas do ciclo de ML, reduzindo o esforço manual na construção de pipelines de qualidade.

**Etapas automatizadas:**
- Pré-processamento e codificação de variáveis
- Seleção de algoritmos
- Ajuste de hiperparâmetros
- Validação cruzada e seleção do melhor modelo
- Ensemble de modelos

**Etapas que ainda dependem do humano:**
- Definição do problema e da variável-alvo
- Coleta e curadoria dos dados
- Avaliação ética e de vieses
- Interpretação no contexto do domínio

**Mensagem-chave:** AutoML é um acelerador, não um substituto do cientista de dados.

---

## Slide 3 - Parte 1: AutoML substitui o cientista de dados?

**Resposta:** Não.

**Por que não:**
1. Nenhuma ferramenta define o problema correto sozinha
2. Dados ruins produzem modelos ruins, independente da ferramenta
3. Métricas altas sem interpretação podem gerar decisões erradas
4. Implantação em produção, monitoramento e decisões éticas exigem julgamento humano

> **Print sugerido:** diagrama mostrando as etapas de ML com setas indicando o que é automático e o que é humano

---

## Slide 4 - Parte 2: O Dataset

**Nome:** Dataset ANP - Preços e Volumes de Combustíveis (2021-2025)

**Fonte:** Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP) - dados abertos

**Estrutura:**
- 1.619 registros (UF-mes)
- 16 atributos
- 27 estados brasileiros
- 60 meses (jan/2021 a dez/2025)

**Variavel-alvo:** `preco_medio_gasolina_c` (preco medio mensal em R$/litro)

**Tipo de problema:** Regressao

**Qualidade dos dados:**
- Sem valores ausentes
- Variaveis categoricas: `uf` (27 categorias), `regiao` (5 categorias)
- Outlier conhecido: Sao Paulo (volume muito maior que outros estados)

**Divisao treino-teste:** 80% treino (1.295 registros) / 20% teste (324 registros), estratificada por regiao, random\_state = 42

> **Print sugerido:** tabela com as primeiras linhas do dataset ou grafico de distribuicao do preco medio da gasolina C por regiao ao longo do tempo

---

## Slide 5 - Parte 3: FLAML - Configuracao e Processo

**Ferramenta:** FLAML (Fast and Lightweight AutoML) - Microsoft

**Como foi usado:**
```
pip install flaml lightgbm
python -m src.flaml_analysis
```

**Configuracao:**
- Tipo: Regressao
- Metrica: RMSE
- Orcamento de tempo: 60 segundos
- Random state: 42

**Estimadores avaliados automaticamente:**

| Estimador | RMSE validacao | Selecionado |
|-----------|---------------|-------------|
| `lgbm` | 0,1255 | Sim |
| `extra_tree` | 0,1287 | Nao |
| `rf` | 0,2501 | Nao |

**Melhor modelo:** LightGBM com n\_estimators=1294, num\_leaves=22, learning\_rate=0,0132

> **Print sugerido:** print da execucao do script ou captura do terminal mostrando o progresso da FLAML

---

## Slide 6 - Parte 3: FLAML - Resultados

**Metricas no conjunto de teste:**

| Metrica | Valor |
|---------|-------|
| RMSE | 0,1148 |
| MAE | 0,0819 |
| R² | 0,9693 |
| MAPE | 1,3841% |
| Tempo | 60,78 segundos |

**Comparacao com baselines simples:**
- Baseline media do treino: RMSE = 0,6553
- FLAML reduziu o RMSE em 82,5% em relacao a media do treino

**Interpretacao:** o modelo explicou 96,93% da variacao do preco da gasolina C.

> **Print sugerido:** grafico `flaml_real_vs_previsto.png` (valores reais x previstos no conjunto de teste)

---

## Slide 7 - Parte 3: FLAML - Importancia de Atributos

**Principais atributos identificados pelo LightGBM:**
1. preco\_medio\_etanol\_hidratado (maior influencia)
2. participacao\_etanol
3. volume\_etanol\_hidratado\_m3
4. variacao\_volume\_gasolina\_c
5. volume\_gasolina\_c\_m3

**Interpretacao:** o preco do etanol e o principal preditor do preco da gasolina C, o que reflete a dinamica de competicao entre os dois combustiveis no mercado brasileiro.

**Erros por regiao:**
- Menores: Centro-Oeste (MAE 0,069) e Sudeste (MAE 0,070)
- Maior: Sul (MAE 0,101)

> **Print sugerido:** grafico `flaml_importancia_atributos.png` - barras horizontais com os atributos mais importantes

---

## Slide 8 - Parte 4: LightAutoML - Configuracao e Processo

**Ferramenta:** LightAutoML (LAMA) - Sber AI Lab

**Como foi usado:**
```
pip install lightautoml
python -m src.lightautoml_analysis
```

**Configuracao:**
- Tipo: Regressao (`reg`)
- Metrica interna: MSE
- Orcamento de tempo: 120 segundos
- Validacao cruzada: 5 dobras
- Random state: 42

**Diferenciais da LightAutoML:**
- Pipeline de multiplos niveis (modelos base + blending automatico)
- Inferencia automatica do tipo de cada variavel
- Nao exige codificacao manual das variaveis categoricas

**Modelos no pipeline:**
- Nivel 0: modelos lineares regularizados e LightGBM
- Nivel 1: blending automatico das previsoes OOF

> **Print sugerido:** diagrama simplificado da arquitetura de pipeline multinivel da LightAutoML

---

## Slide 9 - Parte 4: LightAutoML - Resultados

**Metricas no conjunto de teste:**

| Metrica | Valor |
|---------|-------|
| RMSE | 0,1134 |
| MAE | 0,0888 |
| R² | 0,9701 |
| MAPE | 1,4942% |
| Tempo | 73,94 segundos |

**Principais atributos:**
1. preco\_medio\_etanol\_hidratado (importancia 9.642)
2. ano (importancia 4.613)
3. participacao\_etanol (importancia 2.964)
4. mes (importancia 866)

**Observacao interessante:** variaveis categoricas `uf` e `regiao` obtiveram importancia zero no metodo rapido, indicando que as variaveis numericas ja capturam as diferencas regionais.

> **Print sugerido:** grafico `lightautoml_real_vs_previsto.png` (valores reais x previstos no conjunto de teste)

---

## Slide 10 - Parte 4: LightAutoML - Importancia e Erros

**Erros por regiao:**

| Regiao | MAE | RMSE |
|--------|-----|------|
| Centro-Oeste | 0,0760 | 0,0968 |
| Sudeste | 0,0848 | 0,1127 |
| Nordeste | 0,0888 | 0,1140 |
| Norte | 0,0917 | 0,1165 |
| Sul | 0,1048 | 0,1251 |

**Ausencia de vies:** erro medio assinado de -0,0028 (praticamente nulo), sem tendencia sistematica de superestimacao ou subestimacao.

**Maximo erro absoluto:** R$ 0,42/litro (bem menor do que o maximo da FLAML, de R$ 0,80/litro)

> **Print sugerido:** grafico `lightautoml_mae_por_regiao.png` ou `lightautoml_hist_erro_absoluto.png`

---

## Slide 11 - Parte 5: Comparativo FLAML x LightAutoML

**Tabela comparativa:**

| Criterio | FLAML | LightAutoML |
|----------|-------|-------------|
| RMSE (teste) | 0,1148 | **0,1134** |
| MAE (teste) | **0,0819** | 0,0888 |
| R² (teste) | 0,9693 | **0,9701** |
| MAPE (teste) | **1,3841%** | 1,4942% |
| Tempo de execucao | **60,78s** | 73,94s |
| Facilidade de uso | **Alta** | Media |
| Transparencia do processo | **Alta** (leaderboard) | Media (sem leaderboard) |
| Instalacao | **Simples** | Media (avisos de pacotes) |
| Pipeline | Estimador unico | Multinivel com blending |

**Conclusao:** as duas ferramentas chegaram a resultados equivalentes. A diferenca de RMSE (0,0014) e menor do que R$ 0,002 por litro.

> **Print sugerido:** tabela comparativa lado a lado com destaque visual nas melhores metricas de cada ferramenta

---

## Slide 12 - Parte 5: Reflexoes Finais

**Ferramenta mais facil de usar:** FLAML (API intuitiva, proxima ao scikit-learn, leaderboard direto)

**Ferramenta com melhor desempenho:** LightAutoML (leve vantagem em RMSE e R²)

**A mais facil foi a melhor?** Nao. A FLAML foi mais facil, mas a LightAutoML teve ligeiramente melhor RMSE.

**O AutoML reduziu o tempo de desenvolvimento?** Sim. De dias de experimentacao manual para menos de 74 segundos de execucao automatica.

**Quais decisoes ainda foram humanas:**
- Definir a variavel-alvo
- Remover colunas com vazamento de dados
- Escolher as metricas de avaliacao
- Interpretar os resultados no contexto do mercado de combustiveis

**Ferramenta recomendada para iniciantes:** FLAML

**Por que:** API simples, documentacao clara, transparencia do processo, instalacao sem complicacoes e desempenho competitivo.

> **Print sugerido:** grafico de barras comparando o RMSE das duas ferramentas vs. baselines simples

---

## Slide 13 - Encerramento

**Resumo dos resultados:**
- Dataset: 1.619 registros, 27 UFs, jan/2021 a dez/2025
- Problema: regressao do preco medio da gasolina C
- FLAML: RMSE 0,1148, R² 0,9693, tempo 60,78s
- LightAutoML: RMSE 0,1134, R² 0,9701, tempo 73,94s
- Ambas superaram baselines simples com ampla margem

**Licao aprendida:** AutoML e uma ferramenta poderosa para prototipacao e baseline, mas o papel do cientista de dados permanece essencial para definir o problema, garantir a integridade dos dados e interpretar os resultados com responsabilidade.

> **Print sugerido:** imagem do repositorio GitHub ou do notebook com os graficos gerados pelos experimentos

---

## Notas para a apresentacao

### Evidencias coletadas disponiveis no repositorio

| Arquivo | Onde usar |
|---------|-----------|
| `outputs/figures/flaml_real_vs_previsto.png` | Slide 6 - FLAML resultados |
| `outputs/figures/flaml_importancia_atributos.png` | Slide 7 - FLAML importancia |
| `outputs/figures/flaml_mae_por_regiao.png` | Slide 7 - erros regionais |
| `outputs/figures/lightautoml_real_vs_previsto.png` | Slide 9 - LightAutoML resultados |
| `outputs/figures/lightautoml_importancia_atributos.png` | Slide 9 - LightAutoML importancia |
| `outputs/figures/lightautoml_mae_por_regiao.png` | Slide 10 - erros regionais |
| `outputs/figures/lightautoml_hist_erro_absoluto.png` | Slide 10 - distribuicao erros |
| `outputs/tables/flaml_metricas.csv` | Verificacao dos numeros |
| `outputs/tables/lightautoml_metricas.csv` | Verificacao dos numeros |
| `docs/relatorios/v3.0/relatorio_auto_ml_equipe9_v03.0.pdf` | Relatorio completo para entrega |
