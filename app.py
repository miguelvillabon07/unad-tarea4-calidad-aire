"""Dashboard académico: extensión comunicativa del EDA de Tarea 3."""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from analisis import cargar_datos, filtrar, pares, panel, welch

st.set_page_config(page_title="Calidad del aire | IDEAM", page_icon="📊", layout="wide")
sns.set_theme(style="whitegrid", context="notebook")
AZUL = "#277da8"

@st.cache_data(show_spinner="Preparando la copia analítica del IDEAM…")
def datos_cache():
    return cargar_datos()

@st.cache_data(show_spinner=False)
def referencias_cache():
    base, _ = datos_cache()
    referencia = pares(base)
    continuo = panel(base, "PM10")
    return welch(base), referencia, continuo

def mostrar(fig):
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def numero(valor, decimales=2):
    return f"{valor:,.{decimales}f}".replace(",", "_").replace(".", ",").replace("_", ".")

def dispersion(tabla, titulo):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.scatter(tabla["PM10"], tabla["PM2.5"], color=AZUL, alpha=.75)
    ax.set(title=titulo, xlabel="PM10 promedio anual (µg/m³)",
           ylabel="PM2.5 promedio anual (µg/m³)")
    return fig

def main():
    st.title("Calidad del aire en los sitios observados")
    st.markdown("**Dataset A · IDEAM · Promedios anuales de PM10 y PM2.5 · 2011 a 2024**")
    st.write("Exploro disponibilidad, concentraciones y asociaciones entre sitios de medición. "
             "Esta aplicación continúa el análisis de la Tarea 3; la cobertura disponible no representa todo Colombia.")
    try:
        base, traza = datos_cache()
    except (OSError, ValueError) as error:
        st.error(f"No se pudieron preparar los datos: {error}")
        st.stop()
    with st.sidebar:
        st.header("Explorar los registros")
        departamento = st.selectbox("Departamento", ["Todos"] + sorted(base["departamento"].unique()))
        periodo = st.slider("Periodo de años", 2011, 2024, (2024, 2024))
        variable = st.selectbox("Contaminante para métricas, barras y caja", ["PM10", "PM2.5"])
        st.caption("Unidad: µg/m³. Exposición de referencia: 24 horas. Los valores publicados son resúmenes anuales.")
        st.caption("Cobertura temporal entre 75 y 100 %, con conteo de datos positivo. Los atípicos se conservan.")
    filtrados = filtrar(base, departamento, periodo)
    seleccion = filtrados.loc[filtrados["Variable"].eq(variable)]
    st.caption(f"Selección activa: {departamento} · {periodo[0]} a {periodo[1]} · {variable}")
    exploracion, graficos, validacion, hallazgos = st.tabs(["Exploración", "Visualizaciones", "Validación estadística", "Hallazgos"])
    st.caption("Exploración y visualizaciones responden a los filtros. Validación y hallazgos conservan el alcance original.")
    with exploracion:
        st.header("Exploración de datos")
        columnas = st.columns(3)
        columnas[0].metric(f"Registros anuales de {variable}", len(seleccion))
        columnas[1].metric(f"Media de {variable} (µg/m³)", numero(seleccion["Promedio"].mean()) if len(seleccion) else "Sin datos")
        columnas[2].metric("Desviación estándar (µg/m³)", numero(seleccion["Promedio"].std()) if len(seleccion)>1 else "No estimable")
        st.caption("La desviación estándar muestra cuánto se dispersan los valores alrededor de la media; se calcula con el criterio muestral. Cada registro resume un sitio y año. La media da el mismo peso a cada registro; no es un promedio territorial representativo.")
        if seleccion.empty:
            st.info("No hay registros del contaminante para esta selección. Cambia el departamento o el periodo.")
        columnas_tabla = ["Año", "departamento", "Nombre del Municipio", "Estación", "Variable",
                          "Promedio", "Representatividad Temporal", "No. de datos"]
        st.dataframe(seleccion[columnas_tabla], hide_index=True, width="stretch")

    with graficos:
        st.header("Visualizaciones")
        st.caption("Reutilizo las barras, el boxplot, la torta y la dispersión de la Parte 3. Se recalculan con la selección activa.")
        izquierda, derecha = st.columns(2)
        with izquierda:
            st.subheader("1. Disponibilidad por departamento")
            if not seleccion.empty:
                conteos = seleccion["departamento"].value_counts().sort_values()
                fig, ax = plt.subplots(figsize=(8, max(3.5, len(conteos)*.28)))
                barras = ax.barh(conteos.index, conteos.values, color=AZUL)
                ax.bar_label(barras, padding=3)
                ax.set(title=f"Registros anuales de {variable}", xlabel="Cantidad de registros", ylabel="Departamento")
                ax.set_xlim(0, conteos.max()*1.18)
                mostrar(fig)
            else:
                st.info("Sin datos para las barras.")
        with derecha:
            st.subheader("2. Distribución de concentraciones")
            if not seleccion.empty:
                fig, ax = plt.subplots(figsize=(8, 3.5))
                sns.boxplot(data=seleccion, x="Promedio", color="#76b7c5", ax=ax)
                ax.set(title=f"Promedios anuales de {variable}", xlabel="Concentración (µg/m³)")
                mostrar(fig)
                st.caption("La caja reúne la mitad central. Los puntos exteriores merecen revisión; no son errores ni incumplimientos demostrados.")
            else:
                st.info("Sin datos para la caja.")
        izquierda, derecha = st.columns(2)
        with izquierda:
            st.subheader("3. Composición de los registros")
            st.caption("Usa departamento y periodo; incluye ambos contaminantes para comparar cantidades.")
            if not filtrados.empty:
                conteos = filtrados["Variable"].value_counts()
                fig, ax = plt.subplots(figsize=(7, 4.2))
                colores = {"PM10": AZUL, "PM2.5": "#e69f00"}
                ax.pie(conteos, labels=[f"{v} (n={n})" for v,n in conteos.items()], autopct="%.1f%%",
                       colors=[colores[v] for v in conteos.index], startangle=90)
                ax.set_title("Proporción de registros, no de contaminación")
                mostrar(fig)
            else:
                st.info("Sin registros para la composición.")
        with derecha:
            st.subheader("4. Ambos contaminantes en el mismo sitio")
            st.caption("Usa departamento y el último año del periodo seleccionado; no mezcla años al emparejar.")
            emparejados = pares(filtrados, periodo[1])
            if len(emparejados):
                st.caption(f"{len(emparejados)} sitios emparejados · {periodo[1]}")
                puntos = emparejados.rename(columns={v: f"{v} promedio anual (µg/m³)" for v in ["PM10", "PM2.5"]})
                st.scatter_chart(puntos, x="PM10 promedio anual (µg/m³)", y="PM2.5 promedio anual (µg/m³)", color=AZUL)
                if len(emparejados)>2 and emparejados.nunique().gt(1).all():
                    r = emparejados.corr().loc["PM10", "PM2.5"]
                    st.write(f"Correlación de esta selección: {numero(r,6)}. Describe asociación, sin demostrar causalidad.")
                else:
                    st.info("Los pares disponibles no permiten una correlación interpretable.")
            else:
                st.info("No hay sitios con ambos contaminantes en el último año seleccionado.")

    with validacion:
        st.header("Validación estadística")
        st.info("Referencia fija de la Tarea 3: PM2.5 de 2024, Antioquia y Cundinamarca. Esta comparación conserva su alcance y no cambia con los filtros exploratorios.")
        resultado, _, _ = referencias_cache()
        st.dataframe(pd.DataFrame({"Departamento":["Antioquia", "Cundinamarca"],
            "Registros":[resultado["n_Antioquia"],resultado["n_Cundinamarca"]],
            "Media PM2.5 (µg/m³)":[resultado["media_Antioquia"],resultado["media_Cundinamarca"]]}), hide_index=True)
        st.write(f"En los sitios observados de 2024, la media de PM2.5 es mayor en el grupo de Antioquia, con una diferencia de {numero(resultado['diferencia'],3)} µg/m³. La comparación aporta evidencia de una diferencia bajo sus supuestos, sin representar a los departamentos completos.")
        with st.expander("Resultado de la prueba t de Welch y sus supuestos"):
            st.write(f"Prueba bilateral: p = {numero(resultado['p'],10)}; t = {numero(resultado['t'],6)}; grados de libertad = {numero(resultado['gl'],3)}. H0: medias iguales; H1: medias diferentes. Con alpha = 0,05 rechazo H0 bajo los supuestos de la prueba.")
            st.write(f"Intervalo del 95 % para la diferencia: {numero(resultado['IC95_inferior'],3)} a {numero(resultado['IC95_superior'],3)} µg/m³. La prueba permite varianzas distintas, pero no corrige selección de estaciones ni dependencia espacial. El valor p no es la probabilidad de que H0 sea verdadera.")

    with hallazgos:
        st.header("Hallazgos: una lectura para tomar decisiones")
        st.caption("Síntesis fija del EDA original. Las dos figuras siguientes respaldan esta narrativa y conservan sus universos de referencia.")
        _, referencia, continuo = referencias_cache()
        medias = continuo.groupby("Año")["Promedio"].mean()
        r_ref = referencia.corr().loc["PM10", "PM2.5"]
        st.markdown("### 1. ¿Qué analicé?")
        st.write("Analicé los promedios anuales publicados por el IDEAM entre 2011 y 2024 para entender diferencias entre sitios y cambios en el tiempo. "
                 "Me concentré en PM10 y PM2.5, dos medidas de partículas en el aire, con exposición de referencia de 24 horas y cobertura temporal entre 75 y 100 %. "
                 "Los datos resumen cada año; no describen episodios diarios.")
        st.markdown("### 2. ¿Qué encontré?")
        # Texto corregido de T4-C: asociación entre sitios, sin porcentajes ni efectos causales.
        st.write(f"En los {len(referencia)} sitios con ambos contaminantes en 2024, los sitios con mayor PM10 tienden a presentar mayor PM2.5. "
                 f"La correlación es {numero(r_ref,6)}, una medida de asociación que no demuestra que una partícula cause la otra. "
                 "Tampoco permite afirmar que controlar PM10 reduzca automáticamente PM2.5 ni sustituir su medición. "
                 f"En los {continuo['sitio'].nunique()} sitios constantes de PM10, el promedio pasa de {numero(medias.loc[2011])} µg/m³ en 2011 "
                 f"a {numero(medias.loc[2024])} en 2024, con repuntes intermedios.")
        st.markdown("### 3. ¿Qué significa?")
        st.write("Observo comportamientos relacionados y una reducción entre los extremos del panel largo, pero no una mejora continua ni nacional. "
                 "Ese panel incluye cuatro sitios de Bogotá y uno de Cesar. La cobertura cambia entre años y no he comprobado continuidad instrumental o independencia espacial. "
                 "Las diferencias entre los grupos de estaciones tampoco equivalen a promedios representativos de los departamentos.")
        st.markdown("### 4. ¿Qué se recomendaría?")
        st.write("Recomendaría revisar la continuidad y las condiciones de medición de cada sitio antes de ampliar comparaciones. "
                 "También contrastaría los valores altos con los registros de las estaciones y mantendría el monitoreo de ambos contaminantes. "
                 "Para estudiar causas o cambios recientes necesitaría información adicional; estos resultados orientan la revisión, sin justificar por sí solos decisiones sanitarias.")
        izquierda, derecha = st.columns(2)
        with izquierda:
            mostrar(dispersion(referencia, "Figura 1. Sitios con mayores valores tienden a coincidir · 2024"))
            st.caption("Fuente: elaboración a partir del CSV conservado del IDEAM. 74 sitios; mismo año y filtros de cobertura.")
        with derecha:
            fig, ax = plt.subplots(figsize=(8,4.2))
            ax.plot(medias.index, medias, marker="o", color=AZUL)
            ax.set(title="Figura 2. PM10 baja entre extremos, con repuntes",
                   xlabel="Año · cinco sitios constantes", ylabel="Media anual (µg/m³)")
            mostrar(fig)
            st.caption("Fuente: elaboración a partir del IDEAM. Cuatro sitios de Bogotá y uno de Cesar; no es una tendencia nacional.")
        with st.expander("Método y trazabilidad"):
            st.dataframe(pd.Series(traza, name="Registros").rename_axis("Alcance"))
            st.write("Cuento una representación por equivalencia decimal y textual en todas las columnas, según Tarea 3. "
                     "Conservo el CSV original, los nulos no excluidos por los filtros y los atípicos. "
                     "La clave de sitio combina departamento, municipio, autoridad, estación y coordenadas; no verifica por sí sola identidad física.")
            st.markdown("[Fuente oficial IDEAM: Calidad del Aire en Colombia, Promedio Anual](https://www.datos.gov.co/d/kekd-7v7h)")
        st.caption("Miguel Angel Villabon Romero · Grupo 47 · UNAD · Programación para el análisis de datos, 203008069 · Noviembre de 2026. Desarrollo asistido por Codex y revisión con Gemini; trazabilidad en el notebook.")

if __name__ == "__main__":
    main()
