"""
Anàlisi de les variables demogràfiques i temporals:
- Distribució per sexe (últim any per pacient)
- Estadístics d'edat (registres pacient-any)
- Identificació de valors d'edat invàlids
- Boxplots d'edat globals i per any (després de neteja)
- Anàlisi completa per ABS (top, bottom, histogrames, scatter)
- Distribució temporal per any (registres pacient-any)
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# =========================
# CONNEXIÓ (CONTRASENYA OCULTA PER SEGURETAT)
# =========================
engine = create_engine("mysql+pymysql://root:****@localhost/svrbi")

print("Carregant dades...")
df = pd.read_sql("SELECT PacientSAP, edat, sexe, PAT_ABS, any FROM ckd_pacient_any", engine)

print(f"Registres totals (pacient-any): {len(df):,}")
print(f"Pacients únics: {df['PacientSAP'].nunique():,}")

# =========================
# NETEJA INICIAL: PAT_ABS ('None' -> NaN)
# =========================
df['PAT_ABS'] = df['PAT_ABS'].replace('None', pd.NA)

# =========================
# CARPETA ESPECÍFICA PER A LA SORTIDA
# =========================
output_dir = "outputs/demografiques"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(f"{output_dir}/plots", exist_ok=True)
os.makedirs(f"{output_dir}/taules", exist_ok=True)

# =========================
# 1. SEXE (PACIENTS ÚNICS, ÚLTIM ANY DISPONIBLE)
# =========================
print("\n" + "="*60)
print("SEXE (PACIENTS ÚNICS - últim any per pacient)")
print("="*60)

# Per a cada pacient, agafem l'últim any disponible (assumim que sexe és estable)
df_pacients = df.sort_values(['PacientSAP', 'any']).groupby('PacientSAP').last().reset_index()

sexe_counts = df_pacients['sexe'].value_counts(dropna=False).reset_index()
sexe_counts.columns = ['sexe', 'pacients']
sexe_counts['percentatge'] = (sexe_counts['pacients'] / sexe_counts['pacients'].sum() * 100).round(2)

print(sexe_counts.to_string(index=False))
sexe_counts.to_csv(f"{output_dir}/taules/pacients_per_sexe.csv", index=False, encoding="utf-8-sig")

# =========================
# 2. EDAT (REGISTRES PACIENT-ANY) - ABANS DE NETEJA D'EDAT
# =========================
print("\n" + "="*60)
print("EDAT (REGISTRES PACIENT-ANY) - abans de neteja")
print("="*60)

edat_totes = df['edat'].dropna()
print(f"Registres amb edat no nul·la: {len(edat_totes):,}")
print(f"Mínim: {edat_totes.min():.0f}")
print(f"Màxim: {edat_totes.max():.0f}")
print(f"Mitjana: {edat_totes.mean():.1f}")
print(f"Mediana: {edat_totes.median():.1f}")
print(f"Desviació: {edat_totes.std():.1f}")

# =========================
# 3. IDENTIFICAR I ELIMINAR VALORS D'EDAT INVÀLIDS (NEGATIVA O >150)
# =========================
print("\n" + "="*60)
print("NETEJA D'EDAT: excloent valors <0 o >150")
print("="*60)

edat_invalida = df[(df['edat'] < 0) | (df['edat'] > 150)]
print(f"Registres amb edat invàlida: {len(edat_invalida):,}")
print(f"Pacients afectats: {edat_invalida['PacientSAP'].nunique():,}")

if len(edat_invalida) > 0:
    print("\nValors d'edat invàlids trobats:")
    print(edat_invalida[['PacientSAP', 'edat', 'any']].drop_duplicates().to_string(index=False))

# Eliminar registres amb edat invàlida
df_net = df[(df['edat'] >= 0) & (df['edat'] <= 150)].copy()
print(f"Registres després de neteja d'edat: {len(df_net):,}")

# =========================
# 4. ESTADÍSTICS D'EDAT POST-NETEJA
# =========================
print("\n" + "="*60)
print("EDAT (REGISTRES PACIENT-ANY) - després de neteja")
print("="*60)

edat_neta = df_net['edat'].dropna()
print(f"Registres vàlids: {len(edat_neta):,}")
print(f"Mínim: {edat_neta.min():.0f}")
print(f"Màxim: {edat_neta.max():.0f}")
print(f"Mitjana: {edat_neta.mean():.1f}")
print(f"Mediana: {edat_neta.median():.1f}")
print(f"Desviació: {edat_neta.std():.1f}")

# Guardar estadístics post-neteja
pd.DataFrame([{
    "registres_edat_valids": len(edat_neta),
    "min": edat_neta.min(),
    "max": edat_neta.max(),
    "mitjana": round(edat_neta.mean(), 1),
    "mediana": round(edat_neta.median(), 1),
    "std": round(edat_neta.std(), 1)
}]).to_csv(f"{output_dir}/taules/edat_post_neteja_stats.csv", index=False, encoding="utf-8-sig")

# =========================
# 5. GRÀFICS D'EDAT: BOXPLOT GLOBAL I BOXPLOTS PER ANY
# =========================
print("\n" + "="*60)
print("GENERANT GRÀFICS D'EDAT")
print("="*60)

# Boxplot global (post-neteja)
plt.figure(figsize=(10,4))
sns.boxplot(x=edat_neta, color='steelblue')
plt.title("Boxplot de l'edat (registres pacient-any, dades netes)")
plt.xlabel("Edat (anys)")
plt.tight_layout()
plt.savefig(f"{output_dir}/plots/edat_boxplot_global.png", dpi=300)
plt.close()

# Boxplots per any (post-neteja)
plt.figure(figsize=(12, 6))
sns.boxplot(data=df_net, x='any', y='edat', palette='Blues')
plt.title("Distribució de l'edat per any (registres pacient-any, dades netes)")
plt.xlabel("Any")
plt.ylabel("Edat (anys)")
plt.tight_layout()
plt.savefig(f"{output_dir}/plots/edat_boxplot_per_any.png", dpi=300)
plt.close()

# =========================
# 6. TAULA D'ESTADÍSTICS D'EDAT PER ANY
# =========================
print("\n" + "="*60)
print("ESTADÍSTICS D'EDAT PER ANY")
print("="*60)

edat_per_any = df_net.groupby('any')['edat'].agg(['mean', 'median', 'std', 'min', 'max']).round(1)
edat_per_any = edat_per_any.reset_index()
print(edat_per_any.to_string(index=False))
edat_per_any.to_csv(f"{output_dir}/taules/edat_per_any_stats.csv", index=False, encoding="utf-8-sig")

# =========================
# 7. ABS - ANÀLISI SOBRE PACIENTS ÚNICS (ÚLTIM ANY)
# =========================
print("\n" + "="*60)
print("ABS (PACIENTS ÚNICS - últim any) - ANÀLISI COMPLETA")
print("="*60)

# Utilitzem df_pacients que ja té l'últim any per pacient
abs_counts = df_pacients['PAT_ABS'].value_counts(dropna=False).reset_index()
abs_counts.columns = ['PAT_ABS', 'pacients']

# Separar els que tenen ABS dels que no
abs_com_abs = abs_counts[abs_counts['PAT_ABS'].notna()].copy()
abs_sense_abs = abs_counts[abs_counts['PAT_ABS'].isna()].copy()
total_pacients = len(df_pacients)

abs_com_abs['percentatge'] = (abs_com_abs['pacients'] / total_pacients * 100).round(2)
abs_sense_abs['percentatge'] = (abs_sense_abs['pacients'] / total_pacients * 100).round(2)

abs_com_abs = abs_com_abs.sort_values('pacients', ascending=False).reset_index(drop=True)

print(f"Nombre total d'ABS diferents: {len(abs_com_abs):,}")
print(f"Pacients sense ABS assignada: {abs_sense_abs['pacients'].sum():,} ({abs_sense_abs['percentatge'].sum():.1f}%)")
print()

# TOP 10
top10 = abs_com_abs.head(10).copy()
top10['percentatge_acumulat'] = top10['percentatge'].cumsum().round(2)
print("TOP 10 ABS AMB MÉS PACIENTS:")
print(top10[['PAT_ABS', 'pacients', 'percentatge', 'percentatge_acumulat']].to_string(index=False))
print()

# BOTTOM 10
bottom10 = abs_com_abs.tail(10).copy()
bottom10['percentatge'] = (bottom10['pacients'] / total_pacients * 100).round(4)
print("BOTTOM 10 ABS AMB MENYS PACIENTS:")
print(bottom10[['PAT_ABS', 'pacients', 'percentatge']].to_string(index=False))
print()

# Estadístiques globals
print("ESTADÍSTIQUES GLOBALS D'ABS")
print(f"Mitjana de pacients per ABS: {abs_com_abs['pacients'].mean():.1f}")
print(f"Mediana: {abs_com_abs['pacients'].median():.1f}")
print(f"Mínim: {abs_com_abs['pacients'].min():.0f}")
print(f"Màxim: {abs_com_abs['pacients'].max():.0f}")
print(f"Desviació: {abs_com_abs['pacients'].std():.1f}")

# Percentatge acumulat
abs_sorted = abs_com_abs.sort_values('pacients', ascending=False)
abs_sorted['percentatge_acumulat'] = (abs_sorted['pacients'].cumsum() / total_pacients * 100).round(2)
abs_50 = abs_sorted[abs_sorted['percentatge_acumulat'] <= 50]
abs_80 = abs_sorted[abs_sorted['percentatge_acumulat'] <= 80]
print(f"Les {len(abs_50)} primeres ABS acumulen el 50% dels pacients")
print(f"Les {len(abs_80)} primeres ABS acumulen el 80% dels pacients")

# Guardar taules
abs_com_abs.to_csv(f"{output_dir}/taules/abs_amb_pacients.csv", index=False, encoding="utf-8-sig")
abs_sense_abs.to_csv(f"{output_dir}/taules/abs_sense_pacients.csv", index=False, encoding="utf-8-sig")

# =========================
# FIGURES D'ABS
# =========================
print("\nGenerant figures d'ABS...")

# Top 20
top20 = abs_com_abs.head(20).copy()
top20['percentatge'] = (top20['pacients'] / total_pacients * 100).round(2)
plt.figure(figsize=(12, 6))
sns.barplot(data=top20, x='PAT_ABS', y='pacients', color='steelblue')
plt.title("Top 20 ABS amb major nombre de pacients (últim any)")
plt.xlabel("Codi ABS")
plt.ylabel("Nombre de pacients")
plt.xticks(rotation=90)
for i, (idx, row) in enumerate(top20.iterrows()):
    plt.text(i, row['pacients'] + 200, f"{row['percentatge']}%", ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(f"{output_dir}/plots/figura_abs_top20.png", dpi=300)
plt.close()

# Bottom 20
bottom20 = abs_com_abs.tail(20).copy()
bottom20 = bottom20.sort_values('pacients', ascending=True).reset_index(drop=True)
bottom20['percentatge'] = (bottom20['pacients'] / total_pacients * 100).round(4)
plt.figure(figsize=(12, 6))
sns.barplot(data=bottom20, x='PAT_ABS', y='pacients', color='steelblue')
plt.title("Bottom 20 ABS amb menor nombre de pacients (últim any)")
plt.xlabel("Codi ABS")
plt.ylabel("Nombre de pacients")
plt.xticks(rotation=90)
for i, (idx, row) in enumerate(bottom20.iterrows()):
    plt.text(i, row['pacients'] + 0.5, f"{row['percentatge']}%", ha='center', fontsize=8)
plt.tight_layout()
plt.savefig(f"{output_dir}/plots/figura_abs_bottom20.png", dpi=300)
plt.close()

# Scatter totes les ABS (escala log)
abs_com_abs['index'] = range(1, len(abs_com_abs)+1)
plt.figure(figsize=(14,6))
plt.scatter(abs_com_abs['index'], abs_com_abs['pacients'], alpha=0.5, s=15, color='steelblue')
plt.yscale('log')
plt.title("Distribució de pacients per ABS (escala logarítmica, últim any)")
plt.xlabel("ABS ordenades de més a menys pacients")
plt.ylabel("Nombre de pacients (escala log)")
plt.grid(True, alpha=0.3)
top5_indices = abs_com_abs.head(5)['index'].values
top5_valors = abs_com_abs.head(5)['pacients'].values
bottom5_abs = abs_com_abs.tail(5)
bottom5_indices = bottom5_abs['index'].values
bottom5_valors = bottom5_abs['pacients'].values
plt.scatter(top5_indices, top5_valors, color='red', s=50, label='Top 5 ABS')
plt.scatter(bottom5_indices, bottom5_valors, color='green', s=50, label='Bottom 5 ABS')
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/plots/figura_abs_totes_scatter.png", dpi=300)
plt.close()

# Histograma
plt.figure(figsize=(10,6))
plt.hist(abs_com_abs['pacients'], bins=50, edgecolor='black', alpha=0.7, color='steelblue')
plt.title("Distribució del nombre de pacients per ABS (últim any)")
plt.xlabel("Nombre de pacients per ABS")
plt.ylabel("Freqüència (nombre d'ABS)")
plt.yscale('log')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{output_dir}/plots/figura_abs_histograma.png", dpi=300)
plt.close()

# =========================
# 8. DISTRIBUCIÓ TEMPORAL (SENSE MODIFICAR)
# =========================
print("\n" + "="*60)
print("DISTRIBUCIÓ TEMPORAL (REGISTRES PACIENT-ANY)")
print("="*60)

any_counts = df.groupby('any').size().reset_index(name='registres')
any_counts['pacients'] = df.groupby('any')['PacientSAP'].nunique().values

print(any_counts.to_string(index=False))
any_counts.to_csv(f"{output_dir}/taules/distribucio_temporal.csv", index=False, encoding="utf-8-sig")

# =========================
# RESUM PER AL TEXT (5.2.2)
# =========================
print("\n" + "="*60)
print("RESUM PER A LA MEMÒRIA (APARTAT 5.2.2)")
print("="*60)
print(f"Registres inicials (pacient-any): {len(df):,}")
print(f"Registres després de neteja d'edat (<0 o >150): {len(df_net):,} (eliminats {len(edat_invalida)})")
print(f"Pacients únics (últim any): {total_pacients:,}")
print(f"Pacients sense ABS: {abs_sense_abs['pacients'].sum():,} ({abs_sense_abs['percentatge'].sum():.1f}%)")
print("Figures generades: edat_boxplot_global.png, edat_boxplot_per_any.png, edat_per_any_stats.csv, i les figures d'ABS")

print("\n" + "="*60)
print("ANÀLISI COMPLETADA")
print("="*60)