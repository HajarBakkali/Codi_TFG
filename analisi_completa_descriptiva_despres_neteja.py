"""
Anàlisi descriptiva final després de la neteja.
Genera estadístics, boxplots i violin plots de les variables analítiques,
i calcula la distribució per sexe i any.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# =========================
# CONNEXIÓ A LA BASE DE DADES
# =========================
engine = create_engine("mysql+pymysql://root:****@localhost/svrbi")

print("Carregant dades de ckd_pacient_any...")
df = pd.read_sql("SELECT * FROM ckd_pacient_any", engine)

# =========================
# EXCLUSIÓ D'OUTLIERS IMPOSSIBLES EN FGe
# =========================
initial_count = len(df)
df = df[~((df['fge_ckd_epi'] > 400) & (df['fge_ckd_epi'].notna()))]   # Elimina valors >400 (biològicament impossibles)
removed = initial_count - len(df)
if removed > 0:
    print(f"S'han eliminat {removed} registre amb FGe > 400 (biològicament impossible).")

# =========================
# EXCLUSIÓ DE VALORS EXTREMS DE COLESTEROL TOTAL (RANG 50-1000 mg/dL)
# =========================
initial_count_col = len(df)
df = df[(df['colesterol_total'] >= 50) & (df['colesterol_total'] <= 1000) | (df['colesterol_total'].isna())]   # Manté valors dins del rang [50,1000] o nuls
removed_col = initial_count_col - len(df)
if removed_col > 0:
    print(f"S'han eliminat {removed_col} registres amb colesterol total fora del rang fisiològic ( <50 o >1000 mg/dL).")

# =========================
# CARPETA DE SORTIDA
# =========================
output_dir = "outputs/descriptiva_final"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(f"{output_dir}/plots/edat", exist_ok=True)
os.makedirs(f"{output_dir}/plots/analitiques_globals", exist_ok=True)
os.makedirs(f"{output_dir}/plots/analitiques_per_sexe", exist_ok=True)
os.makedirs(f"{output_dir}/plots/boxplots_globals", exist_ok=True)
os.makedirs(f"{output_dir}/plots/violin_globals", exist_ok=True)
os.makedirs(f"{output_dir}/plots/boxplots_sexe", exist_ok=True)
os.makedirs(f"{output_dir}/plots/violin_sexe", exist_ok=True)
os.makedirs(f"{output_dir}/taules", exist_ok=True)

# =========================
# VARIABLES ANALÍTIQUES QUE ESTUDIAREM
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

# Convertir a numèric per si de cas (els valors no numèrics passen a NaN)
for col in variables.keys():
    df[col] = pd.to_numeric(df[col], errors='coerce')

# =========================
# ELIMINACIÓ DE VALORS NEGATIUS (BIOLÒGICAMENT IMPOSSIBLES)
# =========================
negative_cols = ['creatinina', 'fge_ckd_epi', 'colesterol_total', 'colesterol_hdl', 'colesterol_ldl']
neg_removed = 0
for col in negative_cols:
    n_neg = (df[col] < 0).sum()
    if n_neg > 0:
        df.loc[df[col] < 0, col] = pd.NA
        neg_removed += n_neg
        print(f"S'han convertit a nul {n_neg} valors negatius de {col}.")
if neg_removed > 0:
    print(f"Total de valors negatius eliminats: {neg_removed}")

print(f"Registres després de neteja: {len(df):,}")
print(f"Pacients únics després de neteja: {df['PacientSAP'].nunique():,}")
print()

# =========================
# ESTADÍSTICS DESCRIPTIUS (MITJANA, MEDIANA, DESVIACIÓ, MÍNIM, MÀXIM)
# =========================
resultats = []
print("="*60)
print("ESTADÍSTICS DESCRIPTIUS")
print("="*60)
print(f"{'Variable':30} {'n':>10} {'Mitjana':>10} {'Mediana':>10} {'Desviació':>10} {'Mínim':>10} {'Màxim':>10}")
print("-"*90)

for col, nom in variables.items():
    serie = df[col].dropna()
    if len(serie) == 0:
        continue
    resultats.append({
        'variable': nom,
        'n': len(serie),
        'pct_nuls': round((df[col].isna().sum()/len(df))*100, 1),
        'mitjana': round(serie.mean(), 2),
        'mediana': round(serie.median(), 2),
        'desviacio': round(serie.std(), 2),
        'minim': round(serie.min(), 2),
        'maxim': round(serie.max(), 2)
    })
    print(f"{nom:30} {len(serie):>10,} {serie.mean():>10.2f} {serie.median():>10.2f} {serie.std():>10.2f} {serie.min():>10.2f} {serie.max():>10.2f}")

# Guardar els estadístics en un CSV
df_res = pd.DataFrame(resultats)
df_res.to_csv(f"{output_dir}/taules/estadistics_analitiques.csv", index=False, encoding="utf-8-sig")

# =========================
# FUNCIÓ PER GENERAR FIGURES (BOXPLOT + VIOLIN)
# =========================
def genera_figures(col, nom):
    datos = df[col].dropna()
    if len(datos) == 0:
        return
    
    # FIGURA 1: Boxplot global
    plt.figure(figsize=(6,5))
    sns.boxplot(y=datos, color='steelblue')
    plt.title(f"{nom} - Boxplot global")
    plt.ylabel(nom)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/plots/boxplots_globals/boxplot_global_{col}.png", dpi=300)
    plt.close()
    
    # FIGURA 2: Violin plot global (millor per a distribucions asimètriques)
    if col == 'quocient_albumina_creatinina':
        plt.figure(figsize=(6,5))
        sns.violinplot(y=datos, color='lightblue')
        plt.yscale('log')
        plt.title(f"{nom} - Violin plot global (escala log)")
        plt.ylabel(nom + " (log scale)")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/plots/violin_globals/violin_global_{col}.png", dpi=300)
        plt.close()
    else:
        plt.figure(figsize=(6,5))
        sns.violinplot(y=datos, color='lightblue')
        plt.title(f"{nom} - Violin plot global")
        plt.ylabel(nom)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/plots/violin_globals/violin_global_{col}.png", dpi=300)
        plt.close()
    
    # FIGURA 3: Boxplot per sexe
    df_plot = df[['sexe', col]].dropna()
    df_plot = df_plot[df_plot['sexe'].isin(['F', 'M'])]
    if len(df_plot) > 0:
        plt.figure(figsize=(8,5))
        sns.boxplot(x='sexe', y=col, data=df_plot, order=['F', 'M'])
        plt.title(f"{nom} - Boxplot per sexe")
        plt.xlabel("Sexe")
        plt.ylabel(nom)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/plots/boxplots_sexe/boxplot_sexe_{col}.png", dpi=300)
        plt.close()
        
        # FIGURA 4: Violin plot per sexe
        plt.figure(figsize=(8,5))
        sns.violinplot(x='sexe', y=col, data=df_plot, order=['F', 'M'])
        plt.title(f"{nom} - Violin plot per sexe")
        plt.xlabel("Sexe")
        plt.ylabel(nom)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/plots/violin_sexe/violin_sexe_{col}.png", dpi=300)
        plt.close()

# =========================
# GENERAR FIGURES PER A CADA VARIABLE
# =========================
print("\nGenerant figures (boxplot + violin plot)...")
for col, nom in variables.items():
    genera_figures(col, nom)
    print(f"  {nom}")

# =========================
# EDAT: BOXPLOT I VIOLIN PLOT
# =========================
edat = df['edat'].dropna()
plt.figure(figsize=(10,4))
sns.boxplot(x=edat, color='steelblue')
plt.title("Distribució de l'edat (boxplot)")
plt.xlabel("Edat (anys)")
plt.tight_layout()
plt.savefig(f"{output_dir}/plots/edat/boxplot_edat.png", dpi=300)
plt.close()

plt.figure(figsize=(10,4))
sns.violinplot(x=edat, color='lightblue')
plt.title("Distribució de l'edat (violin plot)")
plt.xlabel("Edat (anys)")
plt.tight_layout()
plt.savefig(f"{output_dir}/plots/edat/violin_edat.png", dpi=300)
plt.close()
print("Figures d'edat")

# =========================
# DISTRIBUCIÓ PER SEXE I ANY (TAULES)
# =========================
df_pacients = df.drop_duplicates(subset=['PacientSAP'])
sexe_counts = df_pacients['sexe'].value_counts(dropna=False).reset_index()
sexe_counts.columns = ['sexe', 'pacients']
sexe_counts['percentatge'] = (sexe_counts['pacients'] / sexe_counts['pacients'].sum() * 100).round(2)
sexe_counts.to_csv(f"{output_dir}/taules/distribucio_sexe.csv", index=False, encoding="utf-8-sig")

any_counts = df.groupby('any').size().reset_index(name='registres')
any_counts.to_csv(f"{output_dir}/taules/distribucio_anys.csv", index=False, encoding="utf-8-sig")

# =========================
# FI DE L'ANÀLISI
# =========================
print("\n" + "="*60)
print("ANÀLISI COMPLETADA")
print("="*60)
print(f"Resultats guardats a: {output_dir}/")
print("   - taules/estadistics_analitiques.csv (inclou desviació)")
print("   - taules/distribucio_sexe.csv")
print("   - taules/distribucio_anys.csv")
print("   - plots/edat/boxplot_edat.png / violin_edat.png")
print("   - plots/boxplots_globals/ (boxplot global per variable)")
print("   - plots/violin_globals/ (violin global per variable)")
print("   - plots/boxplots_sexe/ (boxplot per sexe)")
print("   - plots/violin_sexe/ (violin per sexe)")