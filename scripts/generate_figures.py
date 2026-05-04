"""
generate_figures.py
Genera las figuras académicas para el reporte de investigación LaTeX.
Salida: Documentacion/figures/*.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
ROOT    = Path(__file__).parent.parent
CSV     = ROOT / "resultados_calidad_datos_nl.csv"
OUT_DIR = ROOT / "Documentacion" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Paleta editorial coherente con el dashboard
GOLD   = "#F5C842"
SILVER = "#A8B2BD"
BRONZE = "#C47C3A"
BLUE   = "#2D6A9F"
TEAL   = "#1A8F80"
DARK   = "#1C1C2E"
LIGHT  = "#F4F7FA"

plt.rcParams.update({
    "font.family":     "sans-serif",
    "font.size":       11,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.facecolor":     LIGHT,
    "figure.facecolor":   "white",
    "axes.titlesize":     13,
    "axes.titleweight":   "bold",
})

df = pd.read_csv(CSV)

# ── Figura 1: Histograma distribución de scores globales ────────────────────
fig, ax = plt.subplots(figsize=(8, 4.5))

bins   = np.arange(50, 101, 2.5)
counts, edges, patches = ax.hist(df["score_global"], bins=bins, edgecolor="white", linewidth=0.8)

# Colorear por clasificación
for patch, left in zip(patches, edges[:-1]):
    if left >= 90:
        patch.set_facecolor(GOLD)
    elif left >= 70:
        patch.set_facecolor(SILVER)
    else:
        patch.set_facecolor(BRONZE)

# Línea de promedio
mean_score = df["score_global"].mean()
ax.axvline(mean_score, color=DARK, linestyle="--", linewidth=1.5, label=f"Promedio: {mean_score:.2f}")

ax.set_xlabel("Score Global (0–100)", labelpad=8)
ax.set_ylabel("Número de recursos", labelpad=8)
ax.set_title("Distribución del Score Global de Calidad — 288 Recursos", pad=12)

legend_patches = [
    mpatches.Patch(color=GOLD,   label=f"Gold ≥ 90  ({(df['score_global']>=90).sum()} recursos)"),
    mpatches.Patch(color=SILVER, label=f"Silver 70–89  ({((df['score_global']>=70)&(df['score_global']<90)).sum()} recursos)"),
    mpatches.Patch(color=BRONZE, label=f"Bronze < 70  ({(df['score_global']<70).sum()} recursos)"),
]
ax.legend(handles=legend_patches + [plt.Line2D([0],[0], color=DARK, linestyle="--", label=f"Promedio: {mean_score:.2f}")],
          frameon=False, fontsize=9.5)

plt.tight_layout()
fig.savefig(OUT_DIR / "fig1_distribucion_scores.png", dpi=180, bbox_inches="tight")
plt.close()
print("[OK] fig1_distribucion_scores.png")

# ── Figura 2: Comparativa de dimensiones (barras horizontales) ─────────────
dims_labels = {
    "comp_completitud_global_pct":  "Completitud",
    "acc_score_accuracy_pct":       "Exactitud",
    "cons_score_consistency_pct":   "Consistencia",
    "uniq_score_uniqueness_pct":    "Unicidad",
    "time_score_timeliness_pct":    "Puntualidad",
    "doc_score_documentation_pct":  "Documentación",
    "open_score_openness_pct":      "Apertura",
}
weights = {
    "Completitud":   0.30, "Exactitud":    0.25, "Consistencia": 0.15,
    "Unicidad":      0.08, "Puntualidad":  0.05, "Documentación":0.10, "Apertura": 0.07,
}
means = {label: df[col].mean() for col, label in dims_labels.items()}
sorted_dims  = sorted(means, key=means.get)
sorted_means = [means[d] for d in sorted_dims]

fig, ax = plt.subplots(figsize=(8, 5))
colors = [BRONZE if means[d] < 80 else TEAL for d in sorted_dims]
bars   = ax.barh(sorted_dims, sorted_means, color=colors, height=0.6, edgecolor="white")

# Valores + peso ponderado
for bar, dim, val in zip(bars, sorted_dims, sorted_means):
    w = weights.get(dim, 0)
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}  (w={w:.0%})", va="center", fontsize=9.5, color=DARK)

ax.set_xlim(0, 107)
ax.set_xlabel("Score promedio (0–100)", labelpad=8)
ax.set_title("Score Promedio por Dimensión de Calidad ISO 25012", pad=12)
ax.axvline(80, color=BRONZE, linestyle=":", linewidth=1.2, label="Umbral mínimo 80")
ax.legend(frameon=False, fontsize=9)

plt.tight_layout()
fig.savefig(OUT_DIR / "fig2_dimensiones.png", dpi=180, bbox_inches="tight")
plt.close()
print("[OK] fig2_dimensiones.png")

# ── Figura 3: Distribución Gold / Silver / Bronze (donut) ─────────────────
gold_n   = (df["score_global"] >= 90).sum()
silver_n = ((df["score_global"] >= 70) & (df["score_global"] < 90)).sum()
bronze_n = (df["score_global"] < 70).sum()
total    = len(df)

labels  = [f"Gold\n{gold_n} ({gold_n/total*100:.1f}%)",
           f"Silver\n{silver_n} ({silver_n/total*100:.1f}%)",
           f"Bronze\n{bronze_n} ({bronze_n/total*100:.1f}%)"]
sizes   = [gold_n, silver_n, bronze_n]
colors_ = [GOLD, SILVER, BRONZE]

fig, ax = plt.subplots(figsize=(6, 5))
wedges, texts = ax.pie(sizes, colors=colors_, startangle=90,
                       wedgeprops={"edgecolor":"white","linewidth":2},
                       pctdistance=0.75)
# Donut hole
centre_circle = plt.Circle((0,0), 0.55, fc="white")
ax.add_artist(centre_circle)
ax.text(0, 0, f"{total}\nrecursos", ha="center", va="center", fontsize=13, fontweight="bold", color=DARK)
ax.legend(wedges, labels, loc="lower center", bbox_to_anchor=(0.5, -0.08),
          ncol=3, frameon=False, fontsize=9.5)
ax.set_title("Clasificación de Salud de Datos — Escala Medallion", pad=14)

plt.tight_layout()
fig.savefig(OUT_DIR / "fig3_clasificacion.png", dpi=180, bbox_inches="tight")
plt.close()
print("[OK] fig3_clasificacion.png")

# ── Figura 4: Top 10 organizaciones por score ─────────────────────────────
org = (df.groupby("organizacion")["score_global"]
         .agg(["mean","count"])
         .query("count >= 2")
         .sort_values("mean", ascending=False)
         .head(10))

# Limpiar nombres largos
org.index = [n[:38]+"…" if len(n)>38 else n for n in org.index]

fig, ax = plt.subplots(figsize=(9, 5.5))
y_pos  = range(len(org))
bars   = ax.barh(list(y_pos), org["mean"], color=TEAL, height=0.6, edgecolor="white")
ax.set_yticks(list(y_pos))
ax.set_yticklabels(org.index, fontsize=9)
ax.set_xlim(85, 100)
ax.set_xlabel("Score Global Promedio", labelpad=8)
ax.set_title("Top 10 Dependencias por Calidad de Datos\n(mín. 2 recursos evaluados)", pad=12)

for bar, (_, row) in zip(bars, org.iterrows()):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f"{row['mean']:.2f}  (n={int(row['count'])})",
            va="center", fontsize=8.5, color=DARK)

plt.tight_layout()
fig.savefig(OUT_DIR / "fig4_top_organizaciones.png", dpi=180, bbox_inches="tight")
plt.close()
print("[OK] fig4_top_organizaciones.png")

print("\n[OK] Todas las figuras generadas en Documentacion/figures/")
