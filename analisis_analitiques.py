"""
Anàlisi exploratòria inicial de les variables analítiques
(abans de la neteja profunda). Genera estadístics descriptius
bàsics i boxplots globals i per sexe.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# =========================
# CONNEXIÓ AMB SQLALCHEMY
# =========================
engine = create_engine("mysql+pymysql://root:****@localhost/svrbi")

print("Carregant TOTES les dades...")
df = pd.read_sql("SELECT * FROM ckd_pacient_any", engine)

print(f"Registres totals: {len(df):,}")
print(f"Pacients únics: {df['PacientSAP'].nunique():,}")
print(f"Període: {df['any'].min()} - {df['any'].max()}")

# =========================
# VARIABLES ANALÍTIQUES
# =========================
variables = {
    'creatinina': 'Creatinina (mg/dL)',
    'fge_ckd_epi': 'FGe CKD-EPI (mL/min)',
    'colesterol_total': 'Colesterol total (mg/dL)',
    'colesterol_hdl': 'Colesterol HDL (mg/dL)',
    'colesterol_ldl': 'Colesterol LDL (mg/dL)',
    'quocient_albumina_creatinina': 'ACR (mg/g)',
    'hba1c': 'HbA1c (%)'
}

# Crear carpetes
os.makedirs("outputs/plots", exist_ok=True)
os.makedirs("outputs/taules", exist_ok=True)

# =========================
# PREPARACIÓ DE DADES
# =========================
for col in variables.keys():
    df[col] = pd.to_numeric(df[col], errors='coerce')

# =========================
# ESTADÍSTICS DESCRIPTIUS
# =========================
print("\n" + "=" * 60)
print("ESTADÍSTICS DESCRIPTIUS (SENSE FILTRAR)")
print("=" * 60)

resultats = []

for col, nom in variables.items():
    serie = df[col]

    n_total = len(serie)
    n_nuls = int(serie.isna().sum())
    n_no_nuls = int(serie.notna().sum())

    if n_no_nuls == 0:
        continue

    print(f"\n--- {nom} ---")
    print(f"  N total: {n_total:,}")
    print(f"  N no nuls: {n_no_nuls:,}")
    print(f"  Nuls: {n_nuls:,} ({n_nuls / n_total * 100:.2f}%)")
    print(f"  Mitjana: {serie.mean():.2f}")
    print(f"  Mediana: {serie.median():.2f}")
    print(f"  Desviació: {serie.std():.2f}")
    print(f"  Mínim: {serie.min():.2f}")
    print(f"  Màxim: {serie.max():.2f}")

    resultats.append({
        'variable': nom,
        'n_total': n_total,
        'n_no_nuls': n_no_nuls,
        'nuls': n_nuls,
        'pct_nuls': round(n_nuls / n_total * 100, 2),
        'mitjana': round(serie.mean(), 2),
        'mediana': round(serie.median(), 2),
        'desviacio': round(serie.std(), 2),
        'minim': round(serie.min(), 2),
        'maxim': round(serie.max(), 2)
    })

df_resultats = pd.DataFrame(resultats)
df_resultats.to_csv(
    "outputs/taules/estadistics_descriptius_raw.csv",
    index=False,
    encoding="utf-8-sig"
)

# =========================
# BOXPLOTS GLOBALS
# =========================
print("\n" + "=" * 60)
print("GENERANT BOXPLOTS GLOBALS")
print("=" * 60)

for col, nom in variables.items():
    if df[col].notna().sum() == 0:
        continue

    plt.figure(figsize=(6, 5))
    sns.boxplot(y=df[col])
    plt.title(f"{nom} - Boxplot global")
    plt.ylabel(nom)
    plt.tight_layout()
    plt.savefig(f"outputs/plots/boxplot_raw_{col}.png", dpi=300)
    plt.close()

print(" Boxplots globals guardats a outputs/plots/")

# =========================
# BOXPLOTS PER SEXE
# =========================
print("\n" + "=" * 60)
print("GENERANT BOXPLOTS PER SEXE")
print("=" * 60)

# només categories reals no nul·les
ordre_sexe = [x for x in ['F', 'M', 'U'] if x in df['sexe'].dropna().unique()]

for col, nom in variables.items():
    df_plot = df[['sexe', col]].copy()
    df_plot = df_plot[df_plot['sexe'].isin(ordre_sexe)]

    if df_plot[col].notna().sum() == 0 or len(df_plot) == 0:
        continue

    plt.figure(figsize=(8, 5))
    sns.boxplot(
        x='sexe',
        y=col,
        data=df_plot,
        order=ordre_sexe
    )
    plt.title(f"{nom} - Boxplot per sexe")
    plt.xlabel("Sexe")
    plt.ylabel(nom)
    plt.tight_layout()
    plt.savefig(f"outputs/plots/boxplot_raw_sexe_{col}.png", dpi=300)
    plt.close()

print("Boxplots per sexe guardats a outputs/plots/")

# =========================
# RESUM DE SEXE
# =========================
print("\n" + "=" * 60)
print("DISTRIBUCIÓ DE SEXE")
print("=" * 60)

sexe_dist = df['sexe'].value_counts(dropna=False).reset_index()
sexe_dist.columns = ['sexe', 'registres']
print(sexe_dist.to_string(index=False))

sexe_dist.to_csv(
    "outputs/taules/distribucio_sexe_raw.csv",
    index=False,
    encoding="utf-8-sig"
)

# =========================
# RESUM FINAL
# =========================
print("\n" + "=" * 60)
print("ANÀLISI COMPLETADA")
print("=" * 60)
print(" Resultats guardats a:")
print("   - outputs/taules/estadistics_descriptius_raw.csv")
print("   - outputs/taules/distribucio_sexe_raw.csv")
print("   - outputs/plots/boxplot_raw_*.png")
print("   - outputs/plots/boxplot_raw_sexe_*.png")