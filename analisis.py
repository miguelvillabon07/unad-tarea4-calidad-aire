"""Recuperación reproducible de la metodología de Tarea 3, sin cambiar el CSV."""
from pathlib import Path
from decimal import Decimal, InvalidOperation
import hashlib
import unicodedata
import pandas as pd
from scipy import stats

HUELLA = "4f58cf846a3575efb409af08a1b6b20d6e47ab4777b2c6915e28450899138606"

def firma(serie):
    return serie.fillna("").str.strip().str.upper().map(
        lambda t: "".join(c for c in unicodedata.normalize("NFKD", t)
                          if not unicodedata.combining(c)))

def decimal_texto(texto):
    try:
        numero = Decimal(texto)
        if numero.is_finite():
            return format(numero.normalize(), "f")
    except InvalidOperation:
        pass
    return texto

def cargar_datos(ruta=None):
    ruta = Path(ruta) if ruta else Path(__file__).with_name("DatasetA_IDEAM_2026-10-01.csv")
    if hashlib.sha256(ruta.read_bytes()).hexdigest() != HUELLA:
        raise ValueError("El CSV no corresponde a la copia conservada de Tarea 3.")
    original = pd.read_csv(ruta)
    claves = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    for campo in ["Representatividad Temporal", "Código del Municipio", "Tipo de Estación"]:
        claves[campo] = claves[campo].replace(["", "N/A", "NA"], "")
    for campo in ["Representatividad Temporal", "Porcentaje excedencias limite actual", "Código del Municipio"]:
        claves[campo] = claves[campo].map(decimal_texto)
    analitica = original.loc[~claves.duplicated()].copy()
    particulas = analitica.loc[analitica["Variable"].isin(["PM10", "PM2.5"])
        & analitica["Unidades"].eq("ugm3")
        & analitica["Tiempo de exposición (horas)"].eq(24)].copy()
    particulas["departamento"] = firma(particulas["Nombre del Departamento"])
    particulas["sitio"] = (particulas["Código del Departamento"].astype(str) + "|"
        + firma(particulas["Nombre del Municipio"]) + "|"
        + firma(particulas["Autoridad Ambiental"]) + "|"
        + firma(particulas["Estación"]) + "|"
        + particulas["Latitud"].round(4).astype(str) + "|"
        + particulas["Longitud"].round(4).astype(str))
    if particulas.duplicated(["sitio", "Año", "Variable"]).any():
        raise ValueError("Hay claves repetidas: revisar antes de emparejar.")
    base = particulas.loc[particulas["Representatividad Temporal"].between(75, 100)
        & particulas["No. de datos"].gt(0)].copy()
    traza = {"Original": len(original), "A. Copia analítica": len(analitica),
             "B. Partículas de 24 horas": len(particulas), "B. Con cobertura": len(base),
             "C. Año 2024": int(base["Año"].eq(2024).sum())}
    return base, traza

def filtrar(base, departamento, periodo):
    mascara = base["Año"].between(*periodo)
    if departamento != "Todos":
        mascara &= base["departamento"].eq(departamento)
    return base.loc[mascara].copy()

def pares(base, anio=2024):
    datos = base.loc[base["Año"].eq(anio)]
    tabla = datos.pivot(index="sitio", columns="Variable", values="Promedio")
    return tabla.reindex(columns=["PM10", "PM2.5"]).dropna()

def panel(base, variable, inicio=2011, fin=2024):
    datos = base.loc[base["Variable"].eq(variable) & base["Año"].between(inicio, fin)]
    presencia = datos.groupby("sitio")["Año"].nunique()
    sitios = presencia.index[presencia.eq(fin-inicio+1)]
    return datos.loc[datos["sitio"].isin(sitios)].copy()

def welch(base):
    datos = base.loc[base["Año"].eq(2024) & base["Variable"].eq("PM2.5")]
    a = datos.loc[datos["departamento"].eq("ANTIOQUIA"), "Promedio"]
    b = datos.loc[datos["departamento"].eq("CUNDINAMARCA"), "Promedio"]
    prueba = stats.ttest_ind(a, b, equal_var=False, alternative="two-sided")
    ic = prueba.confidence_interval()
    return {"n_Antioquia": len(a), "n_Cundinamarca": len(b),
            "media_Antioquia": float(a.mean()), "media_Cundinamarca": float(b.mean()),
            "diferencia": float(a.mean()-b.mean()), "t": float(prueba.statistic),
            "gl": float(prueba.df), "p": float(prueba.pvalue),
            "IC95_inferior": float(ic.low), "IC95_superior": float(ic.high)}
