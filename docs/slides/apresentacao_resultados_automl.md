# Apresentação: Comparação de Ferramentas AutoML
## Equipe 9 - FLAML e LightAutoML
### Disciplina: Ciência de Dados - UEA

---

## Slide 1 - Capa

**Título:** Comparação de Ferramentas AutoML: FLAML e LightAutoML

**Subtítulo:** Aplicadas ao conjunto de dados de combustíveis ANP (2021-2025)

**Equipe 9:**
- Ana Beatriz Maciel Nunes
- Fernando Luiz Da Silva Freire
- Juliana Ballin Lima

> **Imagem sugerida:** logo da UEA e logo do projeto ANP

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
2. Dados ruins produzem modelos ruins, independentemente da ferramenta
3. Métricas altas sem interpretação podem gerar decisões erradas
4. Implantação em produção, monitoramento e decisões éticas exigem julgamento humano

> **Imagem sugerida:** diagrama mostrando as etapas de ML com setas indicando o que é automático e o que é humano

---

## Slide 4 - Parte 2: O Conjunto de Dados

**Nome:** Dataset ANP - Preços e Volumes de Combustíveis (2021-2025)

**Fonte:** Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP) - dados abertos

**Estrutura:**
- 1.619 registros (UF-mês)
- 16 atributos
- 27 estados brasileiros
- 60 meses (jan/2021 a dez/2025)

**Variável-alvo:** `preco_medio_gasolina_c` (preço médio mensal em R$/litro)

**Tipo de problema:** Regressão

**Qualidade dos dados:**
- Sem valores ausentes
- Variáveis categóricas: `uf` (27 categorias), `regiao` (5 categorias)
- Outlier conhecido: São Paulo (volume muito maior que outros estados)

**Divisão treino-teste:** 80% treino (1.295 registros) / 20% teste (324 registros), estratificada por região, com `random_state = 42`.

**Evidência coletada:** arquivo tratado `data/processed/dataset_anp_pca_mds_2021_2025.csv`, com 1.619 linhas e 16 colunas, sem valores ausentes.

> **Imagem sugerida:** tabela com as primeiras linhas do dataset ou gráfico de distribuição do preço médio da gasolina C por região ao longo do tempo

---

## Slide 5 - Parte 3: FLAML - Configuração e Processo

**Ferramenta:** FLAML (Fast and Lightweight AutoML) - Microsoft

**Como foi usado:**
```
pip install flaml lightgbm
python -m src.flaml_analysis
```

**Configuração:**
- Tipo: Regressão
- Métrica: RMSE
- Orçamento de tempo: 60 segundos
- Semente aleatória: 42

**Estimadores avaliados automaticamente:**

| Estimador | RMSE de validação | Selecionado |
|-----------|---------------|-------------|
| `lgbm` | 0,1255 | Sim |
| `extra_tree` | 0,1287 | Não |
| `rf` | 0,2501 | Não |

**Melhor modelo:** LightGBM com `n_estimators = 1294`, `num_leaves = 22` e `learning_rate = 0,0132`.

**Evidência coletada:** `outputs/tables/flaml_leaderboard.csv` e `outputs/tables/flaml_configuracao.json`.

> **Imagem sugerida:** captura do terminal mostrando o progresso da FLAML

---

## Slide 6 - Parte 3: FLAML - Resultados

**Métricas no conjunto de teste:**

| Métrica | Valor |
|---------|-------|
| RMSE | 0,1148 |
| MAE | 0,0819 |
| R² | 0,9693 |
| MAPE | 1,3841% |
| Tempo | 60,78 segundos |

**Comparação com baselines simples:**
- Baseline pela média do treino: RMSE = 0,6553
- FLAML reduziu o RMSE em 82,5% em relação à média do treino

**Interpretação:** o modelo explicou 96,93% da variação do preço da gasolina C.

**Evidência coletada:** `outputs/tables/flaml_metricas.csv` e `outputs/tables/flaml_baseline_comparacao.csv`.

> **Imagem sugerida:** gráfico `flaml_real_vs_previsto.png` (valores reais x previstos no conjunto de teste)
> **Imagem opcional:** gráfico `flaml_baseline_rmse.png` para mostrar a comparação com baselines

---

## Slide 7 - Parte 3: FLAML - Importância de Atributos

**Principais atributos identificados pelo LightGBM:**
1. `preco_medio_etanol_hidratado` (maior influência)
2. `participacao_etanol`
3. `volume_etanol_hidratado_m3`
4. `variacao_volume_gasolina_c`
5. `volume_gasolina_c_m3`

**Interpretação:** o preço do etanol é o principal preditor do preço da gasolina C, o que reflete a dinâmica de competição entre os dois combustíveis no mercado brasileiro.

**Erros por região:**
- Menores: Centro-Oeste (MAE 0,069) e Sudeste (MAE 0,070)
- Maior: Sul (MAE 0,101)

**Evidência coletada:** `outputs/tables/flaml_importancia_atributos.csv` e `outputs/tables/flaml_analise_erros_regiao.csv`.

> **Imagem sugerida:** gráfico `flaml_importancia_atributos.png` - barras horizontais com os atributos mais importantes

---

## Slide 8 - Parte 4: LightAutoML - Configuração e Processo

**Ferramenta:** LightAutoML (LAMA) - Sber AI Lab

**Como foi usado:**
```
pip install lightautoml
python -m src.lightautoml_analysis
```

**Configuração:**
- Tipo: Regressão (`reg`)
- Métrica interna: MSE
- Orçamento de tempo: 120 segundos
- Validação cruzada: 5 dobras
- Semente aleatória: 42

**Diferenciais da LightAutoML:**
- Pipeline de múltiplos níveis (modelos base + blending automático)
- Inferência automática do tipo de cada variável
- Não exige codificação manual das variáveis categóricas

**Modelos no pipeline:**
- Nível 0: modelos lineares regularizados e LightGBM
- Nível 1: blending automático das previsões OOF

**Evidência coletada:** script reprodutível `src/lightautoml_analysis.py`, com `Task("reg", metric="mse")`, 5 dobras de validação cruzada e orçamento de 120 segundos.

> **Imagem sugerida:** diagrama simplificado da arquitetura de pipeline multinível da LightAutoML

---

## Slide 9 - Parte 4: LightAutoML - Resultados

**Métricas no conjunto de teste:**

| Métrica | Valor |
|---------|-------|
| RMSE | 0,1134 |
| MAE | 0,0888 |
| R² | 0,9701 |
| MAPE | 1,4942% |
| Tempo | 73,94 segundos |

**Principais atributos:**
1. `preco_medio_etanol_hidratado` (importância 9.642)
2. `ano` (importância 4.613)
3. `participacao_etanol` (importância 2.964)
4. `mes` (importância 866)

**Observação interessante:** variáveis categóricas `uf` e `regiao` obtiveram importância zero no método rápido, indicando que as variáveis numéricas já capturam as diferenças regionais.

**Evidência coletada:** `outputs/tables/lightautoml_metricas.csv` e `outputs/tables/lightautoml_importancia_atributos.csv`.

> **Imagem sugerida:** gráfico `lightautoml_real_vs_previsto.png` (valores reais x previstos no conjunto de teste)
> **Imagem opcional:** gráfico `lightautoml_importancia_atributos.png` para destacar os principais atributos

---

## Slide 10 - Parte 4: LightAutoML - Importância e Erros

**Erros por região:**

| Região | MAE | RMSE |
|--------|-----|------|
| Centro-Oeste | 0,0760 | 0,0968 |
| Sudeste | 0,0848 | 0,1127 |
| Nordeste | 0,0888 | 0,1140 |
| Norte | 0,0917 | 0,1165 |
| Sul | 0,1048 | 0,1251 |

**Ausência de viés:** erro médio assinado de -0,0028 (praticamente nulo), sem tendência sistemática de superestimação ou subestimação.

**Máximo erro absoluto:** R$ 0,42/litro (bem menor do que o máximo da FLAML, de R$ 0,80/litro)

**Evidência coletada:** `outputs/tables/lightautoml_analise_erros_regiao.csv`, `outputs/tables/lightautoml_resumo_erros.csv` e `outputs/tables/lightautoml_previsoes_teste.csv`.

> **Imagem sugerida:** gráfico `lightautoml_mae_por_regiao.png` ou `lightautoml_hist_erro_absoluto.png`

---

## Slide 11 - Parte 5: Comparativo FLAML x LightAutoML

**Tabela comparativa:**

| Critério | FLAML | LightAutoML |
|----------|-------|-------------|
| RMSE (teste) | 0,1148 | **0,1134** |
| MAE (teste) | **0,0819** | 0,0888 |
| R² (teste) | 0,9693 | **0,9701** |
| MAPE (teste) | **1,3841%** | 1,4942% |
| Tempo de execução | **60,78s** | 73,94s |
| Facilidade de uso | **Alta** | Média |
| Transparência do processo | **Alta** (leaderboard) | Média (sem leaderboard) |
| Instalação | **Simples** | Média (avisos de pacotes) |
| Pipeline | Estimador único | Multinível com blending |

**Conclusão:** as duas ferramentas chegaram a resultados equivalentes. A diferença de RMSE (0,0014) é menor do que R$ 0,002 por litro.

**Evidência coletada:** tabelas `outputs/tables/flaml_metricas.csv` e `outputs/tables/lightautoml_metricas.csv`, ambas calculadas no mesmo conjunto de teste.

> **Imagem sugerida:** tabela comparativa lado a lado com destaque visual nas melhores métricas de cada ferramenta

---

## Slide 12 - Parte 5: Reflexões Finais

**Ferramenta mais fácil de usar:** FLAML (API intuitiva, próxima ao scikit-learn, leaderboard direto)

**Ferramenta com melhor desempenho:** LightAutoML (leve vantagem em RMSE e R²)

**A mais fácil foi a melhor?** Não. A FLAML foi mais fácil, mas a LightAutoML teve ligeiramente melhor RMSE.

**O AutoML reduziu o tempo de desenvolvimento?** Sim. De dias de experimentação manual para menos de 74 segundos de execução automática.

**Quais decisões ainda foram humanas:**
- Definir a variável-alvo
- Remover colunas com vazamento de dados
- Escolher as métricas de avaliação
- Interpretar os resultados no contexto do mercado de combustíveis

**Ferramenta recomendada para iniciantes:** FLAML

**Por que:** API simples, documentação clara, transparência do processo, instalação sem complicações e desempenho competitivo.

> **Imagem sugerida:** gráfico de barras comparando o RMSE das duas ferramentas vs. baselines simples

---

## Slide 13 - Encerramento

**Resumo dos resultados:**
- Dataset: 1.619 registros, 27 UFs, jan/2021 a dez/2025
- Problema: regressão do preço médio da gasolina C
- FLAML: RMSE 0,1148, R² 0,9693, tempo 60,78s
- LightAutoML: RMSE 0,1134, R² 0,9701, tempo 73,94s
- Ambas superaram baselines simples com ampla margem

**Lição aprendida:** AutoML é uma ferramenta poderosa para prototipação e baseline, mas o papel do cientista de dados permanece essencial para definir o problema, garantir a integridade dos dados e interpretar os resultados com responsabilidade.

> **Imagem sugerida:** imagem do repositório GitHub ou do notebook com os gráficos gerados pelos experimentos

---

## Notas para a apresentação

### Evidências coletadas disponíveis no repositório

| Arquivo | Onde usar |
|---------|-----------|
| `outputs/figures/flaml_real_vs_previsto.png` | Slide 6 - FLAML resultados |
| `outputs/figures/flaml_baseline_rmse.png` | Slide 6 - comparação com baselines |
| `outputs/figures/flaml_importancia_atributos.png` | Slide 7 - FLAML importância |
| `outputs/figures/flaml_mae_por_regiao.png` | Slide 7 - erros regionais da FLAML |
| `outputs/figures/lightautoml_real_vs_previsto.png` | Slide 9 - LightAutoML resultados |
| `outputs/figures/lightautoml_importancia_atributos.png` | Slide 9 ou 10 - LightAutoML importância |
| `outputs/figures/lightautoml_mae_por_regiao.png` | Slide 10 - erros regionais |
| `outputs/figures/lightautoml_hist_erro_absoluto.png` | Slide 10 - distribuição dos erros |
| `outputs/tables/flaml_leaderboard.csv` | Slide 5 - estimadores avaliados |
| `outputs/tables/flaml_metricas.csv` | Verificação dos números |
| `outputs/tables/flaml_baseline_comparacao.csv` | Slide 6 - baselines simples |
| `outputs/tables/lightautoml_metricas.csv` | Verificação dos números |
| `outputs/tables/lightautoml_resumo_erros.csv` | Slide 10 - distribuição dos resíduos |
| `docs/relatorios/v3.0/relatorio_auto_ml_equipe9_v03.0.pdf` | Relatório completo para entrega |
