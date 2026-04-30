# Relatório curto - PCA e MDS em dados da ANP

## 1. Problema investigado

O projeto investiga como as variações no preço médio da gasolina C se associam ao volume mensal vendido de gasolina C e à participação do etanol hidratado nos estados brasileiros. O cenário de negócio é o de uma rede de postos ou distribuidora que precisa decidir estoque, mix comercial, campanhas e metas regionais sem depender apenas do faturamento agregado.

## 2. Explicação teórica do PCA

PCA, ou Análise de Componentes Principais, é uma técnica de redução de dimensionalidade que transforma variáveis numéricas correlacionadas em componentes principais. Cada componente é uma combinação linear das variáveis originais. O primeiro componente concentra a maior variância possível dos dados; o segundo concentra a maior parte da variância restante, mantendo ortogonalidade em relação ao primeiro.

No projeto, o PCA foi usado para projetar oito features numéricas em duas dimensões, observar tendências, identificar registros afastados e medir quais variáveis mais contribuíram para os primeiros componentes.

## 3. Explicação teórica do MDS

MDS, ou Escalonamento Multidimensional, é uma técnica de visualização que parte das distâncias entre registros. Seu objetivo é posicionar pontos em poucas dimensões preservando, tanto quanto possível, as proximidades do espaço original. Registros parecidos ficam próximos; registros diferentes tendem a ficar afastados.

Ao contrário do PCA, o MDS não informa diretamente a contribuição de cada feature. Por isso, ele foi usado principalmente para comparar similaridades, agrupamentos e outliers com a leitura obtida no PCA.

## 4. Dataset utilizado

Foram usadas duas bases públicas da ANP:

- Série histórica mensal do levantamento de preços por estado, com preço médio de revenda da gasolina C e do etanol hidratado.
- Vendas de derivados de petróleo e etanol, com volumes mensais vendidos em metros cúbicos por UF e produto.

O recorte final contém 1379 registros, 23 UFs e período de 01/2021 a 12/2025. Cada registro representa uma combinação UF-mês após cruzamento entre preços e vendas.

Fontes:

- https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/precos-revenda-e-de-distribuicao-combustiveis/shlp/mensal/mensal-estados-desde-jan2013.xlsx
- https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/vdpb/vendas-derivados-petroleo-e-etanol/vendas-combustiveis-m3-1990-2025.csv

## 5. Features selecionadas e justificativa

As features numéricas analisadas foram:

- `preco_medio_gasolina_c`: preço central da pergunta de negócio.
- `volume_gasolina_c_m3`: demanda mensal do combustível principal.
- `volume_etanol_hidratado_m3`: demanda do possível substituto.
- `variacao_preco_gasolina_c`: mede choques ou quedas mensais de preço.
- `variacao_volume_gasolina_c`: mede a mudança mensal da demanda de gasolina.
- `participacao_etanol`: indica o peso do etanol no total gasolina C + etanol.
- `razao_etanol_gasolina`: compara diretamente o volume de etanol com o de gasolina.
- `preco_relativo_etanol_gasolina`: compara o preço do etanol com o da gasolina.

A UF e a região foram mantidas como variáveis categóricas para colorir os gráficos e apoiar a interpretação visual.

## 6. Preparação e padronização dos dados

As bases foram carregadas dos links oficiais da ANP, os nomes de estados foram normalizados, os produtos de interesse foram filtrados, os dados foram agregados por mês e UF e as tabelas de preço e volume foram cruzadas. Em seguida foram criadas variáveis derivadas de participação, razão, preço relativo e variações percentuais mensais.

Como as features têm escalas muito diferentes, todas as variáveis numéricas foram padronizadas com `StandardScaler`. Essa etapa impede que volumes em m³ dominem indevidamente preços em reais ou indicadores percentuais.

## 7. PCA 2D, variância explicada e contribuição das variáveis

Os dois primeiros componentes explicaram 63.8% da variância total: PC1 explicou 47.5% e PC2 explicou 16.3%.

As variáveis que mais influenciaram PC1 foram: razao_etanol_gasolina, participacao_etanol, volume_etanol_hidratado_m3, volume_gasolina_c_m3. As que mais influenciaram PC2 foram: variacao_preco_gasolina_c, variacao_volume_gasolina_c, preco_medio_gasolina_c, preco_relativo_etanol_gasolina.

Isso indica que a primeira dimensão separou principalmente estados e meses pelo porte e composição do consumo, enquanto a segunda dimensão destacou mudanças relativas de preço, volume e competitividade do etanol.

Figura principal: `outputs/figures/pca_2d_regiao.png`.

## 8. MDS 2D e interpretação das proximidades

O MDS foi aplicado sobre os dados padronizados, usando distância euclidiana e amostra reprodutível de até 800 registros para manter a visualização viável. O stress calculado foi 179725.65; quanto menor esse valor, melhor a preservação das distâncias na projeção.

No gráfico MDS, registros próximos representam UFs e meses com perfis semelhantes de preço, volume, participação do etanol, razão etanol/gasolina e variações mensais. A leitura visual mostrou proximidade entre registros de comportamento regional semelhante e maior afastamento de estados com peso muito alto de etanol ou volumes muito superiores ao restante do país.

Figura principal: `outputs/figures/mds_2d_regiao.png`.

## 9. Comparação entre PCA e MDS

O PCA foi mais útil para explicar quais variáveis estruturam a projeção, pois fornece variância explicada e cargas dos componentes. O MDS foi mais útil para visualizar similaridade entre registros sem exigir que a estrutura principal seja linear.

Os padrões gerais foram compatíveis: estados com maior participação do etanol e grande escala de vendas tenderam a se destacar; registros de menor escala ou com participação baixa do etanol ficaram em áreas mais próximas entre si. A diferença é que o PCA facilita a explicação matemática, enquanto o MDS facilita a leitura de vizinhança.

## 10. Padrões identificados

Antes da análise, esperava-se encontrar diferenças regionais, destaque de estados com maior consumo absoluto, separação parcial de mercados onde o etanol tem maior relevância e alguns meses atípicos ligados a variações bruscas de preço ou volume.

Os estados com maior participação média do etanol no recorte foram: SP (48.4%), MG (33.0%), RJ (26.2%), PR (25.4%), AM (21.1%). Os estados com menor participação média foram: AP (0.7%), RS (1.9%), RR (3.6%), RO (4.1%), SC (4.9%).

Esses padrões fazem sentido no contexto do projeto, porque o etanol é mais competitivo e mais presente em alguns mercados, enquanto em outros a gasolina C domina a composição de consumo.

## 11. Outliers encontrados

Os principais registros afastados no PCA foram:

- SP em 03/2024: gasolina R$ 5.61, participação do etanol 53.5%, variação de volume da gasolina 13.6%.
- SP em 12/2025: gasolina R$ 6.06, participação do etanol 49.8%, variação de volume da gasolina 17.7%.
- SP em 12/2023: gasolina R$ 5.50, participação do etanol 51.0%, variação de volume da gasolina 8.6%.
- SP em 12/2024: gasolina R$ 5.96, participação do etanol 52.1%, variação de volume da gasolina 7.3%.
- SP em 10/2024: gasolina R$ 5.91, participação do etanol 52.7%, variação de volume da gasolina 9.0%.
- SP em 05/2024: gasolina R$ 5.64, participação do etanol 53.4%, variação de volume da gasolina 1.6%.

Esses outliers são explicados principalmente por combinações de grande escala de volume, participação elevada do etanol, variações mensais fortes ou preço relativo do etanol muito diferente do padrão nacional.

## 12. Riscos de interpretação

Existe risco de interpretar agrupamentos visuais como prova causal. PCA e MDS mostram associação e proximidade, mas não provam que o aumento de preço causou diretamente queda de volume. Também há risco de perder informação ao reduzir oito variáveis para duas dimensões, além de limitações das bases agregadas da ANP e ausência de variáveis externas como renda, frota, inflação, câmbio, clima e campanhas comerciais.

## 13. Uso para redução de features

O PCA pode ser usado como apoio para redução de features, especialmente se um modelo futuro precisar condensar variáveis correlacionadas de preço, volume e participação. Porém, como os dois primeiros componentes não preservam toda a variância, uma redução agressiva para apenas duas dimensões deve ser feita com cautela.

O MDS é mais adequado para visualização exploratória do que para redução de features em modelos preditivos, porque suas dimensões não têm interpretação direta por variável.

## 14. Conclusão

PCA e MDS ajudaram a compreender que o mercado analisado não se organiza apenas pelo preço da gasolina C. A escala de vendas, a presença relativa do etanol, a razão entre etanol e gasolina e as variações mensais também estruturam os padrões observados.

Para o cenário da rede de postos ou distribuidora, os métodos ajudam a identificar UFs e meses com comportamento semelhante, encontrar registros atípicos e apoiar decisões de estoque, mix de produtos e campanhas regionais. A análise deve ser vista como etapa exploratória robusta, não como prova causal definitiva.
