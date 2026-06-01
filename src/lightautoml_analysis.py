from __future__ import annotations

import time
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "processed" / "dataset_anp_pca_mds_2021_2025.csv"
OUT_FIG = ROOT / "outputs" / "figures"
OUT_TAB = ROOT / "outputs" / "tables"

TARGET = "preco_medio_gasolina_c"
RANDOM_STATE = 42
TEST_SIZE = 0.2
TIME_BUDGET_SECONDS = 120

REMOVER_DA_MODELAGEM = [
    TARGET,
    "mes_ano",
    "uf_nome",
    "variacao_preco_gasolina_c",
    "preco_relativo_etanol_gasolina",
]


def main() -> None:
    OUT_FIG.mkdir(parents=True, exist_ok=True)
    OUT_TAB.mkdir(parents=True, exist_ok=True)

    torch.set_num_threads(4)

    dados = carregar_dataset()
    train_df, test_df = dividir_treino_teste(dados)

    colunas_remover = [c for c in REMOVER_DA_MODELAGEM if c in dados.columns and c != TARGET]
    train_para_lama = train_df.drop(columns=colunas_remover)
    test_para_lama = test_df.drop(columns=colunas_remover + [TARGET])

    task = Task("reg", metric="mse", greater_is_better=False)
    automl = TabularAutoML(
        task=task,
        timeout=TIME_BUDGET_SECONDS,
        cpu_limit=4,
        reader_params={"n_jobs": 4, "cv": 5, "random_state": RANDOM_STATE},
    )

    roles = {"target": TARGET}

    print("Iniciando treinamento LightAutoML...")
    inicio = time.perf_counter()
    automl.fit_predict(train_para_lama, roles=roles, verbose=0)
    tempo_execucao = time.perf_counter() - inicio
    print(f"Treinamento concluído em {tempo_execucao:.2f}s")

    test_pred = automl.predict(test_para_lama)

    previsoes = np.array(test_pred.data[:, 0])
    y_test = test_df[TARGET].values

    rmse = mean_squared_error(y_test, previsoes) ** 0.5
    mae = mean_absolute_error(y_test, previsoes)
    r2 = r2_score(y_test, previsoes)
    mape = float(np.mean(np.abs((y_test - previsoes) / y_test)) * 100)

    metricas = pd.DataFrame([{
        "ferramenta": "LightAutoML",
        "tipo_problema": "regressão",
        "variavel_alvo": TARGET,
        "metrica_principal": "RMSE",
        "rmse_teste": rmse,
        "mae_teste": mae,
        "r2_teste": r2,
        "mape_teste_percentual": mape,
        "tempo_execucao_segundos": tempo_execucao,
        "time_budget_segundos": TIME_BUDGET_SECONDS,
        "registros_treino": len(train_df),
        "registros_teste": len(test_df),
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
    }])
    metricas.to_csv(OUT_TAB / "lightautoml_metricas.csv", index=False)
    print(f"RMSE: {rmse:.4f} | MAE: {mae:.4f} | R2: {r2:.4f} | MAPE: {mape:.4f}%")

    try:
        importancias = automl.get_feature_scores("fast")
        if importancias is not None and not importancias.empty:
            importancias = importancias.sort_values("Importance", ascending=False).reset_index(drop=True)
            importancias.to_csv(OUT_TAB / "lightautoml_importancia_atributos.csv", index=False)
        else:
            importancias = pd.DataFrame()
    except Exception as exc:
        print(f"Não foi possível extrair a importância dos atributos: {exc}")
        importancias = pd.DataFrame()

    previsoes_df = test_df[["mes_ano", "uf", "regiao", TARGET]].copy()
    previsoes_df["previsao_lightautoml"] = previsoes
    previsoes_df["erro"] = previsoes_df[TARGET] - previsoes_df["previsao_lightautoml"]
    previsoes_df["erro_absoluto"] = previsoes_df["erro"].abs()
    previsoes_df = previsoes_df.sort_values("erro_absoluto", ascending=False)
    previsoes_df.to_csv(OUT_TAB / "lightautoml_previsoes_teste.csv", index=False)

    analise_regiao = previsoes_df.groupby("regiao").agg(
        mae=("erro_absoluto", "mean"),
        rmse=("erro", lambda x: float(np.sqrt((x**2).mean()))),
        erro_medio=("erro", "mean"),
        mape=("erro_absoluto", lambda x: float(
            (x / previsoes_df.loc[x.index, TARGET]).mean() * 100
        )),
    ).reset_index()
    analise_regiao.to_csv(OUT_TAB / "lightautoml_analise_erros_regiao.csv", index=False)

    erros_abs = previsoes_df["erro_absoluto"]
    resumo_erros = pd.DataFrame([{
        "mediana_erro_absoluto": float(erros_abs.median()),
        "percentil_75": float(np.percentile(erros_abs, 75)),
        "percentil_90": float(np.percentile(erros_abs, 90)),
        "percentil_95": float(np.percentile(erros_abs, 95)),
        "max_erro_absoluto": float(erros_abs.max()),
        "desvio_padrao_erro_assinado": float(previsoes_df["erro"].std()),
        "erro_medio_assinado": float(previsoes_df["erro"].mean()),
    }])
    resumo_erros.to_csv(OUT_TAB / "lightautoml_resumo_erros.csv", index=False)

    gerar_figuras(y_test, previsoes, importancias, previsoes_df)

    print("Experimento LightAutoML concluído.")
    print("Arquivos salvos em outputs/tables/ e outputs/figures/")


def carregar_dataset() -> pd.DataFrame:
    dados = pd.read_csv(DATASET_PATH, parse_dates=["mes_ano"])
    if dados.empty:
        raise ValueError("Dataset vazio.")
    return dados


def dividir_treino_teste(dados: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_idx, test_idx = train_test_split(
        dados.index,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=dados["regiao"],
    )
    return dados.loc[train_idx].copy(), dados.loc[test_idx].copy()


def gerar_figuras(
    y_test: np.ndarray,
    previsoes: np.ndarray,
    importancias: pd.DataFrame,
    previsoes_df: pd.DataFrame,
) -> None:
    sns.set_theme(style="whitegrid", context="notebook")

    plt.figure(figsize=(7, 6))
    sns.scatterplot(x=y_test, y=previsoes, color="#1a5c2a", s=45, alpha=0.75)
    minimo = float(min(y_test.min(), previsoes.min()))
    maximo = float(max(y_test.max(), previsoes.max()))
    plt.plot([minimo, maximo], [minimo, maximo], color="#b05f00", linewidth=1.5)
    plt.title("LightAutoML: valores reais e previstos")
    plt.xlabel("Preço real da gasolina C (R$/litro)")
    plt.ylabel("Preço previsto da gasolina C (R$/litro)")
    plt.savefig(OUT_FIG / "lightautoml_real_vs_previsto.png", dpi=140, bbox_inches="tight")
    plt.close()

    if not importancias.empty and "Importance" in importancias.columns:
        col_feat = "Feature" if "Feature" in importancias.columns else importancias.columns[0]
        top = importancias.head(12).sort_values("Importance")
        plt.figure(figsize=(9, 6))
        sns.barplot(data=top, x="Importance", y=col_feat, color="#4a9e6b")
        plt.title("LightAutoML: principais atributos")
        plt.xlabel("Importância")
        plt.ylabel("Atributo")
        plt.savefig(OUT_FIG / "lightautoml_importancia_atributos.png", dpi=140, bbox_inches="tight")
        plt.close()

    erros_abs = previsoes_df["erro_absoluto"]
    plt.figure(figsize=(8, 5))
    sns.histplot(erros_abs, bins=30, color="#1a5c2a", kde=True)
    plt.title("LightAutoML: distribuição dos erros absolutos")
    plt.xlabel("Erro absoluto (R$/litro)")
    plt.ylabel("Frequência")
    plt.savefig(OUT_FIG / "lightautoml_hist_erro_absoluto.png", dpi=140, bbox_inches="tight")
    plt.close()

    regiao_df = previsoes_df.groupby("regiao")["erro_absoluto"].mean().reset_index()
    regiao_df.columns = ["regiao", "mae"]
    plt.figure(figsize=(8, 5))
    sns.barplot(data=regiao_df.sort_values("mae", ascending=False), x="mae", y="regiao", color="#4a9e6b")
    plt.title("LightAutoML: MAE por região")
    plt.xlabel("MAE (R$/litro)")
    plt.ylabel("Região")
    plt.savefig(OUT_FIG / "lightautoml_mae_por_regiao.png", dpi=140, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    main()
