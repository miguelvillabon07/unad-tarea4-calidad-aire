# Calidad del aire en Colombia | Dashboard IDEAM

Proyecto académico de la **Tarea 4 de Programación para el Análisis de Datos (UNAD)**. Preparé un dashboard interactivo para consultar los promedios anuales de PM10 y PM2.5 registrados en diferentes estaciones de monitoreo de Colombia.

El objetivo es presentar los resultados del análisis exploratorio de forma sencilla: observar cuántos registros hay, comparar concentraciones, identificar diferencias entre estaciones y explicar los principales hallazgos. **Los datos corresponden a los sitios disponibles en la fuente y no representan automáticamente a todo el país.**

## Dashboard

**[Ver la aplicación en Streamlit](https://unad-t4-miguel-villabon-calidad-aire.streamlit.app/)**

![Vista del dashboard de calidad del aire](imagenes/dashboard.jpg)

## ¿Qué se puede consultar?

- **Exploración:** cantidad de registros, media y desviación estándar del contaminante seleccionado.
- **Visualizaciones:** registros por departamento, distribución de concentraciones, proporción de PM10 y PM2.5 y comparación entre ambos contaminantes en un mismo sitio.
- **Validación estadística:** comparación de PM2.5 entre estaciones de Antioquia y Cundinamarca para 2024 mediante la prueba t de Welch.
- **Hallazgos:** explicación de los patrones observados, sus límites y las recomendaciones derivadas del análisis.

Los filtros permiten seleccionar departamento, periodo y contaminante. La validación estadística y el resumen de hallazgos usan sus propios conjuntos de referencia, por lo que no cambian al mover los filtros.

## Datos y preparación

Utilicé el conjunto **Calidad del Aire en Colombia, Promedio Anual**, publicado por el IDEAM en Datos Abiertos Colombia. El archivo `DatasetA_IDEAM_2026-10-01.csv` es la copia de trabajo descargada el 1 de octubre de 2026 y abarca registros de 2011 a 2024.

Para mantener el mismo criterio del análisis previo:

1. Conservo el archivo original, con **29.683 filas y 28 columnas**.
2. Identifico registros equivalentes usando todas las columnas. La base analítica contiene **15.745 filas**.
3. Trabajo con PM10 y PM2.5 en `ugm3`, exposición de referencia de 24 horas, representatividad temporal entre 75 % y 100 % y un número de datos positivo.
4. Después de aplicar esos filtros quedan **1.665 registros anuales**.

El procesamiento está en `analisis.py`. Los valores atípicos se mantienen: un dato extremo no se elimina sin comprobar primero que sea un error. Como se trata de promedios anuales, no es posible reconstruir episodios diarios a partir de este archivo.

## Principales resultados

- **2024:** 217 registros seleccionados; 116 de PM10 y 101 de PM2.5.
- **Relación entre contaminantes:** en 74 sitios con ambos datos disponibles en 2024, la correlación de Pearson es aproximadamente **0,818**. Indica asociación, no causalidad.
- **Comparación por departamento:** para PM2.5 en 2024, la media de los sitios observados fue de **18,053 µg/m³** en Antioquia (24 registros) y **12,844 µg/m³** en Cundinamarca (22 registros). La prueba de Welch obtuvo un valor p aproximado de **0,0000647**, sujeto a los supuestos de la prueba.
- **Evolución de PM10:** en cinco sitios con datos continuos, el promedio pasó de **52,90 µg/m³ en 2011** a **30,35 µg/m³ en 2024**, con variaciones entre esos años. No es una tendencia nacional.
- **Valores atípicos:** en el subconjunto de 2024 se identificaron cinco de PM10 y tres de PM2.5 mediante la regla del rango intercuartílico (IQR).

Estos resultados describen las estaciones incluidas en el análisis. No deben interpretarse como promedios representativos de departamentos o como evidencia de causas específicas.

## Ejecutar el proyecto

Se recomienda **Python 3.12**.

```bash
git clone https://github.com/miguelvillabon07/unad-tarea4-calidad-aire.git
cd unad-tarea4-calidad-aire
python -m venv .venv
```

Activa el entorno virtual:

- Windows (PowerShell): `\.venv\Scripts\Activate.ps1`
- Linux/macOS: `source .venv/bin/activate`

Después instala las dependencias e inicia la aplicación:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La aplicación se abre normalmente en `http://localhost:8501`.

## Archivos principales

| Archivo | Contenido |
| --- | --- |
| `app.py` | Interfaz, filtros, gráficos y presentación de resultados |
| `analisis.py` | Lectura, limpieza, filtros y cálculos estadísticos |
| `DatasetA_IDEAM_2026-10-01.csv` | Copia de los datos utilizados |
| `requirements.txt` | Bibliotecas necesarias |
| `imagenes/` | Capturas de la aplicación |
| `.streamlit/config.toml` | Configuración visual del dashboard |

Para comprobar que se usa la misma copia de los datos, `analisis.py` verifica su huella SHA-256 al cargar el CSV.

## Fuente de datos

Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM). *Calidad del Aire en Colombia, Promedio Anual*. [Datos Abiertos Colombia](https://www.datos.gov.co/d/kekd-7v7h).

## Autor

**Miguel Angel Villabon Romero**  
Grupo 47 · Programación para el Análisis de Datos (203008069)  
Especialización en Ciencia de Datos y Analítica  
Universidad Nacional Abierta y a Distancia (UNAD) · Noviembre de 2026
