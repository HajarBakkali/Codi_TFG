"""
Classificació dels pacients segons guies KDIGO:
- Càlcul del FGe amb CKD-EPI 2021 (si no està disponible)
- Assignació de categories G (funció renal) i A (albuminúria)
- Determinació de te_erc (presència de CKD)
- Assignació del nivell de risc (KDIGO)
- Variables de risc cardiovascular (diabetis, LDL alt, HDL baix, colesterol total alt)
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# ==========================================
# CONNEXIÓ (CONTRASENYA OCULTA)
# ==========================================
engine = create_engine("mysql+pymysql://root:****@localhost/svrbi")

print("Carregant dades...")
df = pd.read_sql("SELECT * FROM ckd_pacient_any", engine)
print(f"Registres carregats: {len(df):,}")

# ==========================================
# FUNCIÓ PER CALCULAR EL FGe (CKD-EPI 2021)
# ==========================================
def calcular_fge(creatinina, edat, sexe):
    if pd.isna(creatinina) or pd.isna(edat) or pd.isna(sexe):
        return None
    if sexe == 'F':
        kappa = 0.7
        if creatinina <= kappa:
            fge = 142 * (creatinina / kappa) ** (-0.241) * (0.9938 ** edat) * 1.012
        else:
            fge = 142 * (creatinina / kappa) ** (-1.200) * (0.9938 ** edat) * 1.012
    elif sexe == 'M':
        kappa = 0.9
        if creatinina <= kappa:
            fge = 142 * (creatinina / kappa) ** (-0.302) * (0.9938 ** edat)
        else:
            fge = 142 * (creatinina / kappa) ** (-1.200) * (0.9938 ** edat)
    else:
        return None
    return round(fge, 2)

# ==========================================
# CALCULAR FGe NOMÉS ON FALTI
# ==========================================
print("\nCalculant FGe...")
df['fge_calculat'] = df['fge_ckd_epi'].copy()
mask = df['fge_ckd_epi'].isna() & df['creatinina'].notna() & df['sexe'].notna()
df.loc[mask, 'fge_calculat'] = df[mask].apply(
    lambda row: calcular_fge(row['creatinina'], row['edat'], row['sexe']), axis=1
)

# ==========================================
# CATEGORIA G (FUNCIÓ RENAL)
# ==========================================
def cat_g(fge):
    if pd.isna(fge): return None
    elif fge >= 90: return 'G1'
    elif fge >= 60: return 'G2'
    elif fge >= 45: return 'G3a'
    elif fge >= 30: return 'G3b'
    elif fge >= 15: return 'G4'
    else: return 'G5'

df['categoria_g'] = df['fge_calculat'].apply(cat_g)

# ==========================================
# CATEGORIA A (ALBUMINÚRIA)
# ==========================================
def cat_a(acr):
    if pd.isna(acr): return None
    elif acr < 30: return 'A1'
    elif acr <= 300: return 'A2'
    else: return 'A3'

df['categoria_a'] = df['quocient_albumina_creatinina'].apply(cat_a)

# ==========================================
# TÉ ERC? (CRITERI KDIGO)
# ==========================================
def te_erc(g, a):
    if pd.isna(g) and pd.isna(a): return None
    if g in ['G3a', 'G3b', 'G4', 'G5']: return True
    if a in ['A2', 'A3']: return True
    return False

df['te_erc'] = df.apply(lambda row: te_erc(row['categoria_g'], row['categoria_a']), axis=1)

# ==========================================
# NIVELL DE RISC (MAPA DE CALOR KDIGO)
# ==========================================
def nivell_risc(g, a):
    if pd.isna(g) or pd.isna(a): return None
    if g in ['G1', 'G2']:
        if a == 'A1': return 'Risc baix'
        elif a == 'A2': return 'Risc moderat'
        else: return 'Risc alt'
    elif g == 'G3a':
        if a == 'A1': return 'Risc moderat'
        elif a == 'A2': return 'Risc alt'
        else: return 'Risc molt alt'
    else:
        return 'Risc molt alt'

df['nivell_risc'] = df.apply(lambda row: nivell_risc(row['categoria_g'], row['categoria_a']), axis=1)

# ==========================================
# RISC CARDIOVASCULAR
# ==========================================
df['te_diabetis'] = df['hba1c'].apply(lambda x: x >= 6.5 if pd.notna(x) else None)
df['ldl_alt'] = df['colesterol_ldl'].apply(lambda x: x >= 100 if pd.notna(x) else None)

def hdl_baix(hdl, sexe):
    if pd.isna(hdl) or pd.isna(sexe): return None
    return hdl < 50 if sexe == 'F' else hdl < 40

df['hdl_baix'] = df.apply(lambda row: hdl_baix(row['colesterol_hdl'], row['sexe']), axis=1)
df['colesterol_total_alt'] = df['colesterol_total'].apply(lambda x: x > 200 if pd.notna(x) else None)

# ==========================================
# GUARDAR TAULA (REEMPLAÇANT)
# ==========================================
print("\nGuardant taula (això trigarà 1-2 minuts)...")
df.to_sql('ckd_pacient_any', engine, if_exists='replace', index=False)
print(" Taula actualitzada correctament!")

# ==========================================
# RESUMS
# ==========================================
print("\n" + "="*60)
print("RESUMS FINALS")
print("="*60)
print("\n--- Categoria G ---")
print(df['categoria_g'].value_counts(dropna=False).sort_index().to_string())
print("\n--- Categoria A ---")
print(df['categoria_a'].value_counts(dropna=False).sort_index().to_string())
print("\n--- ERC ---")
print(f"Amb ERC: {df['te_erc'].sum():,} ({df['te_erc'].sum()/len(df)*100:.1f}%)")
print("\n--- Nivell risc ---")
print(df['nivell_risc'].value_counts(dropna=False).to_string())