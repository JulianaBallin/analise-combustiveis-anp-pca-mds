# Roteiro da apresentação: PCA e MDS em dados da ANP

---

## Slide 1: Abertura

**Conteúdo visível no slide:**
- Título: PCA e MDS em dados da ANP
- Subtítulo: Gasolina C, etanol hidratado, preços e volumes por UF

Começar situando o tema. O trabalho usa dados públicos da ANP para observar o preço da gasolina C, o volume vendido de gasolina C e a participação do etanol hidratado nos estados brasileiros ao longo do período 01/2021 a 12/2025.

---

## Slide 2: Problema investigado

**Conteúdo visível no slide:**
- Entender associações entre preço da gasolina C, volume vendido e participação do etanol.
- Apoiar decisões de estoque, mix comercial, campanhas e metas regionais.
- Tratar a análise como exploração visual e estatística, sem inferir causalidade direta.

Explicar o cenário da rede de postos ou distribuidora. A gestão precisa tomar decisões de estoque, mix de produtos, campanhas e metas regionais, mas olhar apenas o faturamento agregado não mostra se a mudança de volume veio de preço, substituição por etanol ou diferença regional.

Fala sugerida: "Nossa pergunta principal foi entender em quais estados e períodos o preço da gasolina C se relaciona com o volume vendido e com a presença do etanol."

---

## Slide 3: Dataset e preparação

**Conteúdo visível no slide:**
- Recorte: 01/2021 a 12/2025, 27 UFs e 1619 registros UF-mês.
- Fontes: série histórica mensal de preços e vendas mensais de derivados e etanol da ANP.
- Features padronizadas com StandardScaler para equilibrar escalas diferentes.

Apresentar as duas bases:

- Série histórica mensal de preços por estado.
- Vendas mensais de derivados de petróleo e etanol por UF.

O join foi feito por mês e sigla `uf`. Regiões como Centro-Oeste deixaram de causar falha no merge por grafia diferente entre as bases. Cada linha é um mês em uma UF. Features numéricas receberam `StandardScaler`.

---

## Slide 4: PCA

**Conteúdo visível no slide:**
- PC1 explicou 40.5% e PC2 explicou 16.9%.
- Variância acumulada dos dois primeiros componentes: 57.5%.
- Principais influências em PC1: participacao_etanol, razao_etanol_gasolina, volume_etanol_hidratado_m3, preco_relativo_etanol_gasolina.
- Principais influências em PC2: variacao_preco_gasolina_c, volume_gasolina_c_m3, variacao_volume_gasolina_c, preco_medio_gasolina_c.
- **Imagem:** gráfico de dispersão PCA 2D com pontos coloridos por região (outputs/figures/pca_2d_regiao.png).

Explicar que o PCA transforma as variáveis originais em componentes principais. Os dois primeiros componentes explicaram 57.5% da variância total.

Fala sugerida: "O primeiro eixo ficou ligado principalmente à composição do consumo e ao peso do etanol. O segundo eixo capturou mais as oscilações mensais de preço e volume."

---

## Slide 5: MDS

**Conteúdo visível no slide:**
- Representa proximidades entre registros usando distâncias no espaço padronizado.
- Stress do MDS: 208340.59.
- Registros próximos indicam comportamento semelhante de preço, volume e participação do etanol.
- **Imagem:** gráfico de dispersão MDS 2D com pontos coloridos por região (outputs/figures/mds_2d_regiao.png).

Explicar que o MDS posiciona registros semelhantes próximos entre si, usando distâncias no espaço padronizado. O stress encontrado foi 208340.59; o gráfico deve ser lido como apoio visual, não como prova exata de causalidade.

Fala sugerida: "No MDS, o interesse é ver quem ficou perto de quem. Se dois registros aparecem próximos, eles têm perfis parecidos considerando preço, volume, participação do etanol e variações mensais."

---

## Slide 6: Padrões e outliers

**Conteúdo visível no slide:**
- Estados com maior participação do etanol aparecem mais afastados dos mercados dependentes de gasolina.
- Outliers combinam grande volume, participação elevada do etanol ou variações mensais fortes.
- Os padrões observados fazem sentido para a hipótese de diferenças regionais de substituição.
- **Imagem:** gráfico de barras com os registros mais afastados na projeção PCA (outputs/figures/outliers_pca.png).

Comentar que os estados com maior participação média do etanol no recorte foram MT (59.9%), GO (50.3%), SP (48.4%), MG (33.0%), RJ (26.2%). São Paulo apareceu com destaque entre os outliers porque combina escala muito alta de vendas e participação forte do etanol.

Fala sugerida: "O ponto atípico não significa erro. Nesse caso, ele mostra que São Paulo tem um comportamento muito diferente em escala e composição do consumo."

---

## Slide 7: Comparação e conclusão

**Conteúdo visível no slide:**
- PCA explica a contribuição das variáveis e pode apoiar redução de features.
- MDS é mais adequado para visualização de similaridade e leitura de vizinhanças.
- Os métodos ajudaram a mapear grupos, tendências e registros atípicos úteis para decisões regionais.

Fechar comparando os métodos:

- PCA ajuda a explicar quais variáveis organizam os dados.
- MDS ajuda a visualizar registros parecidos.
- PCA pode apoiar redução de features em modelos futuros.
- MDS é melhor como visualização exploratória.

Conclusão para falar: "Os dois métodos ajudaram a enxergar que o mercado não se resume ao preço da gasolina. Volume, participação do etanol, preço relativo e variações mensais também estruturam os padrões regionais."
