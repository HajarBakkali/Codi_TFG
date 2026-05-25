# Codi del TFG: Dashboard per al seguiment de la malaltia renal crònica (CKD) a Girona

Aquest repositori conté els scripts utilitzats per al tractament, neteja, anàlisi i modelatge de dades del Treball Final de Grau d'Enginyeria Biomèdica.

## Estructura del repositori

- `neteja_de_dades.py`: Neteja inicial i detecció de valors anòmals.
- `classificacio_ckd.py`: Classificació dels pacients segons criteris KDIGO.
- `analisis_variables_demografiques_temporals.py`: Anàlisi de variables demogràfiques (edat, sexe, ABS) i temporals.
- `analisi_completa_descriptiva_despres_neteja.py`: Estadístics descriptius finals.
- `analisis_analitiques.py`: Anàlisi de variables analítiques (creatinina, FGe, ACR, colesterol, HbA1c).

Les dades originals no es comparteixen per raons de confidencialitat. Aquests scripts parteixen de la taula agregada `ckd_pacient_any` (no inclosa) i generen els resultats que es mostren a la memòria.

## Requeriments

- Python 3.9+
- Llibreries: pandas, matplotlib, seaborn, sqlalchemy, pymysql

Per instal·lar les dependències:

```bash
pip install pandas matplotlib seaborn sqlalchemy pymysql
