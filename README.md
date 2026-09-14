# Carga alostática en personal de bomberos

Dashboard de portafolio en ciencia de datos construido sobre datos de un proyecto de
investigación doctoral: biomarcadores sanguíneos, variabilidad de frecuencia cardiaca (HRV) y
resiliencia percibida (BRS) en una cohorte de bomberos, medidos en dos momentos — **Fase 1** y
**Fase 2**.

**Dashboard interactivo (GitHub Pages):** https://marcarmona1318.github.io/bomberos-carga-alostatica-dashboard/

## Qué hay aquí

| Carpeta | Contenido |
|---|---|
| [`docs/`](docs/) | Dashboard HTML interactivo (autocontenido, publicado vía GitHub Pages) |
| [`notebook/`](notebook/) | Análisis exploratorio en Jupyter (`analisis_carga_alostatica.ipynb`), con salidas ya ejecutadas |
| [`quarto/`](quarto/) | La misma narrativa del notebook en formato Quarto (`index.qmd`) — requiere `quarto render` |
| [`data/`](data/) | Datos anonimizados: `cohorte_anonimizada.csv` (valores crudos) y `dashboard_data.json` (el que consume el dashboard) |
| [`scripts/`](scripts/) | `prepare_data.py` (fusiona y anonimiza los 4 archivos fuente) y `build_notebook.py` (genera el `.ipynb` vía `nbformat`) |

## Los datos

Fuente: 4 archivos normalizados (min-max) de un proyecto de tesis doctoral sobre carga
alostática:

- `biomarcadores_normalizados_minmax.csv` — 15 variables de signos vitales y bioquímica sanguínea
- `HRV_sup_normalizado_minmax.csv` / `HRV_st_normalizado_minmax.csv` — 9 variables de HRV, posición supina y de pie
- `Resiliencia_BRS_normalizado_minmax.csv` — puntaje promedio de la Brief Resilience Scale

Cohorte: **n = 26**, evaluados en Fase 1 y Fase 2. Los identificadores originales fueron
reemplazados por códigos anónimos `P01`–`P26` antes de que ningún dato saliera de la carpeta de
trabajo — ningún nombre se incluye en este repositorio.

## Cómo ver el dashboard

**Opción 1 — GitHub Pages:** https://marcarmona1318.github.io/bomberos-carga-alostatica-dashboard/

**Opción 2 — local:**

```bash
cd docs && python3 -m http.server 8000
```

y abre `http://localhost:8000`.

## Cómo reproducir el análisis

```bash
# 1. Regenerar los datos anonimizados desde las fuentes normalizadas
python3 scripts/prepare_data.py

# 2. Regenerar y ejecutar el notebook
python3 scripts/build_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebook/analisis_carga_alostatica.ipynb

# 3. Renderizar la versión Quarto (requiere Quarto instalado: https://quarto.org)
cd quarto && quarto render index.qmd
```

## Notas metodológicas

- Todas las variables se normalizan con escalamiento mín-máx sobre el rango observado en la
  cohorte, para hacer comparables unidades muy distintas (mmHg, mg/dL, ms, pg/mL...).
- Las correlaciones reportadas son exploratorias (Pearson, Fase 1); con n = 26 deben leerse como
  hipótesis a confirmar, no como hallazgos concluyentes.
- Este repositorio es una pieza de portafolio derivada de un proyecto de investigación más
  amplio; no sustituye ni representa el reporte final de tesis.
