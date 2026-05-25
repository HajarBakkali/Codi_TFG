# Codi del TFG: Dashboard per al seguiment de la malaltia renal crònica (CKD) a Girona

Aquest repositori conté els scripts utilitzats per al tractament, neteja, anàlisi i modelatge de dades del Treball Final de Grau d'Enginyeria Biomèdica.

## Estructura del repositori

- `neteja_de_dades.py`: Neteja inicial i detecció de valors anòmals.
- `classificacio_ckd.py`: Classificació dels pacients segons criteris KDIGO.
- `analisis_variables_demografiques_temporals.py`: Anàlisi de variables demogràfiques (edat, sexe, ABS) i temporals.
- `analisi_completa_descriptiva_despres_neteja.py`: Estadístics descriptius finals.
- `analisis_analitiques.py`: Anàlisi de variables analítiques (creatinina, FGe, ACR, colesterol, HbA1c).
- `consultes_validacio.sql`: Consultes SQL utilitzades per a la validació de dades (volums, valors nuls, outliers, distribucions).
- `outputs/`: Carpeta que conté tots els gràfics (PNG) i taules (CSV) generats pels scripts, organitzats per subcarpetes.

> **Nota**: Les dades originals no es comparteixen per raons de confidencialitat. Els scripts treballen sobre la taula agregada `ckd_pacient_any` (no inclosa) que es va generar a partir de les dades del laboratori de l’Hospital Trueta.

## Requeriments

- Python 3.9 o superior
- Llibreries necessàries:
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `sqlalchemy`
  - `pymysql`

Per instal·lar totes les dependències en un sol pas:

```bash
pip install pandas matplotlib seaborn sqlalchemy pymysql
