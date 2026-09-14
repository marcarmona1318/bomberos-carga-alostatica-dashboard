"""
Prepara y anonimiza los datos de carga alostatica en bomberos para el dashboard
de portafolio. Fusiona los 4 archivos normalizados (biomarcadores, HRV supina,
HRV de pie, resiliencia BRS) con los valores crudos correspondientes, asigna
codigos de sujeto anonimos (P01..P26) y exporta un JSON listo para consumir
desde HTML/JS y un CSV limpio para el notebook.

Fuente: 02_DATOS/PROCESADOS/*.csv (proyecto de tesis doctoral, Marcel Carmona)
"""
import json
import pandas as pd
import numpy as np

SRC = "/Users/marcelcarmona/Documents/DOCTORADO/METODOLOGIA/02_DATOS/PROCESADOS"
OUT = "/Users/marcelcarmona/Documents/DOCTORADO/METODOLOGIA/02_DATOS/dashboard_portafolio"

bio = pd.read_csv(f"{SRC}/biomarcadores_normalizados_minmax.csv")
sup = pd.read_csv(f"{SRC}/HRV_sup_normalizado_minmax.csv")
st = pd.read_csv(f"{SRC}/HRV_st_normalizado_minmax.csv")
brs = pd.read_csv(f"{SRC}/Resiliencia_BRS_normalizado_minmax.csv")
raw = pd.read_csv(f"{SRC}/2027-DATOS REVISADOS.csv")

# --- anonymize: assign P01..P26 by ascending PM, drop names entirely -------
pm_order = sorted(bio["PM"].unique())
code_of = {pm: f"P{str(i+1).zfill(2)}" for i, pm in enumerate(pm_order)}

for df in (bio, sup, st, brs, raw):
    df["SUBJECT"] = df["PM"].map(code_of)
    df.drop(columns=[c for c in ["NOMBRE"] if c in df.columns], inplace=True)

bio = bio.set_index("SUBJECT")
sup = sup.set_index("SUBJECT")
st = st.set_index("SUBJECT")
brs = brs.set_index("SUBJECT")
raw = raw.set_index("SUBJECT")

# --- variable catalogs -------------------------------------------------
BIOMARCADORES = [
    ("INDICE_CINTURA", "Indice cintura-cadera", ""),
    ("BMI", "IMC", "kg/m2"),
    ("SISTOLICA", "Presion sistolica", "mmHg"),
    ("DIASTOLICA", "Presion diastolica", "mmHg"),
    ("F_CARDIACA", "Frecuencia cardiaca", "lpm"),
    ("COLESTEROL", "Colesterol total", "mg/dL"),
    ("TRIGLICERIDOS", "Trigliceridos", "mg/dL"),
    ("HDL", "HDL", "mg/dL"),
    ("LDL", "LDL", "mg/dL"),
    ("ALBUMINA", "Albumina", "g/dL"),
    ("GLUCOSA", "Glucosa", "mg/dL"),
    ("IL6", "Interleucina-6", "pg/mL"),
    ("CORTISOL", "Cortisol", "ug/dL"),
    ("H_GLICOSILADA", "Hemoglobina glicosilada", "%"),
    ("PCR", "Proteina C reactiva", "mg/L"),
]
HRV_VARS = [
    ("SDNN", "SDNN", "ms"),
    ("RMSSD", "RMSSD", "ms"),
    ("lnRMSSD", "ln(RMSSD)", ""),
    ("SD1", "SD1 (Poincare)", "ms"),
    ("SD2", "SD2 (Poincare)", "ms"),
    ("MeanHR", "Frecuencia cardiaca media", "lpm"),
    ("LF", "Potencia LF", "ms2"),
    ("HF", "Potencia HF", "ms2"),
    ("LFHF", "Razon LF/HF", ""),
]

def series(df, col):
    return pd.to_numeric(df[col], errors="coerce")

subjects = []
for s in bio.index:
    subjects.append({
        "id": s,
        "edad": int(raw.loc[s, "EDAD"]) if s in raw.index else None,
        "genero": "M" if (s in raw.index and raw.loc[s, "GENERO"] == 1) else "F",
        "tum_cert": bool(raw.loc[s, "TUM_CERT"]) if s in raw.index else None,
        "exp_previa": bool(raw.loc[s, "EXPERIENCIA PREVIA EMERGENCIAS"]) if s in raw.index else None,
    })

biomarcadores_data = {}
for s in bio.index:
    row = {}
    for key, label, unit in BIOMARCADORES:
        row[key] = {
            "f1_norm": round(float(series(bio, f"{key}_norm")[s]), 4),
            "f2_norm": round(float(series(bio, f"{key}_F2_norm")[s]), 4),
            "f1_raw": float(series(raw, key)[s]) if key in raw.columns else None,
            "f2_raw": float(series(raw, f"{key}_F2")[s]) if f"{key}_F2" in raw.columns else None,
        }
    biomarcadores_data[s] = row

def hrv_block(df, prefix, raw_prefix):
    out = {}
    for s in df.index:
        row = {}
        for key, label, unit in HRV_VARS:
            fcol = f"{prefix}{key}_norm"
            f2col = f"F2_{prefix}{key}_norm"
            raw_col = f"{raw_prefix}{key}"
            raw_f2 = f"F2_{raw_prefix}{key}"
            row[key] = {
                "f1_norm": round(float(series(df, fcol)[s]), 4),
                "f2_norm": round(float(series(df, f2col)[s]), 4),
                "f1_raw": float(series(raw, raw_col)[s]) if raw_col in raw.columns else None,
                "f2_raw": float(series(raw, raw_f2)[s]) if raw_f2 in raw.columns else None,
            }
        out[s] = row
    return out

hrv_sup_data = hrv_block(sup, "sup_", "sup_")
hrv_st_data = hrv_block(st, "st_", "st_")

brs_data = {}
for s in brs.index:
    brs_data[s] = {
        "f1": float(brs.loc[s, "BRS_promedio"]),
        "f2": float(brs.loc[s, "BRS_promedio_F2"]),
        "f1_norm": round(float(brs.loc[s, "BRS_promedio_norm"]), 4),
        "f2_norm": round(float(brs.loc[s, "BRS_promedio_F2_norm"]), 4),
        "estado_fase2": brs.loc[s, "Estado_Fase2"],
        "requiere_revision": brs.loc[s, "Requiere_revision"],
    }

# --- KPIs ----------------------------------------------------------------
brs_f1 = np.array([v["f1"] for v in brs_data.values()])
brs_f2 = np.array([v["f2"] for v in brs_data.values()])
pct_mejora = float((brs_f2 > brs_f1).mean() * 100)
edades = [x["edad"] for x in subjects if x["edad"] is not None]

kpis = {
    "n_sujetos": len(subjects),
    "edad_promedio": round(float(np.mean(edades)), 1),
    "brs_f1_promedio": round(float(brs_f1.mean()), 2),
    "brs_f2_promedio": round(float(brs_f2.mean()), 2),
    "pct_mejora_resiliencia": round(pct_mejora, 1),
    "pct_masculino": round(float(np.mean([1 if x["genero"] == "M" else 0 for x in subjects]) * 100), 1),
}

# --- curated correlation matrix (F1, normalized) --------------------------
curated = {
    "BMI": biomarcadores_data,
    "SISTOLICA": biomarcadores_data,
    "F_CARDIACA": biomarcadores_data,
    "GLUCOSA": biomarcadores_data,
    "COLESTEROL": biomarcadores_data,
    "TRIGLICERIDOS": biomarcadores_data,
    "HDL": biomarcadores_data,
    "IL6": biomarcadores_data,
    "PCR": biomarcadores_data,
    "CORTISOL": biomarcadores_data,
}
curated_labels = {
    "BMI": "IMC", "SISTOLICA": "Sistolica", "F_CARDIACA": "Fc reposo",
    "GLUCOSA": "Glucosa", "COLESTEROL": "Colesterol", "TRIGLICERIDOS": "Trigliceridos",
    "HDL": "HDL", "IL6": "IL-6", "PCR": "PCR", "CORTISOL": "Cortisol",
    "sup_SDNN": "SDNN supino", "sup_LFHF": "LF/HF supino",
    "st_SDNN": "SDNN de pie", "st_LFHF": "LF/HF de pie",
    "BRS": "Resiliencia (BRS)",
}
corr_frame = pd.DataFrame({k: series(bio, f"{k}_norm") for k in curated})
corr_frame["sup_SDNN"] = series(sup, "sup_SDNN_norm")
corr_frame["sup_LFHF"] = series(sup, "sup_LFHF_norm")
corr_frame["st_SDNN"] = series(st, "st_SDNN_norm")
corr_frame["st_LFHF"] = series(st, "st_LFHF_norm")
corr_frame["BRS"] = series(brs, "BRS_promedio_norm")
corr_frame.index = bio.index
corr_matrix = corr_frame.corr(method="pearson").round(3)

# strongest correlate with BRS (excluding itself)
brs_corr = corr_matrix["BRS"].drop("BRS").abs().sort_values(ascending=False)
kpis["variable_mas_asociada_resiliencia"] = curated_labels[brs_corr.index[0]]
kpis["r_variable_mas_asociada_resiliencia"] = round(float(corr_matrix["BRS"][brs_corr.index[0]]), 2)

# --- domain summaries for F1 vs F2 dumbbell chart --------------------------
def domain_summary(data_dict, var_catalog):
    rows = []
    for key, label, unit in var_catalog:
        f1_vals = [data_dict[s][key]["f1_norm"] for s in data_dict]
        f2_vals = [data_dict[s][key]["f2_norm"] for s in data_dict]
        rows.append({
            "key": key, "label": label, "unit": unit,
            "f1_mean": round(float(np.nanmean(f1_vals)), 4),
            "f2_mean": round(float(np.nanmean(f2_vals)), 4),
        })
    rows.sort(key=lambda r: r["f2_mean"] - r["f1_mean"])
    return rows

domains = {
    "biomarcadores": domain_summary(biomarcadores_data, BIOMARCADORES),
    "hrv_sup": domain_summary(hrv_sup_data, HRV_VARS),
    "hrv_st": domain_summary(hrv_st_data, HRV_VARS),
}
domains["resiliencia"] = [{
    "key": "BRS_promedio", "label": "BRS promedio", "unit": "escala 1-5",
    "f1_mean": round(float(brs_f1.mean()), 4), "f2_mean": round(float(brs_f2.mean()), 4),
}]

# --- assemble & write ------------------------------------------------------
payload = {
    "meta": {
        "n": len(subjects),
        "descripcion": "Carga alostatica en personal de bomberos - Fase 1 (F1) vs Fase 2 (F2)",
        "fuente": "Tesis doctoral, Marcel Carmona - datos anonimizados (PM -> P01..P26)",
    },
    "kpis": kpis,
    "subjects": subjects,
    "biomarcadores_catalog": [{"key": k, "label": l, "unit": u} for k, l, u in BIOMARCADORES],
    "hrv_catalog": [{"key": k, "label": l, "unit": u} for k, l, u in HRV_VARS],
    "biomarcadores": biomarcadores_data,
    "hrv_sup": hrv_sup_data,
    "hrv_st": hrv_st_data,
    "brs": brs_data,
    "correlation": {
        "labels": [curated_labels[c] for c in corr_matrix.columns],
        "keys": list(corr_matrix.columns),
        "matrix": corr_matrix.values.round(3).tolist(),
    },
    "domains": domains,
}

with open(f"{OUT}/data/dashboard_data.json", "w") as f:
    json.dump(payload, f, ensure_ascii=False, indent=1)

# --- clean anonymized CSV (long-ish, wide is fine here given N small) ------
wide_rows = []
for s in bio.index:
    row = {"sujeto": s, "edad": raw.loc[s, "EDAD"] if s in raw.index else None,
           "genero": "M" if raw.loc[s, "GENERO"] == 1 else "F"}
    for key, _, _ in BIOMARCADORES:
        row[f"{key}_F1"] = biomarcadores_data[s][key]["f1_raw"]
        row[f"{key}_F2"] = biomarcadores_data[s][key]["f2_raw"]
    for key, _, _ in HRV_VARS:
        row[f"sup_{key}_F1"] = hrv_sup_data[s][key]["f1_raw"]
        row[f"sup_{key}_F2"] = hrv_sup_data[s][key]["f2_raw"]
        row[f"st_{key}_F1"] = hrv_st_data[s][key]["f1_raw"]
        row[f"st_{key}_F2"] = hrv_st_data[s][key]["f2_raw"]
    row["BRS_F1"] = brs_data[s]["f1"]
    row["BRS_F2"] = brs_data[s]["f2"]
    wide_rows.append(row)

pd.DataFrame(wide_rows).to_csv(f"{OUT}/data/cohorte_anonimizada.csv", index=False)

print("OK ->", f"{OUT}/data/dashboard_data.json")
print("OK ->", f"{OUT}/data/cohorte_anonimizada.csv")
print("KPIs:", json.dumps(kpis, indent=2, ensure_ascii=False))
