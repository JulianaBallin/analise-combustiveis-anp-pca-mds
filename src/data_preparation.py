from __future__ import annotations

from pathlib import Path
import unicodedata

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


PRECO_URL = (
    "https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/"
    "precos-revenda-e-de-distribuicao-combustiveis/shlp/mensal/"
    "mensal-estados-desde-jan2013.xlsx"
)
VENDAS_URL = (
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/"
    "vdpb/vendas-derivados-petroleo-e-etanol/vendas-combustiveis-m3-1990-2025.csv"
)

MESES = {
    "JAN": 1,
    "FEV": 2,
    "MAR": 3,
    "ABR": 4,
    "MAI": 5,
    "JUN": 6,
    "JUL": 7,
    "AGO": 8,
    "SET": 9,
    "OUT": 10,
    "NOV": 11,
    "DEZ": 12,
}

UF_NOMES = {
    "ACRE": "AC",
    "ALAGOAS": "AL",
    "AMAPA": "AP",
    "AMAZONAS": "AM",
    "BAHIA": "BA",
    "CEARA": "CE",
    "DISTRITO FEDERAL": "DF",
    "ESPIRITO SANTO": "ES",
    "GOIAS": "GO",
    "MARANHAO": "MA",
    "MATO GROSSO": "MT",
    "MATO GROSSO DO SUL": "MS",
    "MINAS GERAIS": "MG",
    "PARA": "PA",
    "PARAIBA": "PB",
    "PARANA": "PR",
    "PERNAMBUCO": "PE",
    "PIAUI": "PI",
    "RIO DE JANEIRO": "RJ",
    "RIO GRANDE DO NORTE": "RN",
    "RIO GRANDE DO SUL": "RS",
    "RONDONIA": "RO",
    "RORAIMA": "RR",
    "SANTA CATARINA": "SC",
    "SAO PAULO": "SP",
    "SERGIPE": "SE",
    "TOCANTINS": "TO",
}

FEATURES_NUMERICAS = [
    "preco_medio_gasolina_c",
    "volume_gasolina_c_m3",
    "volume_etanol_hidratado_m3",
    "variacao_preco_gasolina_c",
    "variacao_volume_gasolina_c",
    "participacao_etanol",
    "razao_etanol_gasolina",
    "preco_relativo_etanol_gasolina",
]


def remover_acentos(texto: object) -> str:
    texto = "" if pd.isna(texto) else str(texto)
    normalizado = unicodedata.normalize("NFKD", texto.strip().upper())
    return "".join(c for c in normalizado if not unicodedata.combining(c))


def preparar_dados(periodo_inicio: int = 2021, periodo_fim: int = 2025) -> pd.DataFrame:
    precos = carregar_precos()
    vendas = carregar_vendas()

    dados = precos.merge(vendas, on=["mes_ano", "uf_nome", "uf", "regiao"], how="inner")
    dados = dados.sort_values(["uf", "mes_ano"]).reset_index(drop=True)
    dados["volume_total_analisado_m3"] = (
        dados["volume_gasolina_c_m3"] + dados["volume_etanol_hidratado_m3"]
    )
    dados["participacao_etanol"] = (
        dados["volume_etanol_hidratado_m3"] / dados["volume_total_analisado_m3"]
    )
    dados["razao_etanol_gasolina"] = (
        dados["volume_etanol_hidratado_m3"] / dados["volume_gasolina_c_m3"]
    )
    dados["preco_relativo_etanol_gasolina"] = (
        dados["preco_medio_etanol_hidratado"] / dados["preco_medio_gasolina_c"]
    )
    dados["variacao_preco_gasolina_c"] = dados.groupby("uf")[
        "preco_medio_gasolina_c"
    ].pct_change()
    dados["variacao_volume_gasolina_c"] = dados.groupby("uf")[
        "volume_gasolina_c_m3"
    ].pct_change()
    dados["ano"] = dados["mes_ano"].dt.year
    dados["mes"] = dados["mes_ano"].dt.month

    dados = dados[(dados["ano"] >= periodo_inicio) & (dados["ano"] <= periodo_fim)]
    dados = dados.replace([np.inf, -np.inf], np.nan).dropna(subset=FEATURES_NUMERICAS)
    return dados.reset_index(drop=True)


def carregar_precos() -> pd.DataFrame:
    precos = pd.read_excel(PRECO_URL, header=16)
    precos.columns = [remover_acentos(col).lower().replace(" ", "_") for col in precos.columns]
    precos = precos.rename(
        columns={
            "mes": "mes_ano",
            "estado": "uf_nome",
            "preco_medio_revenda": "preco_medio_revenda",
        }
    )
    precos["produto_norm"] = precos["produto"].map(remover_acentos)
    precos = precos[
        precos["produto_norm"].isin(["GASOLINA COMUM", "GASOLINA C", "ETANOL HIDRATADO"])
    ].copy()
    precos["produto_final"] = np.where(
        precos["produto_norm"].str.contains("ETANOL"), "etanol_hidratado", "gasolina_c"
    )
    precos["uf_nome"] = precos["uf_nome"].map(remover_acentos)
    precos["uf"] = precos["uf_nome"].map(UF_NOMES)
    precos["regiao"] = precos["regiao"].map(remover_acentos)
    precos = precos.dropna(subset=["uf"])
    precos = precos.pivot_table(
        index=["mes_ano", "uf_nome", "uf", "regiao"],
        columns="produto_final",
        values="preco_medio_revenda",
        aggfunc="mean",
    ).reset_index()
    precos = precos.rename(
        columns={
            "gasolina_c": "preco_medio_gasolina_c",
            "etanol_hidratado": "preco_medio_etanol_hidratado",
        }
    )
    return precos


def carregar_vendas() -> pd.DataFrame:
    vendas = pd.read_csv(VENDAS_URL, sep=";", encoding="utf-8")
    vendas.columns = [remover_acentos(col).lower().replace(" ", "_") for col in vendas.columns]
    vendas["produto_norm"] = vendas["produto"].map(remover_acentos)
    vendas = vendas[
        vendas["produto_norm"].isin(["GASOLINA C", "ETANOL HIDRATADO"])
    ].copy()
    vendas["produto_final"] = np.where(
        vendas["produto_norm"].str.contains("ETANOL"), "etanol_hidratado", "gasolina_c"
    )
    vendas["uf_nome"] = vendas["unidade_da_federacao"].map(remover_acentos)
    vendas["uf"] = vendas["uf_nome"].map(UF_NOMES)
    vendas["regiao"] = vendas["grande_regiao"].map(remover_acentos).str.replace("REGIAO ", "")
    vendas["mes_num"] = vendas["mes"].map(MESES)
    vendas["mes_ano"] = pd.to_datetime(
        dict(year=vendas["ano"], month=vendas["mes_num"], day=1)
    )
    vendas["vendas"] = (
        vendas["vendas"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".")
    ).astype(float)
    vendas = vendas.dropna(subset=["uf", "mes_num"])
    vendas = vendas.pivot_table(
        index=["mes_ano", "uf_nome", "uf", "regiao"],
        columns="produto_final",
        values="vendas",
        aggfunc="sum",
    ).reset_index()
    vendas = vendas.rename(
        columns={
            "gasolina_c": "volume_gasolina_c_m3",
            "etanol_hidratado": "volume_etanol_hidratado_m3",
        }
    )
    return vendas


def padronizar_features(dados: pd.DataFrame) -> tuple[pd.DataFrame, StandardScaler]:
    scaler = StandardScaler()
    matriz = scaler.fit_transform(dados[FEATURES_NUMERICAS])
    dados_padronizados = pd.DataFrame(matriz, columns=FEATURES_NUMERICAS, index=dados.index)
    return dados_padronizados, scaler
