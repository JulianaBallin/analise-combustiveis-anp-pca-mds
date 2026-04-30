from __future__ import annotations

import pandas as pd
from sklearn.decomposition import PCA


def aplicar_pca(dados_padronizados: pd.DataFrame, n_components: int = 2):
    pca = PCA(n_components=n_components, random_state=42)
    componentes = pca.fit_transform(dados_padronizados)
    resultado = pd.DataFrame(componentes, columns=["PC1", "PC2"], index=dados_padronizados.index)
    cargas = pd.DataFrame(
        pca.components_.T,
        index=dados_padronizados.columns,
        columns=["PC1", "PC2"],
    )
    variancia = pd.DataFrame(
        {
            "componente": ["PC1", "PC2"],
            "variancia_explicada": pca.explained_variance_ratio_,
            "variancia_acumulada": pca.explained_variance_ratio_.cumsum(),
        }
    )
    return resultado, cargas, variancia, pca
