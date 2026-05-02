# Roteiro da apresentação: PCA e MDS em dados da ANP

## Slide 1: Abertura

Começar situando o tema. O trabalho usa dados públicos da ANP para observar preço da gasolina C, volume vendido de gasolina C e participação do etanol hidratado nos estados brasileiros.

## Slide 2: Problema investigado

Explicar o cenário da rede de postos ou distribuidora. A gestão precisa tomar decisões de estoque, mix de produtos, campanhas e metas regionais, mas olhar apenas o faturamento agregado não mostra se a mudança de volume veio de preço, substituição por etanol ou diferença regional.

Fala sugerida: "Nossa pergunta principal foi entender em quais estados e períodos o preço da gasolina C se relaciona com o volume vendido e com a presença do etanol."

## Slide 3: Dataset e preparação

Apresentar as duas bases:

- Série histórica mensal de preços por estado.
- Vendas mensais de derivados de petróleo e etanol por UF.

O recorte usado foi de 01/2021 a 12/2025, com 27 UFs e 1619 registros (join mês + sigla `uf`; regiões como Centro-Oeste deixaram de causar falha no merge). Cada linha é um mês em uma UF. Features numéricas receberam `StandardScaler`.

## Slide 4: PCA

Explicar que o PCA transforma as variáveis originais em componentes principais. Os dois primeiros componentes explicaram 57.5% da variância total.

Destacar:

- PC1 explicou 40.5%.
- PC2 explicou 16.9%.
- PC1 foi mais influenciado por participacao_etanol, razao_etanol_gasolina, volume_etanol_hidratado_m3, preco_relativo_etanol_gasolina.
- PC2 foi mais influenciado por variacao_preco_gasolina_c, volume_gasolina_c_m3, variacao_volume_gasolina_c, preco_medio_gasolina_c.

Fala sugerida: "O primeiro eixo ficou ligado principalmente à composição do consumo e ao peso do etanol. O segundo eixo capturou mais as oscilações mensais de preço e volume."

## Slide 5: MDS

Explicar que o MDS posiciona registros semelhantes próximos entre si, usando distâncias no espaço padronizado. O stress encontrado foi 208340.59, então o gráfico deve ser lido como apoio visual, não como prova exata de causalidade.

Fala sugerida: "No MDS, o interesse é ver quem ficou perto de quem. Se dois registros aparecem próximos, eles têm perfis parecidos considerando preço, volume, participação do etanol e variações mensais."

## Slide 6: Padrões e outliers

Comentar que os estados com maior participação média do etanol no recorte foram MT (59.9%), GO (50.3%), SP (48.4%), MG (33.0%), RJ (26.2%). São Paulo apareceu com destaque entre os outliers porque combina escala muito alta de vendas e participação forte do etanol.

Fala sugerida: "O ponto atípico não significa erro. Nesse caso, ele mostra que São Paulo tem um comportamento muito diferente em escala e composição do consumo."

## Slide 7: Comparação e conclusão

Fechar comparando os métodos:

- PCA ajuda a explicar quais variáveis organizam os dados.
- MDS ajuda a visualizar registros parecidos.
- PCA pode apoiar redução de features em modelos futuros.
- MDS é melhor como visualização exploratória.

Conclusão para falar: "Os dois métodos ajudaram a enxergar que o mercado não se resume ao preço da gasolina. Volume, participação do etanol, preço relativo e variações mensais também estruturam os padrões regionais."
