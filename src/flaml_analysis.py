from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from flaml import AutoML
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "processed" / "dataset_anp_pca_mds_2021_2025.csv"
OUT_FIG = ROOT / "outputs" / "figures"
OUT_TAB = ROOT / "outputs" / "tables"

TARGET = "preco_medio_gasolina_c"
RANDOM_STATE = 42
TEST_SIZE = 0.2
TIME_BUDGET_SECONDS = 60
ESTIMATOR_LIST = ["lgbm", "rf", "extra_tree"]

REMOVER_DA_MODELAGEM = [
    TARGET,
    "mes_ano",
    "uf_nome",
    "variacao_preco_gasolina_c",
    "preco_relativo_etanol_gasolina",
]

CATEGORICAS = ["uf", "regiao"]


def main() -> None:
    OUT_FIG.mkdir(parents=True, exist_ok=True)
    OUT_TAB.mkdir(parents=True, exist_ok=True)

    dados = carregar_dataset()
    X, y, features_originais = preparar_matriz_modelagem(dados)
    train_idx, test_idx = dividir_treino_teste(dados)

    X_train = X.loc[train_idx]
    X_test = X.loc[test_idx]
    y_train = y.loc[train_idx]
    y_test = y.loc[test_idx]

    automl = AutoML()
    inicio = time.perf_counter()
    automl.fit(
        X_train=X_train,
        y_train=y_train,
        task="regression",
        metric="rmse",
        time_budget=TIME_BUDGET_SECONDS,
        estimator_list=ESTIMATOR_LIST,
        seed=RANDOM_STATE,
        n_jobs=-1,
        verbose=0,
    )
    tempo_execucao = time.perf_counter() - inicio

    previsoes = automl.predict(X_test)
    metricas = calcular_metricas(
        y_test=y_test,
        previsoes=previsoes,
        automl=automl,
        tempo_execucao=tempo_execucao,
        treino_n=len(X_train),
        teste_n=len(X_test),
        atributos_n=X.shape[1],
        features_originais=features_originais,
    )

    leaderboard = montar_leaderboard(automl)
    importancia = extrair_importancia_atributos(automl, X.columns)
    previsoes_df = montar_previsoes(dados, test_idx, previsoes)
    baseline = calcular_baselines(dados, train_idx, test_idx, previsoes)
    resumo_erros = resumir_erros(previsoes_df)
    erros_regiao = analisar_erros_por_regiao(previsoes_df)
    top_importancias = importancia.head(12).copy()

    salvar_resultados(
        metricas,
        leaderboard,
        importancia,
        previsoes_df,
        automl,
        baseline,
        resumo_erros,
        erros_regiao,
        top_importancias,
    )
    gerar_figuras(y_test, previsoes, importancia, baseline, previsoes_df)

    linha = metricas.iloc[0]
    print("Experimento FLAML concluído.")
    print(f"Melhor estimador: {linha['melhor_estimador']}")
    print(f"RMSE teste: {linha['rmse_teste']:.4f}")
    print(f"MAE teste: {linha['mae_teste']:.4f}")
    print(f"R2 teste: {linha['r2_teste']:.4f}")
    print(f"Tempo de execução: {linha['tempo_execucao_segundos']:.2f} segundos")


def carregar_dataset() -> pd.DataFrame:
    dados = pd.read_csv(DATASET_PATH, parse_dates=["mes_ano"])
    if dados.empty:
        raise ValueError("O dataset processado está vazio.")
    return dados


def preparar_matriz_modelagem(dados: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    features_originais = [col for col in dados.columns if col not in REMOVER_DA_MODELAGEM]
    X_base = dados[features_originais].copy()
    X = pd.get_dummies(X_base, columns=CATEGORICAS, drop_first=False, dtype=float)
    y = dados[TARGET].astype(float)
    return X, y, features_originais


def dividir_treino_teste(dados: pd.DataFrame) -> tuple[pd.Index, pd.Index]:
    train_idx, test_idx = train_test_split(
        dados.index,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=dados["regiao"],
    )
    return pd.Index(train_idx), pd.Index(test_idx)


def calcular_metricas(
    y_test: pd.Series,
    previsoes,
    automl: AutoML,
    tempo_execucao: float,
    treino_n: int,
    teste_n: int,
    atributos_n: int,
    features_originais: list[str],
) -> pd.DataFrame:
    rmse = mean_squared_error(y_test, previsoes) ** 0.5
    mae = mean_absolute_error(y_test, previsoes)
    r2 = r2_score(y_test, previsoes)
    mape = (abs((y_test - previsoes) / y_test).mean()) * 100

    return pd.DataFrame(
        [
            {
                "ferramenta": "FLAML",
                "tipo_problema": "regressão",
                "variavel_alvo": TARGET,
                "metrica_principal": "RMSE",
                "rmse_teste": rmse,
                "mae_teste": mae,
                "r2_teste": r2,
                "mape_teste_percentual": mape,
                "melhor_estimador": automl.best_estimator,
                "tempo_execucao_segundos": tempo_execucao,
                "time_budget_segundos": TIME_BUDGET_SECONDS,
                "registros_treino": treino_n,
                "registros_teste": teste_n,
                "atributos_originais_modelagem": len(features_originais),
                "atributos_apos_one_hot": atributos_n,
                "random_state": RANDOM_STATE,
                "test_size": TEST_SIZE,
                "estimadores_testados": ", ".join(ESTIMATOR_LIST),
                "colunas_removidas": ", ".join(REMOVER_DA_MODELAGEM),
            }
        ]
    )


def montar_leaderboard(automl: AutoML) -> pd.DataFrame:
    perdas = getattr(automl, "best_loss_per_estimator", {})
    configs = getattr(automl, "best_config_per_estimator", {})
    linhas = []

    for estimador in ESTIMATOR_LIST:
        perda = perdas.get(estimador)
        config = configs.get(estimador)
        linhas.append(
            {
                "estimador": estimador,
                "melhor_loss_validacao_rmse": float(perda) if perda is not None else None,
                "melhor_configuracao": serializar_json(config),
                "selecionado_como_melhor": estimador == automl.best_estimator,
            }
        )

    return pd.DataFrame(linhas).sort_values("melhor_loss_validacao_rmse", na_position="last")


def extrair_importancia_atributos(automl: AutoML, colunas: pd.Index) -> pd.DataFrame:
    estimador = automl.model.estimator
    if not hasattr(estimador, "feature_importances_"):
        return pd.DataFrame(columns=["atributo", "importancia", "importancia_percentual"])

    importancia = pd.Series(estimador.feature_importances_, index=colunas, dtype=float)
    importancia_df = (
        importancia.sort_values(ascending=False)
        .rename_axis("atributo")
        .reset_index(name="importancia")
    )
    soma = importancia_df["importancia"].sum()
    importancia_df["importancia_percentual"] = (
        importancia_df["importancia"] / soma * 100 if soma else 0
    )
    return importancia_df


def montar_previsoes(dados: pd.DataFrame, test_idx: pd.Index, previsoes) -> pd.DataFrame:
    resultado = dados.loc[test_idx, ["mes_ano", "uf", "regiao", TARGET]].copy()
    resultado["previsao_flaml"] = previsoes
    resultado["erro"] = resultado[TARGET] - resultado["previsao_flaml"]
    resultado["erro_absoluto"] = resultado["erro"].abs()
    return resultado.sort_values("erro_absoluto", ascending=False)


def calcular_baselines(
    dados: pd.DataFrame,
    train_idx: pd.Index,
    test_idx: pd.Index,
    previsoes,
) -> pd.DataFrame:
    treino = dados.loc[train_idx]
    teste = dados.loc[test_idx]
    y_test = teste[TARGET].astype(float)

    media_global = float(treino[TARGET].mean())
    medias_regiao = treino.groupby("regiao")[TARGET].mean()
    medias_uf = treino.groupby("uf")[TARGET].mean()

    predicoes = {
        "FLAML (lgbm)": pd.Series(previsoes, index=test_idx, dtype=float),
        "Média do treino": pd.Series(media_global, index=test_idx, dtype=float),
        "Média por região": teste["regiao"].map(medias_regiao).fillna(media_global).astype(float),
        "Média por UF": teste["uf"].map(medias_uf).fillna(media_global).astype(float),
    }

    rmse_referencia = mean_squared_error(y_test, predicoes["Média do treino"]) ** 0.5
    linhas = []
    for nome, pred in predicoes.items():
        rmse = mean_squared_error(y_test, pred) ** 0.5
        linhas.append(
            {
                "modelo": nome,
                "rmse": rmse,
                "mae": mean_absolute_error(y_test, pred),
                "r2": r2_score(y_test, pred),
                "mape_percentual": (abs((y_test - pred) / y_test).mean()) * 100,
                "melhora_rmse_vs_media_treino_percentual": (
                    (1 - rmse / rmse_referencia) * 100 if nome == "FLAML (lgbm)" else None
                ),
            }
        )

    return pd.DataFrame(linhas)


def resumir_erros(previsoes_df: pd.DataFrame) -> pd.DataFrame:
    erros_abs = previsoes_df["erro_absoluto"]
    return pd.DataFrame(
        [
            {
                "mediana_erro_absoluto": float(erros_abs.median()),
                "percentil_75": float(erros_abs.quantile(0.75)),
                "percentil_90": float(erros_abs.quantile(0.90)),
                "percentil_95": float(erros_abs.quantile(0.95)),
                "max_erro_absoluto": float(erros_abs.max()),
                "desvio_padrao_erro_assinado": float(previsoes_df["erro"].std()),
                "erro_medio_assinado": float(previsoes_df["erro"].mean()),
            }
        ]
    )


def analisar_erros_por_regiao(previsoes_df: pd.DataFrame) -> pd.DataFrame:
    return (
        previsoes_df.groupby("regiao")
        .agg(
            mae=("erro_absoluto", "mean"),
            rmse=("erro", lambda x: float((x.pow(2).mean()) ** 0.5)),
            erro_medio=("erro", "mean"),
            mape=(
                "erro_absoluto",
                lambda x: float((x / previsoes_df.loc[x.index, TARGET]).mean() * 100),
            ),
        )
        .reset_index()
        .sort_values("mae")
    )


def salvar_resultados(
    metricas: pd.DataFrame,
    leaderboard: pd.DataFrame,
    importancia: pd.DataFrame,
    previsoes: pd.DataFrame,
    automl: AutoML,
    baseline: pd.DataFrame,
    resumo_erros: pd.DataFrame,
    erros_regiao: pd.DataFrame,
    top_importancias: pd.DataFrame,
) -> None:
    metricas.to_csv(OUT_TAB / "flaml_metricas.csv", index=False)
    leaderboard.to_csv(OUT_TAB / "flaml_leaderboard.csv", index=False)
    importancia.to_csv(OUT_TAB / "flaml_importancia_atributos.csv", index=False)
    previsoes.to_csv(OUT_TAB / "flaml_previsoes_teste.csv", index=False)
    baseline.to_csv(OUT_TAB / "flaml_baseline_comparacao.csv", index=False)
    resumo_erros.to_csv(OUT_TAB / "flaml_resumo_erros.csv", index=False)
    erros_regiao.to_csv(OUT_TAB / "flaml_analise_erros_regiao.csv", index=False)
    top_importancias.to_csv(OUT_TAB / "flaml_top_importancias.csv", index=False)

    configuracao = {
        "best_estimator": automl.best_estimator,
        "best_config": converter_json(automl.best_config),
        "best_loss": float(automl.best_loss),
        "estimator_list": ESTIMATOR_LIST,
        "time_budget_seconds": TIME_BUDGET_SECONDS,
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "target": TARGET,
        "removed_columns": REMOVER_DA_MODELAGEM,
    }
    (OUT_TAB / "flaml_configuracao.json").write_text(
        json.dumps(configuracao, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def gerar_figuras(
    y_test: pd.Series,
    previsoes,
    importancia: pd.DataFrame,
    baseline: pd.DataFrame,
    previsoes_df: pd.DataFrame,
) -> None:
    sns.set_theme(style="whitegrid", context="notebook")

    plt.figure(figsize=(7, 6))
    sns.scatterplot(x=y_test, y=previsoes, color="#1a5c2a", s=45, alpha=0.75)
    minimo = min(float(y_test.min()), float(pd.Series(previsoes).min()))
    maximo = max(float(y_test.max()), float(pd.Series(previsoes).max()))
    plt.plot([minimo, maximo], [minimo, maximo], color="#b05f00", linewidth=1.5)
    plt.title("FLAML: valores reais e previstos")
    plt.xlabel("Preço real da gasolina C (R$/litro)")
    plt.ylabel("Preço previsto da gasolina C (R$/litro)")
    plt.savefig(OUT_FIG / "flaml_real_vs_previsto.png", dpi=140, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=baseline.sort_values("rmse"),
        x="rmse",
        y="modelo",
        color="#4a9e6b",
    )
    plt.title("FLAML: comparação de RMSE com baselines")
    plt.xlabel("RMSE (R$/litro)")
    plt.ylabel("Modelo")
    plt.savefig(OUT_FIG / "flaml_baseline_rmse.png", dpi=140, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(previsoes_df["erro_absoluto"], bins=30, color="#1a5c2a", kde=True)
    plt.title("FLAML: distribuição dos erros absolutos")
    plt.xlabel("Erro absoluto (R$/litro)")
    plt.ylabel("Frequência")
    plt.savefig(OUT_FIG / "flaml_hist_erro_absoluto.png", dpi=140, bbox_inches="tight")
    plt.close()

    regiao_df = previsoes_df.groupby("regiao")["erro_absoluto"].mean().reset_index()
    regiao_df.columns = ["regiao", "mae"]
    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=regiao_df.sort_values("mae", ascending=False),
        x="mae",
        y="regiao",
        color="#4a9e6b",
    )
    plt.title("FLAML: MAE por região")
    plt.xlabel("MAE (R$/litro)")
    plt.ylabel("Região")
    plt.savefig(OUT_FIG / "flaml_mae_por_regiao.png", dpi=140, bbox_inches="tight")
    plt.close()

    if importancia.empty:
        return

    top_importancia = importancia.head(12).sort_values("importancia")
    plt.figure(figsize=(9, 6))
    sns.barplot(data=top_importancia, x="importancia", y="atributo", color="#4a9e6b")
    plt.title("FLAML: principais atributos do melhor modelo")
    plt.xlabel("Importância")
    plt.ylabel("Atributo")
    plt.savefig(OUT_FIG / "flaml_importancia_atributos.png", dpi=140, bbox_inches="tight")
    plt.close()


def serializar_json(valor: Any) -> str:
    return json.dumps(converter_json(valor), ensure_ascii=False, sort_keys=True)


def converter_json(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {chave: converter_json(item) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [converter_json(item) for item in valor]
    if hasattr(valor, "item"):
        return valor.item()
    return valor


if __name__ == "__main__":
    main()
