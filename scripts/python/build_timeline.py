"""
HDMF Timeline - simple version
Group A (existing): COL(8) PER(7) ECU(8) CHL(3) = 26 waves
Group B (new):      DOM(8) ARG(7) PRY(8) URY(7) CRI(8) PAN(7) = 45 waves
Grand total: 71 waves | 6-10 Abril 2026
"""
import os
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HDMF_Timeline_Apr6_10.xlsx')

DARK  = '2E2E2E'
WHITE = 'FFFFFF'
HDR_BG  = '2E2E2E'
SEC_BG  = 'E8E8E8'
GANTT   = '2E2E2E'
DONE_BG = 'EBEBEB'
LIGHT   = 'F5F5F5'

def fill(h): return PatternFill('solid', fgColor=h)
def bd():
    s = Side(style='thin', color='CCCCCC')
    return Border(left=s, right=s, top=s, bottom=s)
def font(bold=False, size=9, color=DARK, italic=False):
    return Font(bold=bold, size=size, color=color, italic=italic, name='Calibri')
def aln(h='center', v='center', wrap=True):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

DAY_COLS = ['Lun 6', 'Mar 7', 'Mie 8', 'Jue 9', 'Vie 10']

# ═══════════════════════════════════════════════════════════════════════════════
# GROUP A — existing countries
# ═══════════════════════════════════════════════════════════════════════════════
TASKS_A = [
('SEC','YA COMPLETADO', None, None, 'SEC', set(), ''),
('', 'COL 2025t3',                        'COL','2025t3', 'Hecho',   {1}, 'armo/COL/COL_2025t3_BID.dta'),
('', 'COL 2024t3  (re-run path)',          'COL','2024t3', 'Hecho',   {1}, 'Ejecutar dia 1 para actualizar carpeta output'),
('', 'ECU 2025m12',                       'ECU','2025m12','Hecho',   {1}, 'armo/ECU/ECU_2025m12_BID.dta'),
('', 'PER 2024a',                         'PER','2024a',  'Hecho',   {1}, 'armo/PER/PER_2024a_BID.dta'),
('', 'CHL 2024a',                         'CHL','2024a',  'Hecho',   {1}, 'armo/CHL/CHL_2024a_BID.dta'),

('SEC','DIA 1  |  Lun 6 Abr  |  Setup + Descargas + Scripts disponibles', None,None,'SEC',set(),''),
(1,  'Auditoria de datos y scope',                  'TODOS','--',    'Setup',   {1}, 'Listar ondas faltantes por pais'),
(2,  'Descarga COL GEIH 2018-2022  (DANE)',          'COL', '18-22', 'Descarga',{1}, 'dane.gov.co/microdatos. NOTA: 2022 cambia marco (2005->2018)'),
(3,  'Descarga PER ENAHO 2018-2023  (INEI)',         'PER', '18-23', 'Descarga',{1}, 'proyectos.inei.gob.pe/microdatos. Modulos 200+500 por ano'),
(4,  'Descarga ECU ENEMDU dic 2018-2023  (INEC)',    'ECU', '18-23', 'Descarga',{1}, 'ecuadorencifras.gob.ec. Diciembre = cobertura nacional'),
(5,  'Descarga CHL CASEN 2020+2022  (MDS)',          'CHL', '20+22', 'Descarga',{1}, 'Solo existen 2020 y 2022. CASEN 2019 cancelada. CASEN es bienal'),
(6,  'COL 2024t3  re-run (path actualizado)',        'COL', '2024t3','Ejecutar', {1}, 'COL_2024t3_variablesBID_local.do -> armo/COL/'),
(7,  'COL 2023t3  ejecutar script existente',        'COL', '2023t3','Ejecutar', {1}, 'COL_2023t3_variablesBID.do -> armo/COL/'),
(8,  'ECU 2024m12  descomprimir + ejecutar',         'ECU', '2024m12','Ejecutar',{1}, 'Descomprimir zip -> ECU_2024m12_variablesBID.do -> armo/ECU/'),

('SEC','DIA 2  |  Mar 7 Abr  |  Colombia 2018-2022 + Indicadores COL', None,None,'SEC',set(),''),
(9,  'COL 2022t3  dict.check + clonar + run',       'COL','2022t3','Clonar',{2}, 'CRITICO: primer ano marco 2018. Verificar p3373, p3042, oci/dsi'),
(10, 'COL 2021t3  dict.check + clonar + run',       'COL','2021t3','Clonar',{2}, 'Marco 2005 (ultimo). Clonar desde 2022t3'),
(11, 'COL 2020t3  dict.check + clonar + run',       'COL','2020t3','Clonar',{2}, 'COVID: muestra reducida. Verificar expansion fex_c18'),
(12, 'COL 2019t3  dict.check + clonar + run',       'COL','2019t3','Clonar',{2}, 'Clonar desde 2020t3'),
(13, 'COL 2018t3  dict.check + clonar + run',       'COL','2018t3','Clonar',{2}, 'Primer ano scope. Verificar p3373 disponible desde 2018'),
(14, 'Indicadores COL 2018-2025  (Python)',          'COL','--',    'Indic.',{2}, 'Ejecutar hdmf_2.py. Verificar tendencias empleo/migracion COL'),

('SEC','DIA 3  |  Mie 8 Abr  |  Peru 2018-2023 + Indicadores COL+PER', None,None,'SEC',set(),''),
(15, 'PER 2023a  dict.check + clonar + run',        'PER','2023a','Clonar',{3}, 'Clonar desde PER_2024a. Modulos 200+500 mergeados'),
(16, 'PER 2022a  dict.check + clonar + run',        'PER','2022a','Clonar',{3}, 'Clonar desde 2023a'),
(17, 'PER 2021a  dict.check + clonar + run',        'PER','2021a','Clonar',{3}, 'Verificar cambios post-COVID en empleo'),
(18, 'PER 2020a  dict.check + clonar + run',        'PER','2020a','Clonar',{3}, 'COVID: revision ytot_ci. Muestra parcial'),
(19, 'PER 2019a  dict.check + clonar + run',        'PER','2019a','Clonar',{3}, 'Clonar desde 2020a'),
(20, 'PER 2018a  dict.check + clonar + run',        'PER','2018a','Clonar',{3}, 'Primer ano PER. Verificar migrante_ci disponible'),
(21, 'Indicadores COL+PER 2018-2025  (Python)',     'CROSS','--',  'Indic.',{3}, 'Revisar empleo, educacion, formalizacion. Tendencias 2018-2025'),

('SEC','DIA 4  |  Jue 9 Abr  |  Ecuador 2018-2023 + Chile 2020+2022 + Indicadores', None,None,'SEC',set(),''),
(22, 'ECU 2023m12  dict.check + clonar + run',     'ECU','2023m12','Clonar',{4}, 'Clonar desde ECU_2025m12. Verificar var migracion'),
(23, 'ECU 2022m12  dict.check + clonar + run',     'ECU','2022m12','Clonar',{4}, 'Clonar desde 2023m12'),
(24, 'ECU 2021m12  dict.check + clonar + run',     'ECU','2021m12','Clonar',{4}, 'Verificar cambios INEC post-pandemia'),
(25, 'ECU 2020m12  dict.check + clonar + run',     'ECU','2020m12','Clonar',{4}, 'COVID: ajuste metodologico INEC. Verificar pesos'),
(26, 'CHL 2022a   dict.check + clonar + run',      'CHL','2022a',  'Clonar',{4}, 'Clonar desde CHL_2024. CASEN bienal: onda previa a 2024'),
(27, 'CHL 2020a   dict.check + clonar + run',      'CHL','2020a',  'Clonar',{4}, 'CASEN en Pandemia. Muestra ajustada. No existe CASEN 2018 ni 2019'),
(28, 'Indicadores COL+PER+ECU+CHL  (Python)',      'CROSS','--',   'Indic.',{4}, 'Ejecutar hdmf_2.py. Revisar population_origin, labor, education'),

('SEC','DIA 5  |  Vie 10 Abr  |  ECU 2018-2019 + Validacion + Indicadores finales + QC', None,None,'SEC',set(),''),
(29, 'ECU 2019m12  dict.check + clonar + run',    'ECU','2019m12','Clonar', {5}, 'Clonar desde 2020m12'),
(30, 'ECU 2018m12  dict.check + clonar + run',    'ECU','2018m12','Clonar', {5}, 'Primer ano ECU. Venezolanos llegando masivamente 2018-2019'),
(31, 'Validacion global  (todos los BID.dta)',     'TODOS','--',   'Validar',{5}, 'Agente validator: rangos, missings<30%, binary (0/1/.), factor_ci>0'),
(32, 'Indicadores finales  hdmf_2.py completo',    'TODOS','--',   'Indic.', {5}, 'Verificar pais_c.value_counts(). hdmf_indicators.xlsx + figuras generados'),
(33, 'Indicadores laborales: empleo, desempleo',   'TODOS','--',   'Indic.', {5}, 'Revisar labor_status_pivot. Saltos 2020 esperados (COVID)'),
(34, 'Indicadores de formalizacion (LAC)',          'TODOS','--',   'Indic.', {5}, 'formality_pivot + contract_type. USA excluida. Tendencia 2018-2025'),
(35, 'Indicadores educativos: nivel + anos',        'TODOS','--',   'Indic.', {5}, 'edu_distribution_pivot + edu_years'),
(36, 'Indicadores de poblacion y origen',           'TODOS','--',   'Indic.', {5}, 'top_mig_countries. Venezuela como principal origen en COL/PER/ECU'),
(37, 'QC + documentacion final',                    'TODOS','--',   'QC',     {5}, 'Revisar figuras. Actualizar inputs_summary.md. Git commit'),
]

# ═══════════════════════════════════════════════════════════════════════════════
# GROUP B — new countries
# DOM=8 | ARG=7 | PRY=8 | URY=7 | CRI=8 | PAN=7 = 45 waves
# All new surveys -> need survey_mapper + stata_generator first, then clone
# ═══════════════════════════════════════════════════════════════════════════════
TASKS_B = [
('SEC','DIA 1  |  Lun 6 Abr  |  Setup + Descargas paralelas + Metadata', None,None,'SEC',set(),''),
(1,  'Auditoria: scope y portales de microdatos por pais',   'TODOS','--',   'Setup',   {1}, 'Confirmar portales: BCRD (DOM), INDEC (ARG), INE (PRY), INE (URY), INEC (CRI), INEC Panama (PAN)'),
(2,  'Descarga DOM ENCFT 2018-2025  (BCRD)',                  'DOM', '18-25', 'Descarga',{1}, 'bancentral.gov.do -- microdata por solicitud formal a OAI. Trimestral; usar t3'),
(3,  'Descarga ARG EPH 2018-2024  (INDEC)',                   'ARG', '18-24', 'Descarga',{1}, 'indec.gob.ar -> FTP microdata. Trimestral; usar t3. CH15 = lugar nacimiento'),
(4,  'Descarga PRY EPHC 2018-2025  (INE)',                    'PRY', '18-25', 'Descarga',{1}, 'ine.gov.py/microdatos. Trimestral; usar t3. Verificar var migracion en DDI'),
(5,  'Descarga URY ECH 2018-2024  (INE Uruguay)',             'URY', '18-24', 'Descarga',{1}, 'gub.uy/ine -> ANDA catalog. Anual. Tiene var migrante + pais nacimiento'),
(6,  'Descarga CRI ENAHO 2018-2025  (INEC)',                  'CRI', '18-25', 'Descarga',{1}, 'sistemas.inec.cr/pad5. Anual (julio). Tiene condicion migratoria'),
(7,  'Descarga PAN EML 2018-2024  (INEC Panama / ILO)',       'PAN', '18-24', 'Descarga',{1}, 'inec.gob.pa / ILO surveyLib. Anual. Verificar var migracion en DDI -- posible ausencia'),
(8,  'Preparar metadata templates (6 paises)',                 'TODOS','--',  'Setup',   {1}, 'Llenar harmonization_System/inputs/[ISO]_[PERIOD]_metadata.md para cada pais'),

('SEC','DIA 2  |  Mar 7 Abr  |  DOM + ARG: nuevos scripts + clones', None,None,'SEC',set(),''),
(9,  'DOM 2025t3  survey_mapper + stata_generator (NUEVO)',  'DOM','2025t3','Nuevo',  {2}, 'Pegar agents/survey_mapper.md -> map_labor/demographics/migration/income. Generar COL_2025t3_variablesBID.do equivalente para DOM'),
(10, 'DOM 2024t3  dict.check + clonar + run',               'DOM','2024t3','Clonar', {2}, 'Clonar desde 2025t3. COVID t2-2020/t1-2021: modo telefono, datos disponibles con caveat'),
(11, 'DOM 2023t3 a 2018t3  (6 clones)',                     'DOM','23-18', 'Clonar', {2}, '6 clones encadenados. Verificar var migracion en cada onda (ENCFT reemplaza ENFT desde 2017)'),
(12, 'ARG 2024t3  survey_mapper + stata_generator (NUEVO)', 'ARG','2024t3','Nuevo',  {2}, 'CH15 = lugar nacimiento (1-5). ARG excluye zonas rurales -- documentar en metadata'),
(13, 'ARG 2023t3  dict.check + clonar + run',               'ARG','2023t3','Clonar', {2}, 'Clonar desde 2024t3. EPH tiene cambio metodologico acumulativo desde 2016'),
(14, 'ARG 2022t3 a 2018t3  (5 clones)',                     'ARG','22-18', 'Clonar', {2}, '5 clones. 2020t2: modo telefono (ASPO). Documentar con *CHANGED'),
(15, 'Indicadores DOM+ARG  (Python parcial)',               'CROSS','--',  'Indic.', {2}, 'Ejecutar hdmf_2.py con DOM+ARG. Verificar pais_c y tendencias empleo/migracion'),

('SEC','DIA 3  |  Mie 8 Abr  |  PRY + URY: nuevos scripts + clones', None,None,'SEC',set(),''),
(16, 'PRY 2025t3  survey_mapper + stata_generator (NUEVO)', 'PRY','2025t3','Nuevo',  {3}, 'EPHC continua desde 2017. Verificar lugar_nacimiento en DDI ANDA antes de mapear'),
(17, 'PRY 2024t3  dict.check + clonar + run',               'PRY','2024t3','Clonar', {3}, 'Clonar desde 2025t3'),
(18, 'PRY 2023t3 a 2018t3  (6 clones)',                     'PRY','23-18', 'Clonar', {3}, '6 clones. Sin gaps documentados. Verificar que migrante_ci disponible desde 2018'),
(19, 'URY 2024a   survey_mapper + stata_generator (NUEVO)', 'URY','2024a', 'Nuevo',  {3}, 'ECH anual. Tiene var migrante (no-migrante / uruguayo-retornado / extranjero) y pais nacimiento. Nota: N migrantes pequeno por ano -- considerar pooling 2-3 anos en analisis'),
(20, 'URY 2023a  dict.check + clonar + run',                'URY','2023a', 'Clonar', {3}, 'Clonar desde 2024a'),
(21, 'URY 2022a a 2018a  (5 clones)',                       'URY','22-18', 'Clonar', {3}, '5 clones. Sin gaps. ECH excluye viviendas colectivas -- puede subestimar migrantes recientes'),
(22, 'Indicadores PRY+URY  (Python parcial)',               'CROSS','--',  'Indic.', {3}, 'Ejecutar hdmf_2.py con PRY+URY. Verificar education, labor, formalizacion'),

('SEC','DIA 4  |  Jue 9 Abr  |  CRI + PAN: nuevos scripts + clones', None,None,'SEC',set(),''),
(23, 'CRI 2025a   survey_mapper + stata_generator (NUEVO)', 'CRI','2025a', 'Nuevo',  {4}, 'ENAHO anual (julio). Tiene condicion migratoria y lugar nacimiento. Fuente oficial extranjeros en CRI'),
(24, 'CRI 2024a  dict.check + clonar + run',                'CRI','2024a', 'Clonar', {4}, 'Clonar desde 2025a'),
(25, 'CRI 2023a a 2018a  (6 clones)',                       'CRI','23-18', 'Clonar', {4}, '6 clones. Sin gaps. 2020-2021: protocolos adaptados pero datos completos'),
(26, 'PAN 2024a   survey_mapper + stata_generator (NUEVO)', 'PAN','2024a', 'Nuevo',  {4}, 'EML anual. ADVERTENCIA: var migracion no confirmada en DDI publico. Verificar en ILO surveyLib antes de mapear. Si ausente: migrante_ci=. para todas las ondas'),
(27, 'PAN 2023a  dict.check + clonar + run',                'PAN','2023a', 'Clonar', {4}, 'Clonar desde 2024a. 2020: modo telefono (EMLT) -- documentar con *CHANGED'),
(28, 'PAN 2022a a 2018a  (5 clones)',                       'PAN','22-18', 'Clonar', {4}, '5 clones. Mes de referencia varia por ano (agosto/septiembre/octubre/abril). Documentar en metadata'),
(29, 'Indicadores CRI+PAN  (Python parcial)',               'CROSS','--',  'Indic.', {4}, 'Ejecutar hdmf_2.py con CRI+PAN. Revisar population_origin, labor, formalizacion'),

('SEC','DIA 5  |  Vie 10 Abr  |  Validacion + Indicadores finales + QC', None,None,'SEC',set(),''),
(30, 'Validacion global  (45 BID.dta nuevos)',              'TODOS','--',  'Validar',{5}, 'Agente validator: rangos, missings<30%, binary (0/1/.), factor_ci>0. Documentar anomalias'),
(31, 'Indicadores finales  hdmf_2.py completo (6 paises)', 'TODOS','--',  'Indic.', {5}, 'Ejecutar hdmf_2.py. Verificar pais_c.value_counts() incluye DOM/ARG/PRY/URY/CRI/PAN'),
(32, 'Indicadores laborales: empleo, desempleo, PEA',      'TODOS','--',  'Indic.', {5}, 'Revisar labor_status_pivot. Saltos 2020 esperados'),
(33, 'Indicadores formalizacion',                           'TODOS','--',  'Indic.', {5}, 'formality_pivot. Verificar DOM y PAN si formal_ci disponible'),
(34, 'Indicadores educativos',                              'TODOS','--',  'Indic.', {5}, 'edu_distribution_pivot + edu_years. Comparar migrantes vs nativos'),
(35, 'Indicadores poblacion y origen migrante',             'TODOS','--',  'Indic.', {5}, 'top_mig_countries por pais. CRI: nicaraguenses. URY: argentinos/brasileros. PAN: verificar'),
(36, 'QC + codebooks + documentacion final',                'TODOS','--',  'QC',     {5}, 'Revisar figuras. Generar harmonization_codebook por pais. Git commit todo'),
]

# ═══════════════════════════════════════════════════════════════════════════════
# INVENTORY GROUP A
# ═══════════════════════════════════════════════════════════════════════════════
INV_A = [
    ('COL',2018,'2018t3','Descargar','Clonar+Run',2,'Clonar 2019t3. Marco 2005. Verificar p3373'),
    ('COL',2019,'2019t3','Descargar','Clonar+Run',2,'Clonar 2020t3'),
    ('COL',2020,'2020t3','Descargar','Clonar+Run',2,'COVID: verificar expansion y oci/dsi'),
    ('COL',2021,'2021t3','Descargar','Clonar+Run',2,'Marco 2005 (ultimo). Clonar 2022t3'),
    ('COL',2022,'2022t3','Descargar','Clonar+Run',2,'CRITICO: cambio marco 2005->2018'),
    ('COL',2023,'2023t3','Disponible','Ejecutar',  1,'Script existe. Ejecutar dia 1'),
    ('COL',2024,'2024t3','Disponible','Re-run',    1,'Re-run para actualizar path'),
    ('COL',2025,'2025t3','Disponible','Hecho',     0,'armo/COL/COL_2025t3_BID.dta'),
    ('PER',2018,'2018a', 'Descargar','Clonar+Run',3,'Modulos 200+500. Verificar migrante_ci'),
    ('PER',2019,'2019a', 'Descargar','Clonar+Run',3,'Clonar 2020a'),
    ('PER',2020,'2020a', 'Descargar','Clonar+Run',3,'COVID: revision ytot_ci'),
    ('PER',2021,'2021a', 'Descargar','Clonar+Run',3,'Clonar 2022a'),
    ('PER',2022,'2022a', 'Descargar','Clonar+Run',3,'Clonar 2023a'),
    ('PER',2023,'2023a', 'Descargar','Clonar+Run',3,'Clonar 2024a'),
    ('PER',2024,'2024a', 'Disponible','Hecho',     0,'armo/PER/PER_2024a_BID.dta'),
    ('ECU',2018,'2018m12','Descargar','Clonar+Run',5,'Clonar 2019m12'),
    ('ECU',2019,'2019m12','Descargar','Clonar+Run',5,'Clonar 2020m12'),
    ('ECU',2020,'2020m12','Descargar','Clonar+Run',4,'COVID: ajuste metodologico INEC'),
    ('ECU',2021,'2021m12','Descargar','Clonar+Run',4,'Clonar 2022m12'),
    ('ECU',2022,'2022m12','Descargar','Clonar+Run',4,'Clonar 2023m12'),
    ('ECU',2023,'2023m12','Descargar','Clonar+Run',4,'Clonar 2025m12'),
    ('ECU',2024,'2024m12','Disponible (zip)','Ejecutar',1,'Descomprimir + script existente'),
    ('ECU',2025,'2025m12','Disponible','Hecho',    0,'armo/ECU/ECU_2025m12_BID.dta'),
    ('CHL',2018,'-- no existe --','--','--',       0,'CASEN es bienal. No hay datos 2018'),
    ('CHL',2019,'-- cancelada --','--','--',       0,'CASEN 2019 cancelada por estallido social'),
    ('CHL',2020,'2020a','Descargar','Clonar+Run',  4,'CASEN en Pandemia. Muestra ajustada'),
    ('CHL',2021,'-- no existe --','--','--',       0,'CASEN bienal. No hay datos 2021'),
    ('CHL',2022,'2022a','Descargar','Clonar+Run',  4,'Clonar desde CHL_2024'),
    ('CHL',2023,'-- no existe --','--','--',       0,'CASEN bienal. No hay datos 2023'),
    ('CHL',2024,'2024a','Disponible','Hecho',      0,'armo/CHL/CHL_2024a_BID.dta'),
    ('CHL',2025,'-- no existe --','--','--',       0,'CASEN bienal. Siguiente seria 2026'),
]

# ═══════════════════════════════════════════════════════════════════════════════
# INVENTORY GROUP B
# ═══════════════════════════════════════════════════════════════════════════════
INV_B = [
    ('DOM',2018,'2018t3','Solicitar BCRD','Nuevo+Clonar',2,'ENCFT trimestral. Verificar var migracion -- no confirmada'),
    ('DOM',2019,'2019t3','Solicitar BCRD','Clonar+Run',  2,'Clonar 2020t3'),
    ('DOM',2020,'2020t3','Solicitar BCRD','Clonar+Run',  2,'COVID: t2-2020/t1-2021 modo telefono. Datos disponibles con caveat'),
    ('DOM',2021,'2021t3','Solicitar BCRD','Clonar+Run',  2,'Clonar 2022t3'),
    ('DOM',2022,'2022t3','Solicitar BCRD','Clonar+Run',  2,'Clonar 2023t3'),
    ('DOM',2023,'2023t3','Solicitar BCRD','Clonar+Run',  2,'Clonar 2024t3'),
    ('DOM',2024,'2024t3','Solicitar BCRD','Clonar+Run',  2,'Clonar 2025t3'),
    ('DOM',2025,'2025t3','Solicitar BCRD','Nuevo script',2,'Onda mas reciente. Crear script base con survey_mapper'),
    ('ARG',2018,'2018t3','Disponible INDEC','Clonar+Run',2,'Clonar 2019t3. ARG excluye zonas rurales'),
    ('ARG',2019,'2019t3','Disponible INDEC','Clonar+Run',2,'Clonar 2020t3'),
    ('ARG',2020,'2020t3','Disponible INDEC','Clonar+Run',2,'2020t2: modo telefono (ASPO). Documentar *CHANGED'),
    ('ARG',2021,'2021t3','Disponible INDEC','Clonar+Run',2,'Clonar 2022t3'),
    ('ARG',2022,'2022t3','Disponible INDEC','Clonar+Run',2,'Clonar 2023t3'),
    ('ARG',2023,'2023t3','Disponible INDEC','Clonar+Run',2,'Clonar 2024t3'),
    ('ARG',2024,'2024t3','Disponible INDEC','Nuevo script',2,'Onda mas reciente. CH15 = lugar nacimiento (1-5)'),
    ('PRY',2018,'2018t3','Disponible INE', 'Clonar+Run', 3,'Clonar 2019t3. Verificar migrante_ci en DDI ANDA'),
    ('PRY',2019,'2019t3','Disponible INE', 'Clonar+Run', 3,'Clonar 2020t3'),
    ('PRY',2020,'2020t3','Disponible INE', 'Clonar+Run', 3,'Sin gap documentado. Verificar ajustes COVID'),
    ('PRY',2021,'2021t3','Disponible INE', 'Clonar+Run', 3,'Clonar 2022t3'),
    ('PRY',2022,'2022t3','Disponible INE', 'Clonar+Run', 3,'Clonar 2023t3'),
    ('PRY',2023,'2023t3','Disponible INE', 'Clonar+Run', 3,'Clonar 2024t3'),
    ('PRY',2024,'2024t3','Disponible INE', 'Clonar+Run', 3,'Clonar 2025t3'),
    ('PRY',2025,'2025t3','Disponible INE', 'Nuevo script',3,'Onda mas reciente. Crear script base'),
    ('URY',2018,'2018a', 'Disponible INE', 'Clonar+Run', 3,'Clonar 2019a. N migrantes pequeno por ano'),
    ('URY',2019,'2019a', 'Disponible INE', 'Clonar+Run', 3,'Clonar 2020a'),
    ('URY',2020,'2020a', 'Disponible INE', 'Clonar+Run', 3,'Sin gap. ECH anual continua'),
    ('URY',2021,'2021a', 'Disponible INE', 'Clonar+Run', 3,'Clonar 2022a'),
    ('URY',2022,'2022a', 'Disponible INE', 'Clonar+Run', 3,'Clonar 2023a'),
    ('URY',2023,'2023a', 'Disponible INE', 'Clonar+Run', 3,'Clonar 2024a'),
    ('URY',2024,'2024a', 'Disponible INE', 'Nuevo script',3,'Onda mas reciente. Tiene migrante+pais_nacimiento'),
    ('CRI',2018,'2018a', 'Disponible INEC','Clonar+Run', 4,'Clonar 2019a'),
    ('CRI',2019,'2019a', 'Disponible INEC','Clonar+Run', 4,'Clonar 2020a'),
    ('CRI',2020,'2020a', 'Disponible INEC','Clonar+Run', 4,'Protocolos adaptados COVID. Datos completos'),
    ('CRI',2021,'2021a', 'Disponible INEC','Clonar+Run', 4,'Clonar 2022a'),
    ('CRI',2022,'2022a', 'Disponible INEC','Clonar+Run', 4,'Clonar 2023a'),
    ('CRI',2023,'2023a', 'Disponible INEC','Clonar+Run', 4,'Clonar 2024a'),
    ('CRI',2024,'2024a', 'Disponible INEC','Clonar+Run', 4,'Clonar 2025a'),
    ('CRI',2025,'2025a', 'Disponible INEC','Nuevo script',4,'Onda mas reciente. Julio 2025. Condicion migratoria incluida'),
    ('PAN',2018,'2018a', 'Disponible ILO', 'Clonar+Run', 4,'Clonar 2019a. Verificar migracion -- posiblemente ausente'),
    ('PAN',2019,'2019a', 'Disponible ILO', 'Clonar+Run', 4,'Clonar 2020a'),
    ('PAN',2020,'2020a', 'Disponible ILO', 'Clonar+Run', 4,'EMLT (telefono). Documentar cambio metodologico'),
    ('PAN',2021,'2021a', 'Disponible ILO', 'Clonar+Run', 4,'Clonar 2022a'),
    ('PAN',2022,'2022a', 'Disponible ILO', 'Clonar+Run', 4,'Clonar 2023a. Referencia: abril'),
    ('PAN',2023,'2023a', 'Disponible ILO', 'Clonar+Run', 4,'Clonar 2024a'),
    ('PAN',2024,'2024a', 'Disponible ILO', 'Nuevo script',4,'Onda mas reciente. Referencia: octubre 2024. Var migracion a verificar'),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════════
# (pais, iso3, survey, freq, period_code, most_recent, n_waves, mig_var, portal, notes)
SUMMARY = [
    # Group A
    ('Colombia',          'COL','GEIH',   'Trimestral','t3',  '2025t3', 8, 'Si',           'dane.gov.co/microdatos',             'Cambio marco metodologico 2022 (2005->2018). Hecho: 2025+2024 done.'),
    ('Peru',              'PER','ENAHO',  'Anual',     'a',   '2024a',  7, 'Si',           'proyectos.inei.gob.pe/microdatos',   'Modulos 200+500. Hecho: 2024 done. 2018-2023 pendientes.'),
    ('Ecuador',           'ECU','ENEMDU', 'Mensual',   'm12', '2025m12',8, 'Si',           'ecuadorencifras.gob.ec',             'Diciembre = cobertura nacional. Hecho: 2025+2024 done.'),
    ('Chile',             'CHL','CASEN',  'Bienal',    'a',   '2024a',  3, 'Si',           'observatorio.ministeriodesarrollosocial.gob.cl','Solo 2020, 2022, 2024. 2019 cancelada. 2018/2021/2023 no existen. Hecho: 2024 done.'),
    ('Rep. Dominicana',   'DOM','ENCFT',  'Trimestral','t3',  '2025t3', 8, 'No confirmada','bancentral.gov.do (solicitud OAI)',  'Microdata por solicitud formal al BCRD. Var migracion no confirmada en docs publicos.'),
    ('Argentina',         'ARG','EPH',    'Trimestral','t3',  '2024t3', 7, 'Si (CH15)',    'indec.gob.ar (FTP libre)',           'CH15 = lugar nacimiento. Excluye zonas rurales. 2020t2 modo telefono.'),
    ('Paraguay',          'PRY','EPHC',   'Trimestral','t3',  '2025t3', 8, 'Probable',     'ine.gov.py/microdatos',              'Verificar lugar_nacimiento en DDI ANDA antes de mapear. Sin gaps COVID.'),
    ('Uruguay',           'URY','ECH',    'Anual',     'a',   '2024a',  7, 'Si',           'gub.uy/ine + Anda5',                 'Tiene migrante + pais nacimiento. N migrantes pequeno por ano -- recomendar pooling.'),
    ('Costa Rica',        'CRI','ENAHO',  'Anual',     'a',   '2025a',  8, 'Si',           'sistemas.inec.cr/pad5',              'Tiene condicion migratoria. Fuente oficial de extranjeros en CRI.'),
    ('Panama',            'PAN','EML',    'Anual',     'a',   '2024a',  7, 'No confirmada','inec.gob.pa / ILO surveyLib',        'Var migracion no confirmada. 2020 modo telefono (EMLT). Mes referencia varia por ano.'),
]


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET BUILDER
# ═══════════════════════════════════════════════════════════════════════════════
wb = openpyxl.Workbook()

def write_timeline_sheet(ws, tasks, title, subtitle):
    """Render a Gantt timeline sheet."""
    for col, w in zip(['A','B','C','D','E','F','G','H','I','J','K'],
                      [4,  52,  7,   9,  11, 10,  10,  10, 10,  10, 55]):
        ws.column_dimensions[col].width = w

    ws.row_dimensions[1].height = 26
    ws.merge_cells('A1:K1')
    c = ws['A1']
    c.value = title
    c.font  = Font(bold=True, size=12, color=WHITE, name='Calibri')
    c.fill  = fill(HDR_BG); c.alignment = aln()

    ws.row_dimensions[2].height = 20
    ws.merge_cells('A2:K2')
    c = ws['A2']
    c.value = subtitle
    c.font  = Font(size=9, italic=True, color='555555', name='Calibri')
    c.fill  = fill(LIGHT); c.alignment = aln(h='left')

    ws.row_dimensions[3].height = 26
    for ci, h in enumerate(['#','Tarea','Pais','Onda','Tipo'] + DAY_COLS + ['Notas'], 1):
        c = ws.cell(row=3, column=ci)
        c.value = h
        c.font  = Font(bold=True, size=9, color=WHITE, name='Calibri')
        c.fill  = fill('555555'); c.alignment = aln(); c.border = bd()

    row = 4
    for task in tasks:
        tid, desc, country, wave, ttype, days_active, notes = task
        ws.row_dimensions[row].height = 18

        if ttype == 'SEC':
            ws.merge_cells(f'A{row}:K{row}')
            c = ws[f'A{row}']
            c.value = f'  {desc}'
            c.font  = Font(bold=True, size=9, color=DARK, name='Calibri')
            c.fill  = fill(SEC_BG); c.alignment = aln(h='left'); c.border = bd()
            row += 1; continue

        is_done = ttype == 'Hecho'
        row_bg  = DONE_BG if is_done else WHITE

        def wr(col_l, val, bld=False, clr=DARK, bg=row_bg, ha='center', it=False):
            c = ws[f'{col_l}{row}']
            c.value = val
            c.font  = Font(bold=bld, size=9, color=clr, italic=it, name='Calibri')
            c.fill  = fill(bg); c.alignment = aln(h=ha); c.border = bd()

        wr('A', str(tid) if tid != '' else '')
        wr('B', desc, ha='left', it=is_done, clr='888888' if is_done else DARK)
        wr('C', country or '--', bld=True)
        wr('D', wave or '--')
        wr('E', ttype, clr='888888' if is_done else DARK)

        for di, col_l in enumerate(['F','G','H','I','J'], 1):
            c = ws[f'{col_l}{row}']
            if di in days_active and not is_done:
                c.fill = fill(GANTT)
            elif di in days_active and is_done:
                c.fill = fill('BBBBBB')
            else:
                c.fill = fill(row_bg)
            c.value = ''; c.alignment = aln(); c.border = bd()

        wr('K', notes, ha='left', it=True, clr='555555')
        row += 1

    # Footer
    ws.row_dimensions[row].height = 16
    ws.merge_cells(f'A{row}:K{row}')
    c = ws[f'A{row}']
    c.value = footer_text(tasks)
    c.font  = Font(size=9, color='555555', italic=True, name='Calibri')
    c.fill  = fill(LIGHT); c.alignment = aln(h='left'); c.border = bd()
    ws.freeze_panes = 'B4'


def footer_text(tasks):
    types = [t[4] for t in tasks if t[4] != 'SEC']
    n_done  = types.count('Hecho')
    n_clone = types.count('Clonar')
    n_new   = types.count('Nuevo')
    n_run   = sum(1 for t in types if t in ('Ejecutar','Re-run'))
    n_ind   = types.count('Indic.')
    n_dl    = types.count('Descarga')
    n_val   = types.count('Validar')
    n_qc    = types.count('QC')
    return (f'  Hechos: {n_done}  |  Descargas paralelas: {n_dl}  |  Ejecutar: {n_run}  |  '
            f'Scripts nuevos: {n_new}  |  Clones: {n_clone}  |  '
            f'Indicadores Python: {n_ind}  |  Validacion: {n_val}  |  QC: {n_qc}')


def write_inventory_sheet(ws, inventory, title, note):
    for col, w in zip(['A','B','C','D','E','F','G'], [7,6,11,18,14,5,55]):
        ws.column_dimensions[col].width = w

    ws.row_dimensions[1].height = 26
    ws.merge_cells('A1:G1')
    c = ws['A1']; c.value = title
    c.font = Font(bold=True, size=12, color=WHITE, name='Calibri')
    c.fill = fill(HDR_BG); c.alignment = aln()

    ws.row_dimensions[2].height = 28
    ws.merge_cells('A2:G2')
    c = ws['A2']; c.value = note
    c.font = Font(size=9, italic=True, color='555555', name='Calibri')
    c.fill = fill(LIGHT)
    c.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
    c.border = bd()

    for ci, h in enumerate(['Pais','Ano','Onda','Raw','Accion','Dia','Notas'], 1):
        c = ws.cell(row=3, column=ci)
        c.value = h
        c.font  = Font(bold=True, size=9, color=WHITE, name='Calibri')
        c.fill  = fill('555555'); c.alignment = aln(); c.border = bd()

    for ri, row_data in enumerate(inventory, 4):
        pais, year, period, raw, action, day, notes = row_data
        ws.row_dimensions[ri].height = 16
        na     = '--' in str(period) or period == 'N/A'
        done   = action == 'Hecho'
        bg     = 'EEEEEE' if na else (DONE_BG if done else (LIGHT if ri % 2 == 0 else WHITE))
        clr_tx = 'AAAAAA' if na else DARK

        for ci, val in enumerate([pais, year, period, raw, action, day if day else '--', notes], 1):
            c = ws.cell(row=ri, column=ci)
            c.value = val if val != 0 else '--'
            c.font  = Font(size=9, color=clr_tx, italic=na, bold=(ci==1), name='Calibri')
            c.fill  = fill(bg)
            c.alignment = aln(h='left' if ci >= 4 else 'center')
            c.border = bd()

    ws.freeze_panes = 'A4'


# ── Sheet 1: Timeline Group A ─────────────────────────────────────────────────
ws1 = wb.active
ws1.title = 'Timeline A (COL PER ECU CHL)'
write_timeline_sheet(
    ws1, TASKS_A,
    'HDMF - Grupo A: COL(8) + PER(7) + ECU(8) + CHL(3) = 26 ondas | 6-10 Abril 2026',
    'Encuestas: COL GEIH t3 (2018-2025) | PER ENAHO anual (2018-2024) | ECU ENEMDU dic (2018-2025) | CHL CASEN bienal (2020, 2022, 2024 solamente -- 2019 cancelada)'
)

# ── Sheet 2: Timeline Group B ─────────────────────────────────────────────────
ws2 = wb.create_sheet('Timeline B (6 nuevos paises)')
write_timeline_sheet(
    ws2, TASKS_B,
    'HDMF - Grupo B: DOM(8) + ARG(7) + PRY(8) + URY(7) + CRI(8) + PAN(7) = 45 ondas | 6-10 Abril 2026',
    'Encuestas: DOM ENCFT t3 | ARG EPH t3 | PRY EPHC t3 | URY ECH anual | CRI ENAHO anual (julio) | PAN EML anual | Todos nuevos -> crear script con survey_mapper+stata_generator primero'
)

# ── Sheet 3: Inventario Group A ───────────────────────────────────────────────
ws3 = wb.create_sheet('Inventario - Grupo A')
write_inventory_sheet(
    ws3, INV_A,
    'Inventario ondas Grupo A | COL + PER + ECU + CHL | 2018-2025',
    'CHL CASEN bienal: solo existen 2020, 2022 y 2024 (2019 cancelada; 2018/2021/2023 no existen). '
    'COL GEIH: cambio de marco metodologico enero 2022 (2005->2018) -- dictionary check critico en onda 2022 vs 2021.'
)

# ── Sheet 4: Inventario Group B ───────────────────────────────────────────────
ws4 = wb.create_sheet('Inventario - Grupo B')
write_inventory_sheet(
    ws4, INV_B,
    'Inventario ondas Grupo B | DOM + ARG + PRY + URY + CRI + PAN | 2018-mas reciente',
    'DOM: microdata por solicitud formal al BCRD (no portal abierto). '
    'PAN y DOM: variable migracion no confirmada en DDI publico -- verificar antes de mapear. '
    'ARG: excluye zonas rurales. URY: N migrantes pequeno por ano, considerar pooling 2-3 anos.'
)

# ── Sheet 5: Summary ──────────────────────────────────────────────────────────
ws5 = wb.create_sheet('Resumen del Proyecto')

for col, w in zip(['A','B','C','D','E','F','G','H','I','J'],
                  [18,  7,  14,  13,  10,  11,  9,   13,  35, 55]):
    ws5.column_dimensions[col].width = w

ws5.row_dimensions[1].height = 30
ws5.merge_cells('A1:J1')
c = ws5['A1']
c.value = 'HDMF -- Resumen del Proyecto | 10 paises | 71 ondas | 2018-2025'
c.font  = Font(bold=True, size=14, color=WHITE, name='Calibri')
c.fill  = fill(HDR_BG); c.alignment = aln()

# Totals row
ws5.row_dimensions[2].height = 18
ws5.merge_cells('A2:J2')
c = ws5['A2']
c.value = ('  Grupo A (existentes): COL 8 ondas + PER 7 + ECU 8 + CHL 3 = 26 ondas     |     '
           'Grupo B (nuevos): DOM 8 + ARG 7 + PRY 8 + URY 7 + CRI 8 + PAN 7 = 45 ondas     |     '
           'TOTAL: 71 ondas en 10 paises')
c.font  = Font(bold=True, size=10, color=DARK, name='Calibri')
c.fill  = fill(LIGHT); c.alignment = aln(h='left'); c.border = bd()

# Section headers
def sec_row(ws, row_n, text):
    ws.row_dimensions[row_n].height = 18
    ws.merge_cells(f'A{row_n}:J{row_n}')
    c = ws.cell(row=row_n, column=1)
    c.value = f'  {text}'
    c.font  = Font(bold=True, size=9, color=DARK, name='Calibri')
    c.fill  = fill(SEC_BG); c.alignment = aln(h='left'); c.border = bd()

# Column headers
hdrs = ['Pais','ISO3','Encuesta','Frecuencia','Periodo','Mas reciente',
        'Ondas\n2018-hoy','Var. migracion','Portal oficial','Notas clave']
ws5.row_dimensions[3].height = 30
for ci, h in enumerate(hdrs, 1):
    c = ws5.cell(row=3, column=ci)
    c.value = h; c.font = Font(bold=True, size=9, color=WHITE, name='Calibri')
    c.fill  = fill('555555'); c.alignment = aln(); c.border = bd()

# Group A header
sec_row(ws5, 4, 'GRUPO A -- Paises con scripts existentes (armonizacion parcial en curso)')

# Group A rows
for ri, row_data in enumerate(SUMMARY[:4], 5):
    pais, iso3, survey, freq, period, recent, n_waves, mig, portal, notes = row_data
    ws5.row_dimensions[ri].height = 28
    bg = LIGHT if ri % 2 == 0 else WHITE
    vals = [pais, iso3, survey, freq, period, recent, n_waves, mig, portal, notes]
    for ci, val in enumerate(vals, 1):
        c = ws5.cell(row=ri, column=ci)
        c.value = val
        c.font  = Font(size=9, color=DARK, bold=(ci <= 2), name='Calibri')
        c.fill  = fill(bg)
        c.alignment = Alignment(horizontal='center' if ci <= 7 else 'left',
                                vertical='center', wrap_text=True)
        c.border = bd()

# Group B header
sec_row(ws5, 9, 'GRUPO B -- Paises nuevos (scripts por crear con survey_mapper + stata_generator)')

for ri, row_data in enumerate(SUMMARY[4:], 10):
    pais, iso3, survey, freq, period, recent, n_waves, mig, portal, notes = row_data
    ws5.row_dimensions[ri].height = 28
    bg = LIGHT if ri % 2 == 0 else WHITE
    vals = [pais, iso3, survey, freq, period, recent, n_waves, mig, portal, notes]
    for ci, val in enumerate(vals, 1):
        c = ws5.cell(row=ri, column=ci)
        c.value = val
        c.font  = Font(size=9, color=DARK, bold=(ci <= 2), name='Calibri')
        c.fill  = fill(bg)
        c.alignment = Alignment(horizontal='center' if ci <= 7 else 'left',
                                vertical='center', wrap_text=True)
        c.border = bd()

# Totals block
tot_row = 16
sec_row(ws5, tot_row, 'TOTALES DEL PROYECTO')

totals_data = [
    ('Total paises',         '10',  '4 con scripts existentes  +  6 nuevos'),
    ('Total ondas',          '71',  'Grupo A: 26  |  Grupo B: 45'),
    ('Ondas ya hechas',      '5',   'COL 2025t3, COL 2024t3, ECU 2025m12, PER 2024a, CHL 2024a'),
    ('Ondas Grupo A nuevas', '21',  'Descargar + clonar/ejecutar en dias 1-5 (semana actual)'),
    ('Ondas Grupo B nuevas', '45',  '6 scripts nuevos (survey_mapper) + 39 clones'),
    ('Variable migracion',   '8/10','DOM y PAN requieren verificacion adicional del DDI'),
    ('Periodo cubierto',     '2018-2025','COL/ECU/DOM/PRY/CRI hasta 2025; PER/ARG/URY/PAN hasta 2024'),
    ('Distribucion trabajo', '5 dias','Lun-Vie 6-10 Abril 2026. Descargas en paralelo dia 1'),
]

for ri, (label, val, detail) in enumerate(totals_data, tot_row + 1):
    ws5.row_dimensions[ri].height = 18
    bg = LIGHT if ri % 2 == 0 else WHITE
    for ci, (txt, w) in enumerate([(label,True),(val,True),(detail,False)], 1):
        c = ws5.cell(row=ri, column=ci)
        c.value = txt; c.font = Font(bold=w, size=9, color=DARK, name='Calibri')
        c.fill  = fill(bg)
        c.alignment = aln(h='left' if ci >= 2 else 'left')
        c.border = bd()
    # merge detail across remaining cols
    ws5.merge_cells(f'C{ri}:J{ri}')

# merge value col across a couple cols
for ri in range(tot_row + 1, tot_row + 1 + len(totals_data)):
    ws5.merge_cells(f'B{ri}:B{ri}')

ws5.freeze_panes = 'A4'

# ── Save ──────────────────────────────────────────────────────────────────────
wb.save(OUT)
print(f'Saved: {OUT}')
