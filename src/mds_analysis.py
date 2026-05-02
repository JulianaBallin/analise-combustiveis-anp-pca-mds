from __future__ import annotations

import pandas as pd
from sklearn.manifold import MDS


def aplicar_mds(dados_padronizados: pd.DataFrame, max_registros: int = 800):
    amostra = dados_padronizados.copy()
    if len(amostra) > max_registros:
        amostra = amostra.sample(max_registros, random_state=42)

    # sklearn 1.7+: usar dissimilaridade explícita e metric=True ao passar dados brutos evita breakage
    # com defaults que mudaram; n_init fixo também evita warnings de comportamento novo.
    mds = MDS(
        n_components=2,
        metric=True,
        dissimilarity="euclidean",
        normalized_stress="auto",
        n_init=4,
        max_iter=300,
        random_state=42,
        verbose=0,
    )
    coords = mds.fit_transform(amostra)
    resultado = pd.DataFrame(coords, columns=["MDS1", "MDS2"], index=amostra.index)
    return resultado, mds
