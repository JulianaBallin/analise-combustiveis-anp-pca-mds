from __future__ import annotations

import pandas as pd
from sklearn.manifold import MDS


def aplicar_mds(dados_padronizados: pd.DataFrame, max_registros: int = 800):
    amostra = dados_padronizados.copy()
    if len(amostra) > max_registros:
        amostra = amostra.sample(max_registros, random_state=42)

    mds = MDS(
        n_components=2,
        metric_mds=True,
        random_state=42,
        n_init=4,
        init="random",
        max_iter=300,
        normalized_stress="auto",
        metric="euclidean",
    )
    coords = mds.fit_transform(amostra)
    resultado = pd.DataFrame(coords, columns=["MDS1", "MDS2"], index=amostra.index)
    return resultado, mds
