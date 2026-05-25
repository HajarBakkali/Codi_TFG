"""
Neteja inicial de la taula ckd_pacient_any:
- Filtre d'edat (16-150)
- Filtre de sexe (només F i M)
- Neteja de valors negatius i límits per a creatinina i ACR
- Eliminació de registres sense FGe ni creatinina
- Sobreescriptura de la taula neta a MariaDB
"""

import os
import pandas as pd
from sqlalchemy import create_engine

# =========================
# CONNEXIÓ (CONTRASENYA OCULTA)
# =========================
engine = create_engine("mysql+pymysql://root:****@localhost/svrbi")

print("Carregant dades...")
df = pd.read_sql("SELECT * FROM ckd_pacient_any", engine)

total_inicial = len(df)
print(f"Registres totals (pacient-any): {total_inicial:,}")
print(f"Pacients únics inicials: {df['PacientSAP'].nunique():,}")
print()

# =========================
# APLICACIÓ DELS FILTRES DE NETEGES 
# =========================

print("="*60)
print("APLICANT FILTRES DE NETEGES")
print("="*60)

# 1. Filtrar edat (>=16 i <=150)
df = df[(df['edat'] >= 16) & (df['edat'] <= 150)].copy()
print(f"1. Edat >=16 i <=150: {len(df):,} registres (eliminats {total_inicial - len(df):,})")

# 2. Filtrar sexe (només F i M)
df = df[df['sexe'].isin(['F', 'M'])].copy()
print(f"2. Sexe F/M: {len(df):,} registres")

# 3. Netejar creatinina: valors <=0 -> NULL
creat_negatius = (df['creatinina'] <= 0).sum()
df.loc[df['creatinina'] <= 0, 'creatinina'] = None
print(f"3. Creatinina <=0: {creat_negatius:,} registres convertits a NULL")

# 4. Netejar ACR: valors negatius -> NULL, valors >5000 -> 5000
acr_negatius = (df['quocient_albumina_creatinina'] < 0).sum()
acr_grans = (df['quocient_albumina_creatinina'] > 5000).sum()
df.loc[df['quocient_albumina_creatinina'] < 0, 'quocient_albumina_creatinina'] = None
df.loc[df['quocient_albumina_creatinina'] > 5000, 'quocient_albumina_creatinina'] = 5000
print(f"4. ACR corregits: {acr_negatius:,} negatius -> NULL, {acr_grans:,} >5000 -> 5000")

# 5. Eliminar registres sense FGe ni creatinina
sense_dades = df[(df['fge_ckd_epi'].isna()) & (df['creatinina'].isna())].shape[0]
df = df[(df['fge_ckd_epi'].notna()) | (df['creatinina'].notna())].copy()
print(f"5. Registres sense FGe ni creatinina: {sense_dades:,} eliminats")

# =========================
# SOBRESCRIURE LA TAULA ORIGINAL
# =========================
print("\n" + "="*60)
print("SOBRESCRIVINT LA TAULA ORIGINAL A MARIADB")
print("="*60)

# Substituir la taula original per la versió neta
df.to_sql('ckd_pacient_any', engine, if_exists='replace', index=False)
print(f"Taula 'ckd_pacient_any' actualitzada a MariaDB amb {len(df):,} registres")

# =========================
# RESULTAT FINAL
# =========================
print("\n" + "="*60)
print("RESULTAT FINAL")
print("="*60)
print(f"Registres finals: {len(df):,}")
print(f"Pacients únics finals: {df['PacientSAP'].nunique():,}")
print(f"Percentatge de registres conservats: {len(df)/total_inicial*100:.2f}%")

# =========================
# COMPOSICIÓ DE LA MOSTRA FINAL
# =========================
print("\n" + "="*60)
print("COMPOSICIÓ DE LA MOSTRA FINAL")
print("="*60)
amb_fge = df['fge_ckd_epi'].notna().sum()
sense_fge_amb_creat = df[(df['fge_ckd_epi'].isna()) & (df['creatinina'].notna())].shape[0]
print(f"Registres amb FGe directe: {amb_fge:,}")
print(f"Registres sense FGe però amb creatinina (es pot calcular): {sense_fge_amb_creat:,}")

# =========================
# ESTADÍSTIQUES FINALS PER ANY
# =========================
print("\n" + "="*60)
print("ESTADÍSTIQUES FINALS PER ANY")
print("="*60)
any_stats = df.groupby('any').size().reset_index(name='registres')
any_stats['pacients'] = df.groupby('any')['PacientSAP'].nunique().values
print(any_stats.to_string(index=False))