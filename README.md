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
reemplazados por códigos anónimos `P01`–`P32` antes de que ningún dato saliera de la carpeta de
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

- El dashboard resume el grupo con la **mediana** (no el promedio): la muestra es pequeña (n=26)
  y varios biomarcadores tienen valores atípicos que distorsionan la media.
- Los cambios porcentuales no se etiquetan como "mejora" o "deterioro" — esa lectura depende del
  indicador y del criterio clínico de quien lo revisa; un aumento no es automáticamente positivo
  ni negativo (p. ej. HDL vs. LDL).
- Para el análisis exploratorio más técnico (correlaciones de Pearson, normalización min-max,
  radar por sujeto) ver `notebook/` y `quarto/`; el dashboard en `docs/` deliberadamente deja ese
  nivel de detalle fuera de la vista principal por tratarse de una audiencia clínica no
  especializada en HRV.
- Este repositorio es una pieza de portafolio derivada de un proyecto de investigación más
  amplio; no sustituye ni representa el reporte final de tesis.

## Discrepancia de datos conocida — cortisol

El dashboard calcula un cambio de **+52.2%** en la mediana de cortisol entre Fase 1 y Fase 2
(n=26, `2027-DATOS REVISADOS.csv`). Un artículo relacionado de este mismo proyecto reporta
**+61%**. Se investigó esta discrepancia antes de publicar el panel, probando las fórmulas más
comunes de "cambio de grupo":

| Fórmula | Resultado |
|---|---|
| Cambio de la media del grupo | +54.9% |
| Media de los cambios individuales (%) | +57.0% |
| Cambio de la mediana del grupo (la que usa el dashboard) | +52.2% |
| Reportado en el artículo | +61% |

Ninguna reconcilia exactamente con el +61% publicado. Un participante (P15 / PM19) tiene el
mismo valor de cortisol en ambas fases (9.82 µg/dL) — podría ser un cambio real de cero o un
marcador de dato faltante en Fase 2; excluirlo mueve el cálculo a +58.5%/+59.3% según la
fórmula, tampoco exacto. No se ajustaron los datos para forzar la coincidencia: la discrepancia
se documenta aquí y dentro del propio dashboard (acordeón "Cómo leer este panel y calidad de los
datos"), en vez de maquillarla. Si tienes a mano la versión de la base o la fórmula exacta que
usó el artículo, con eso se puede cerrar la brecha.
