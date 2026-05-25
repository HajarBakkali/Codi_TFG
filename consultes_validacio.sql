-- =====================================================
-- CONSULTES SQL: Dashboard Malaltia Renal Crònica 
-- =====================================================

-- 1. Volum total de registres analítics (taula original)
SELECT COUNT(*) AS total_registres
FROM tab_ics_nefro_ckd_abs_ano;
-- Resultat: 9.387.238

-- 2. Nombre de pacients únics (PacientSAP)
SELECT COUNT(DISTINCT PacientSAP) AS total_pacients
FROM tab_ics_nefro_ckd_abs_ano
WHERE PacientSAP IS NOT NULL AND PacientSAP != '';
-- Resultat: 529.197

-- 3. Volum de registres de la taula de població de referència
SELECT COUNT(*) AS total_registres_poblacio
FROM tab_cs_poblacio_ref_001;
-- Resultat: 58.209

-- 4. Distribució de pacients per any (abans de neteja)
SELECT any, COUNT(DISTINCT PacientSAP) AS pacients
FROM ckd_pacient_any
GROUP BY any
ORDER BY any;

-- 5. Registres amb edat invàlida (<0 o >150)
SELECT COUNT(*) AS registres_invalids
FROM ckd_pacient_any
WHERE edat < 0 OR edat > 150;

-- 6. Pacients amb edat invàlida (mostrar valors)
SELECT DISTINCT PacientSAP, edat
FROM ckd_pacient_any
WHERE edat < 0 OR edat > 150;

-- 7. Valors negatius de creatinina
SELECT COUNT(*) AS creatinina_negativa
FROM ckd_pacient_any
WHERE creatinina < 0;

-- 8. Valors negatius d'ACR
SELECT COUNT(*) AS acr_negatiu
FROM ckd_pacient_any
WHERE quocient_albumina_creatinina < 0;

-- 9. Valors d'ACR > 5000 (abans de fixar límit)
SELECT COUNT(*) AS acr_molt_alt
FROM ckd_pacient_any
WHERE quocient_albumina_creatinina > 5000;

-- 10. Registres sense FGe ni creatinina (eliminats)
SELECT COUNT(*) AS sense_dades_renals
FROM ckd_pacient_any
WHERE fge_ckd_epi IS NULL AND creatinina IS NULL;

-- 11. Registres amb FGe > 400 (outlier detectat)
SELECT COUNT(*) AS fge_molt_alt
FROM ckd_pacient_any
WHERE fge_ckd_epi > 400;

-- 12. Valors extrems de colesterol total
SELECT MIN(colesterol_total) AS min_col, MAX(colesterol_total) AS max_col
FROM ckd_pacient_any;

-- 13. Distribució de pacients per sexe (únics)
SELECT sexe, COUNT(DISTINCT PacientSAP) AS pacients
FROM ckd_pacient_any
WHERE sexe IN ('F','M')
GROUP BY sexe;

-- 14. Top 10 ABS amb més pacients
SELECT PAT_ABS, COUNT(DISTINCT PacientSAP) AS pacients
FROM ckd_pacient_any
WHERE PAT_ABS IS NOT NULL
GROUP BY PAT_ABS
ORDER BY pacients DESC
LIMIT 10;

-- 15. Pacients sense ABS assignada
SELECT COUNT(DISTINCT PacientSAP) AS sense_abs
FROM ckd_pacient_any
WHERE PAT_ABS IS NULL;

-- 16. Distribució anual de registres després de neteja (taula final)
SELECT any, COUNT(*) AS registres, COUNT(DISTINCT PacientSAP) AS pacients
FROM ckd_pacient_any
GROUP BY any
ORDER BY any;

-- 17. Estructura de la taula de població
DESCRIBE tab_cs_poblacio_ref_001;

-- 18. Anys disponibles a la taula de població
SELECT DISTINCT any FROM tab_cs_poblacio_ref_001 ORDER BY any;

-- 19. ABS amb les seves AGAs (per a la dimensió)
SELECT DISTINCT abs_codi, AGACodi, AGADescripció
FROM tab_cs_poblacio_ref_001
ORDER BY AGACodi, abs_codi;

-- 20. Pacients per AGA (aproximació, unint per codi d'ABS)
SELECT t2.AGADescripció, COUNT(DISTINCT t1.PacientSAP) AS pacients
FROM ckd_pacient_any t1
JOIN tab_cs_poblacio_ref_001 t2 ON t1.PAT_ABS = t2.abs_codi
WHERE t1.PAT_ABS IS NOT NULL
GROUP BY t2.AGADescripció
ORDER BY pacients DESC;
