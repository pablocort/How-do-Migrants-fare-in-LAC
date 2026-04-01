use "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Enpove 2022\3. Bases creadas\Completa.dta", clear

tab p502

*====================================================*
* Labels de carrera (solo códigos presentes en p502)
* Fuente: universo que compartiste
*====================================================*

capture label drop lbl_p502_carrera
label define lbl_p502_carrera ///
    11026  "Ciencias Militares (Ejército)" ///
    11035  "Capitanía y Guardacostas" ///
    11055  "Fuerzas Especiales" ///
    11105  "Policía Naval" ///
    11115  "Seguridad e Instrucción Militar" ///
    21015  "Administración y Ciencias Policiales" ///
    21016  "Administración y Ciencias Policiales (oficiales)" ///
    111015 "Educación Inicial" ///
    111016 "Educación Básica, Inicial y Primaria" ///
    111026 "Educación Inicial" ///
    111036 "Educación Inicial -  Niñez Temprana" ///
    111046 "Educación Inicial -  Retardo Mental" ///
    112015 "Educación Primaria" ///
    112016 "Educación Primaria" ///
    112026 "Educación Primaria -  Educación Básica Alternativa" ///
    112036 "Educación Primaria - Inglés" ///
    112046 "Educación Primaria Intercultural" ///
    112066 "Educación Primaria y Bilingüe Intercultural" ///
    112076 "Educación Primaria y Problemas de Aprendizaje" ///
    121015 "Educación en Computación e Informática" ///
    121016 "Educación Secundaria" ///
    121025 "Educación en Idiomas - Inglés" ///
    121036 "Educación Secundaria - Arte" ///
    121065 "Educación Secundaria - Ciencias Sociales" ///
    121066 "Educación Secundaria - Biología y Química" ///
    121076 "Educación Secundaria - Ciencia Tecnología y Ambiente" ///
    121085 "Educación Secundaria - Matemática" ///
    121096 "Educación Secundaria - Ciencias Biológicas y Química" ///
    121116 "Educación Secundaria - Ciencias Matemáticas, Físicas e Informática" ///
    121126 "Educación Secundaria - Ciencias Naturales" ///
    121136 "Educación Secundaria - Ciencias Naturales Tecnología y Ambiente" ///
    121156 "Educación Secundaria - Ciencias Sociales" ///
    121176 "Educación Secundaria - Ciencias Sociales - Geografía" ///
    121216 "Educación Secundaria - Ciencias Sociales y Desarrollo Rural" ///
    121226 "Educación Secundaria - Ciencias Sociales y Promoción Socio Cultural" ///
    121236 "Educación Secundaria - Ciencias Sociales y Turismo" ///
    121246 "Educación Secundaria - Computación e Informática" ///
    121256 "Educación Secundaria - Comunicación" ///
    121286 "Educación Secundaria - Filosofía y Psicopedagogía" ///
    121306 "Educación Secundaria - Historia, Geografía y Ecología" ///
    121336 "Educación Secundaria - Historia y Geografía" ///
    121346 "Educación Secundaria - Idioma Extranjero Traducción e Interpretación" ///
    121366 "Educación Secundaria - Inglés" ///
    121376 "Educación Secundaria - Inglés e Italiano" ///
    121406 "Educación Secundaria - Lengua, Comunicación e Idioma Inglés" ///
    121426 "Educación Secundaria - Lengua y Literatura" ///
    121436 "Educación Secundaria - Lenguaje, Literatura e Idiomas" ///
    121456 "Educación Secundaria - Matemática" ///
    121516 "Educación Secundaria - Para el trabajo" ///
    121996 "Otras Carreras de Educación Secundaria" ///
    131015 "Educación Física" ///
    131016 "Educación Física" ///
    131036 "Educación Física en Poblaciones Especiales" ///
    131046 "Educación Física y Danzas" ///
    131056 "Educación Física y Deportes" ///
    141015 "Educación Especial Audición" ///
    141025 "Educación Especial Retardo" ///
    151056 "Educación Artística - Música" ///
    161036 "Construcción Civil" ///
    161046 "Construcciones Metálicas - Soldadura Industrial" ///
    161056 "Diseño Industrial y Arquitectónico" ///
    161076 "Electricidad" ///
    161086 "Electrónica" ///
    161096 "Electrónica e Informática" ///
    161116 "Mecánica Automotriz" ///
    161126 "Mecánica de Producción" ///
    199015 "Educación Básica Alternativa" ///
    199016 "Educación 1" ///
    199025 "Otras Carreras de Educación" ///
    199996 "Otras Carreras de Educación" ///
    212016 "Historia" ///
    213036 "Literatura" ///
    213046 "Literatura y Lingüística 1" ///
    214015 "Interpretación de Idiomas" ///
    214016 "Idiomas" ///
    214025 "Traducción de Idiomas" ///
    215015 "Archivos" ///
    215016 "Archivo  y Gestión Documental 1" ///
    215026 "Bibliotecología y Ciencias de la Información" ///
    216016 "Filosofía" ///
    216025 "Teología - Católica" ///
    216026 "Teología" ///
    217016 "Estudios Latinoamericanos" ///
    221016 "Artes 1" ///
    221035 "Restauración y Conservación de Obras de Arte" ///
    221036 "Artes  Escénicas" ///
    221996 "Otras Carreras de Arte" ///
    222016 "Arte y Diseño Gráfico Empresarial 1" ///
    222026 "Arte y Diseño Empresarial" ///
    222046 "Diseño Digital Publicitario" ///
    222055 "Ciencias Publicitarias" ///
    222056 "Diseño Gráfico" ///
    222066 "Diseño Gráfico Publicitario" ///
    222075 "Dirección y Diseño Gráfico" ///
    222076 "Diseño Industrial" ///
    222095 "Diseño de Interiores" ///
    222105 "Diseño de Producto" ///
    222106 "Diseño Profesional Gráfico" ///
    222116 "Diseño y Gestión en Moda" ///
    222125 "Diseño Gráfico" ///
    222155 "Diseño Industrial" ///
    222175 "Diseño Técnico" ///
    222205 "Publicidad" ///
    222996 "Otras Carreras de Diseño" ///
    224015 "Composición" ///
    224016 "Artista Músico" ///
    224036 "Música" ///
    224106 "Producción Musical" ///
    225016 "Teatro con Mención en Actuación" ///
    311016 "Sociología" ///
    311025 "Relaciones Institucionales" ///
    311035 "Relaciones Públicas" ///
    312026 "Servicio Social" ///
    312036 "Trabajo Social" ///
    313015 "Terapia Psicoanalítica" ///
    313016 "Psicología" ///
    321015 "Ciencias de la Comunicación" ///
    321026 "Ciencias de la Comunicación" ///
    321036 "Ciencias de la Comunicación Social 2" ///
    321046 "Ciencias de la Comunicación y Publicidad" ///
    321056 "Comunicación Audiovisual" ///
    321065 "Comunicación Social" ///
    321066 "Comunicación Audiovisual y Medios Interactivos" ///
    321116 "Comunicación y Periodismo" ///
    321126 "Comunicación y Publicidad" ///
    321136 "Comunicaciones 3" ///
    322026 "Periodismo" ///
    322035 "Periodismo" ///
    322055 "Periodismo Deportivo" ///
    322066 "Producción de Radio, Cine y Televisión" ///
    322076 "Publicidad" ///
    331016 "Administración" ///
    331025 "Administración" ///
    331026 "Administración de Banca y Finanzas" ///
    331035 "Administración Bancaria" ///
    331036 "Administración de Empresas" ///
    331046 "Administración de Negocios" ///
    331055 "Administración Bancaria y Financiera" ///
    331056 "Administración de Negocios Turísticos" ///
    331065 "Administración de Aeropuertos" ///
    331066 "Administración de Servicios" ///
    331076 "Administración en Salud" ///
    331085 "Administración de Banca y Finanzas" ///
    331086 "Administración y Emprendimiento" ///
    331095 "Administración de Empresas" ///
    331096 "Administración y Finanzas" ///
    331106 "Administración y Gerencia" ///
    331115 "Administración de Negocios" ///
    331116 "Administración y Gestión Empresarial" ///
    331125 "Administración de Negocios y Ventas" ///
    331126 "Administración y Recursos Humanos" ///
    331135 "Administración de Seguros" ///
    331136 "Administración y Sistemas" ///
    331146 "Ciencias Administrativas 1" ///
    331155 "Administración Industrial" ///
    331156 "Ciencias Empresariales" ///
    331165 "Administración Logística" ///
    331175 "Administración Municipal" ///
    331195 "Administración y Gestión Empresarial" ///
    331205 "Administración y Finanzas" ///
    331206 "Ingeniería Empresarial" ///
    331216 "Ingeniería Empresarial y de Sistemas" ///
    331235 "Gerencia" ///
    331245 "Gestión Comercial" ///
    331255 "Gestión del Emprendimiento" ///
    331275 "Organización y Administración de Empresas" ///
    332025 "Administración de Empresas Turísticas y Hoteleras" ///
    332035 "Administración de Hostelería" ///
    332046 "Administración de Servicios Turísticos 1" ///
    332066 "Administración en Turismo" ///
    332075 "Administración de Negocios Internacionales de Turismo" ///
    332076 "Administración en Turismo y Hotelería 2" ///
    332096 "Administración en Turismo, Hotelería y Gastronomía" ///
    332105 "Cocina" ///
    332115 "Ecoturismo y Gestión Ambiental" ///
    332125 "Gastronomía y Arte Culinario" ///
    332135 "Hostelería" ///
    332155 "Pastelería" ///
    332165 "Servicios Hoteleros y Cocina" ///
    332175 "Turismo y Hotelería" ///
    332186 "Gastronomía" ///
    332256 "Hotelería y Administración" ///
    332276 "Turismo" ///
    332336 "Turismo y Hotelería" ///
    333015 "Marketing" ///
    333016 "Administración y Marketing" ///
    333036 "Marketing" ///
    333046 "Marketing Empresarial" ///
    333055 "Marketing y Publicidad" ///
    333075 "Mercadotecnia" ///
    333106 "Marketing y Publicidad" ///
    334016 "Administración y Agronegocios" ///
    334036 "Ingeniería en Agronegocios" ///
    335025 "Comercio Exterior" ///
    335026 "Administración de Negocios Internacionales 1" ///
    335036 "Comercio Exterior" ///
    335056 "Comercio y Negocios Internacionales" ///
    335065 "Logística del Comercio Internacional" ///
    335066 "Gestión" ///
    335076 "Gestión de Puertos y Aduanas" ///
    335146 "Relaciones Internacionales y Negociaciones" ///
    336016 "Administración Pública" ///
    336026 "Administración Pública y Gestión Social" ///
    336046 "Gestión Pública y Desarrollo Social" ///
    337015 "Asistente Ejecutivo" ///
    337025 "Secretariado Ejecutivo" ///
    339015 "Administración de Recursos Humanos" ///
    339016 "Administración y Gestión Deportiva" ///
    339035 "Administrativo" ///
    339056 "Gestión de Recursos Humanos" ///
    339076 "Relaciones Industriales" ///
    339085 "Planificación y Gestión de Desarrollo" ///
    339095 "Supervisión de Operaciones" ///
    339996 "Otras Carreras de Administración" ///
    341025 "Economía Empresarial" ///
    341026 "Economía" ///
    341036 "Economía Agraria" ///
    341066 "Economía Pública" ///
    341086 "Economía y Gestión Ambiental" ///
    342015 "Banca y Finanzas" ///
    342025 "Contabilidad" ///
    342026 "Banca y Seguros" ///
    342035 "Contabilidad Computarizada" ///
    342036 "Ciencias Contables" ///
    342045 "Contabilidad y Finanzas" ///
    342056 "Contabilidad" ///
    342066 "Contabilidad Administrativa y Auditoria" ///
    342076 "Contabilidad Auditoría y Finanzas 1" ///
    342086 "Contabilidad y Administración" ///
    342106 "Contabilidad y Finanzas" ///
    342116 "Contabilidad y Tributación" ///
    342136 "Gestión Tributaria" ///
    351016 "Derecho" ///
    351026 "Derecho Corporativo" ///
    351046 "Derecho del Mar y Servicios Aduaneros" ///
    351056 "Derecho y Ciencias Políticas 1" ///
    352016 "Ciencia Política" ///
    352026 "Ciencia Política y Gobierno" ///
    411016 "Biología" ///
    411046 "Biología y Microbiología" ///
    411076 "Ciencias Biológicas" ///
    412015 "Zootecnia" ///
    412016 "Ingeniería Zootecnia 1" ///
    412026 "Zootecnia" ///
    421026 "Física" ///
    422016 "Ingeniería de Procesos Químicos y Metalúrgicos" ///
    422025 "Química Industrial" ///
    422026 "Ingeniería Química" ///
    422035 "Tecnología de Análisis Químico" ///
    422036 "Química" ///
    423016 "Geología" ///
    423036 "Ingeniería de Geología - Geotecnia" ///
    423046 "Ingeniería Geofísica" ///
    423056 "Ingeniería Geológica" ///
    431016 "Matemática 1" ///
    431036 "Matemática e Informática" ///
    432046 "Ingeniería Estadística e Informática" ///
    441016 "Ciencias de la Computación" ///
    441025 "Administración Informática de Empresas" ///
    441036 "Computación Científica" ///
    441045 "Análisis de Sistemas" ///
    441046 "Computación e Informática" ///
    441056 "Informática" ///
    441065 "Analista" ///
    441085 "Computación" ///
    441095 "Computación e Informática" ///
    441115 "Computación y Sistemas" ///
    441125 "Informática" ///
    441185 "Redes y Seguridad Informática" ///
    441225 "Sistemas de Información" ///
    441245 "Software y Sistemas" ///
    511016 "Ingeniería de Seguridad y Auditoría Informática" ///
    511026 "Ingeniería de Sistemas" ///
    511036 "Ingeniería de Sistemas de Información" ///
    511056 "Ingeniería de Sistemas e Informática 1" ///
    511076 "Ingeniería de Sistemas y Computación 2" ///
    511136 "Ingeniería de Tecnologías de la Información y Sistemas" ///
    511146 "Ingeniería en Tecnologías y Sistemas de Información" ///
    511156 "Ingeniería Informática" ///
    511166 "Ingeniería Informática y Estadística 3" ///
    512015 "Control de Tránsito Aéreo" ///
    512016 "Ingeniería de Redes y Comunicaciones" ///
    512035 "Técnica en Ingeniería de Sonidos" ///
    512045 "Técnica en Ingeniería de Telecomunicaciones" ///
    512046 "Ingeniería de Telecomunicaciones 1" ///
    521015 "Procesos Industriales y de Sistemas" ///
    521016 "Ingeniería Ambiental y de Prevención de Riesgos" ///
    521025 "Salud y Seguridad Ocupacional" ///
    521026 "Ingeniería de Higiene y Seguridad Industrial" ///
    521035 "Tecnología de la Producción" ///
    521036 "Ingeniería de la Producción y Administración" ///
    521046 "Ingeniería Industrial" ///
    521056 "Ingeniería Industrial y Comercial" ///
    522015 "Gastronomía Industrial" ///
    522016 "Industrias Alimentarias" ///
    522025 "Industrias Alimentarias" ///
    522026 "Ingeniería Alimentaria 1" ///
    522036 "Ingeniería de Industrias Alimentarias 2" ///
    523015 "Agroindustrias" ///
    523016 "Agroindustrias" ///
    523026 "Ingeniería Agroindustrial" ///
    524015 "Electricidad" ///
    524016 "Ingeniería de Sistemas de Energía 1" ///
    524025 "Electricidad Industrial" ///
    524026 "Ingeniería Eléctrica" ///
    524035 "Electrotécnia Industrial" ///
    524045 "Técnicas de Ingeniería Eléctrica" ///
    524046 "Ingeniería Eléctrica y Electrónica" ///
    525015 "Electrónica" ///
    525016 "Ingeniería Electrónica" ///
    525045 "Electrónica de Sistemas Industriales" ///
    525055 "Electrónica Digital" ///
    525065 "Electrónica Industrial" ///
    525105 "Técnicas de Ingeniería Electrónica" ///
    526015 "Aeronáutica" ///
    526016 "Ingeniería de Materiales" ///
    526036 "Ingeniería Mecánica" ///
    526045 "Mantenimiento de Aeronaves" ///
    526056 "Ingeniería Mecánica Eléctrica 1" ///
    526065 "Mantenimiento de Maquinaria" ///
    526075 "Mantenimiento de Maquinaria de Planta" ///
    526076 "Ingeniería Mecatrónica" ///
    526085 "Mantenimiento de Maquinaria Pesada" ///
    526095 "Mantenimiento de Motores, Hélices y Unidad de Potencia Auxiliar" ///
    526105 "Mantenimiento de Vehículos Motorizados y Equipos Contra   Incendio" ///
    526145 "Mecánica Aeronaval" ///
    526165 "Mecánica Automotriz" ///
    526175 "Mecánica de Mantenimiento" ///
    526185 "Mecánica de Producción" ///
    526215 "Operación de Máquinas, Herramientas y Control Numérico" ///
    526225 "Técnica en Ingeniería Mecánica de Mantenimiento" ///
    526235 "Técnica en Ingeniería Mecánica de Producción" ///
    526245 "Tecnología Mecánica Eléctrica" ///
    527035 "Geología de Minas" ///
    527036 "Ingeniería de Petróleo" ///
    527046 "Ingeniería de Petróleo y Gas Natural" ///
    527055 "Metalurgia" ///
    527056 "Ingeniería Metalúrgica 1" ///
    527066 "Ingeniería Metalúrgica y de Materiales 2" ///
    527075 "Procesos Químicos y Metalúrgicos" ///
    527076 "Ingeniería Petroquímica" ///
    528015 "Diseño de Modas" ///
    528026 "Ingeniería Textil y Confecciones 1" ///
    528055 "Gestión de Modas y Confecciones" ///
    531016 "Ingeniería Civil" ///
    531025 "Construcción Civil" ///
    531026 "Ingeniería Civil y Ambiental" ///
    531095 "Topografía" ///
    531105 "Topografía Superficial y Minera" ///
    532016 "Ingeniería Sanitaria" ///
    533015 "Arquitectura de Interiores" ///
    533026 "Arquitectura" ///
    534025 "Conservación y Restauración" ///
    592016 "Ciencias Aeronáuticas" ///
    592046 "Ingeniería de Navegación y Marina Mercante" ///
    592056 "Ingeniería del Transporte Marítimo y Gestión Logística Portuaria" ///
    592066 "Ingeniería Hidráulica" ///
    592086 "Ingeniería Naval" ///
    594015 "Manejo de Cuencas y Gestión Ambiental" ///
    594016 "Ciencia Tecnología y Ambiente" ///
    594025 "Medio Ambiente" ///
    594026 "Desarrollo Ambiental" ///
    594035 "Medio Ambiente y Recursos Naturales" ///
    594046 "Gestión Ambiental Empresarial" ///
    594066 "Ingeniería Ambiental y Recursos Naturales" ///
    594086 "Ingeniería de Medio Ambiente 1" ///
    594106 "Ingeniería en Ecoturismo" ///
    599016 "Ingeniería Automotriz" ///
    611016 "Agronomía" ///
    611035 "Agropecuaria" ///
    611036 "Ciencias Agrarias" ///
    611056 "Conservación de Suelos y Agua" ///
    611065 "Gestión de Recursos Hídricos" ///
    611066 "Ingeniería Agraria" ///
    611076 "Ingeniería Agrícola" ///
    611095 "Producción Agraria" ///
    611105 "Producción Agrícola" ///
    611106 "Ingeniería Agrónoma" ///
    611115 "Producción Agropecuaria" ///
    611116 "Ingeniería Agronómica" ///
    611125 "Producción Pecuaria" ///
    611136 "Ingeniería Agropecuaria" ///
    621016 "Medicina Veterinaria" ///
    621026 "Veterinaria y Zootecnia" ///
    621036 "Medicina Veterinaria y Zootecnia" ///
    711016 "Medicina" ///
    711025 "Paramédico" ///
    711026 "Medicina Humana" ///
    712015 "Nutrición y Dietética" ///
    712025 "Nutrición y Tecnología de los Alimentos" ///
    712046 "Nutrición" ///
    712066 "Nutrición, Salud y Técnicas Alimentarias" ///
    712076 "Nutrición y Dietética" ///
    713015 "Prótesis Dental" ///
    713026 "Odontología" ///
    714015 "Auxiliar de Enfermería" ///
    714016 "Enfermería" ///
    714035 "Enfermería Técnica" ///
    715015 "Fisioterapia y Rehabilitación" ///
    715016 "Laboratorio Clínico" ///
    715025 "Laboratorio Clínico" ///
    715035 "Mantenimiento de Establecimientos de Salud" ///
    715046 "Radiología" ///
    715056 "Tecnología Médica" ///
    715075 "Radiología" ///
    715076 "Terapia Física" ///
    715086 "Terapia Física y Rehabilitación" ///
    715096 "Terapia Ocupacional" ///
    716015 "Farmacia" ///
    716016 "Ciencias Farmacéuticas y Bioquímica" ///
    716026 "Farmacia y Bioquímica" ///
    719016 "Ciencias del Deporte" ///
    811105 "Turismo" ///
    812015 "Cosmética Dermatológica" ///
    , replace

label values p502 lbl_p502_carrera


*====================================================*
* cinef13_ci (0-10) derivado de p502 (código carrera)
*====================================================*

capture drop cinef13_ci
gen byte cinef13_ci = .

*--- 0: Fuerzas Armadas y Policiales 
replace cinef13_ci = 0 if inlist(p502, ///
    11026,11035,11055,11105,11115, ///
    21015,21016)

*--- 1: Educación 
replace cinef13_ci = 1 if inlist(p502, ///
    111015,111016,111026,111036,111046, ///
    112015,112016,112026,112036,112046,112066,112076, ///
    121015,121016,121025,121036,121065,121066,121076,121085,121096,121116,121126,121136,121156,121176,121216,121226,121236,121246,121256,121286,121306,121336,121346,121366,121376,121406,121426,121436,121456,121516,121996, ///
    131015,131016,131036,131046,131056, ///
    141015,141025, ///
    151056, ///
    161036,161046,161056,161076,161086,161096,161116,161126, ///
    199015,199016,199025,199996)

*--- 2: Artes y Humanidades 
replace cinef13_ci = 2 if inlist(p502, ///
    212016, ///
    213036,213046, ///
    214015,214016,214025, ///
    215015,215016,215026, ///
    216016,216025,216026, ///
    217016, ///
    221016,221035,221036,221996, ///
    222016,222026,222046,222055,222056,222066,222075,222076,222095,222105,222106,222116,222125,222155,222175,222205,222996, ///
    224015,224016,224036,224106, ///
    225016)

*--- 3: Ciencias Sociales, Periodismo e Información (prefijos 31 y 32)
replace cinef13_ci = 3 if cinef13_ci==. & inrange(p502, 310000, 329999)

*--- 4: Administración de Empresas y Derecho (prefijos 33,34,35)
replace cinef13_ci = 4 if cinef13_ci==. & inrange(p502, 330000, 359999)

*--- 5: Ciencias Naturales, Matemáticas y Estadística (prefijos 41,42,43)
replace cinef13_ci = 5 if cinef13_ci==. & inrange(p502, 410000, 439999)

*--- 6: TIC (44xxxx + 51xxxx + 512xxx)
replace cinef13_ci = 6 if cinef13_ci==. & inrange(p502, 440000, 449999)
replace cinef13_ci = 6 if cinef13_ci==. & inrange(p502, 510000, 519999)
replace cinef13_ci = 6 if cinef13_ci==. & inrange(p502, 512000, 512999)

*--- 7: Ingeniería, Industria y Construcción (52xxxx + 53xxxx + 59xxxx)
replace cinef13_ci = 7 if cinef13_ci==. & inrange(p502, 520000, 539999)
replace cinef13_ci = 7 if cinef13_ci==. & inrange(p502, 590000, 599999)

*--- 8: Agropecuario, Silvicultura, Pesca y Veterinaria (61xxxx + 62xxxx)
replace cinef13_ci = 8 if cinef13_ci==. & inrange(p502, 610000, 629999)

*--- 9: Salud y bienestar (71xxxx)
replace cinef13_ci = 9 if cinef13_ci==. & inrange(p502, 710000, 719999)

*--- 10: Servicios (81xxxx + 82xxxx)
replace cinef13_ci = 10 if cinef13_ci==. & inrange(p502, 810000, 829999)

*--- Dejar 99999 u otros fuera como missing 
replace cinef13_ci = . if p502==99999

label var cinef13_ci "CINEF-13 (0-10) derivado de p502"

capture label drop lbl_cinef13_ci
label define lbl_cinef13_ci ///
    0  "Programas y certificaciones genéricos" ///
    1  "Educación" ///
    2  "Artes y Humanidades" ///
    3  "Ciencias Sociales, Periodismo e Información" ///
    4  "Administración de Empresas y Derecho" ///
    5  "Ciencias Naturales, Matemáticas y Estadística" ///
    6  "Tecnología de la Información y la Comunicación (TIC)" ///
    7  "Ingeniería, Industria y Construcción" ///
    8  "Agropecuario, Silvicultura, Pesca y Veterinaria" ///
    9  "Salud y bienestar" ///
    10 "Servicios", replace

label values cinef13_ci lbl_cinef13_ci


******************************************************************************************************
gen cinef13=cinef13_ci

label define cinef13 ///
    0  "Programas genéricos" ///
    1  "Educación" ///
    2  "Artes y Humanidades" ///
    3  "Ciencias Sociales, Periodismo" ///
    4  "Adm. de Empresas y Derecho" ///
    5  "Cs. Naturales, Matemáticas, Est." ///
    6  "TIC" ///
    7  "Ing., Industria y Construcción" ///
    8  "Agro, Silvicultura, Pesca, Vet." ///
    9  "Salud y bienestar" ///
    10 "Servicios", replace

label values cinef13 cinef13

graph bar (percent) [pweight=factorfinal], ///
    over(cinef13, sort(1) descending label(labsize(small))) ///
    ytitle("Porcentaje") ///
    blabel(bar, format(%4.1f) position(outside)) ///
    bargap(10) ///
    horizontal title("PERU")
	
graph export "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\profesiones_peru.png", replace 	

tab2xl cinef13_ci [iw=factorfinal] using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(PERU, replace)

******************************************************************************************************

* Variable agrupada de nivel educativo (Perú) a partir de p501b (string)
* Grupos: Ninguno, Primaria, Secundaria, Media, Superior

capture drop nivel_edu
gen byte nivel_edu = .

* Limpiar espacios (opcional pero recomendable)
replace p501b = strtrim(p501b)

* 0 Ninguno
replace nivel_edu = 0 if p501b == "1.Sin nivel"

* 1 Primaria (incluye inicial + primaria)
replace nivel_edu = 1 if inlist(p501b, ///
    "2.Educación inicial", ///
    "3.Primaria incompleta", ///
    "4.Primaria completa")

* 2 Secundaria
replace nivel_edu = 2 if p501b == "5.Secundaria incompleta"

* 3 Media
**# Bookmark #2
replace nivel_edu = 3 if p501b == "6.Secundaria completa"

* 4 Superior
replace nivel_edu = 4 if inlist(p501b, ///
    "8.Superior No universitaria incompleta", ///
    "9.Superior No universitaria completa", ///
    "10.Superior Universitaria incompleta", ///
    "11.Superior Universitaria completa", ///
    "12.Maestría/ Doctorado")


label define nivel_edu_lbl ///
    0 "Ninguno" ///
    1 "Primaria" ///
    2 "Secundaria" ///
    3 "Media" ///
    4 "Superior", replace

label values nivel_edu nivel_edu_lbl
label var nivel_edu "Nivel educativo agrupado"

graph bar (percent) [pweight=factorfinal], ///
    over(nivel_edu, label(labsize(small))) ///
    ytitle("Porcentaje") ///
    blabel(bar, format(%4.1f) position(outside)) ///
    bargap(10) ///
    bar(1, color(cranberry%70)) ///
	title("PERU")
	
graph export "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\niveledu_peru.png", replace 	
	
