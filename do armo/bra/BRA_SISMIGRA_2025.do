global root "C:\Users\STEFFANNYR\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC"

*** Importar bases 
import delimited "$root\bases armo\raw\bra\sismigra_2024.csv",  clear
keep if pais_nascimento=="VENEZUELA" | pais_nacionalidade=="VENEZUELA" // 121,899
tempfile sismigra_2024
save `sismigra_2024'

import delimited "$root\bases armo\raw\bra\sismigra_2023.csv",  clear
keep if pais_nascimento=="VENEZUELA" | pais_nacionalidade=="VENEZUELA" // 126,336
tempfile sismigra_2023
save `sismigra_2023'

import delimited "$root\bases armo\raw\bra\sismigra_2022.csv",  clear
keep if pais_nascimento=="VENEZUELA" | pais_nacionalidade=="VENEZUELA" // 145,273
tempfile sismigra_2022
save `sismigra_2022'

import delimited "$root\bases armo\raw\bra\sismigra_2021.csv",  clear
keep if pais_nascimento=="VENEZUELA" | pais_nacionalidade=="VENEZUELA" // 168,321
tempfile sismigra_2021
save `sismigra_2021'

import delimited "$root\bases armo\raw\bra\sismigra_2019_2020.csv",  clear
keep if pais_nascimento=="VENEZUELA" | pais_nacionalidade=="VENEZUELA" // 130,753
tempfile sismigra_2019_2020
save `sismigra_2019_2020'

import delimited "$root\bases armo\raw\bra\sismigra_2018.csv",  clear
keep if pais_nascimento=="VENEZUELA" | pais_nacionalidade=="VENEZUELA" // 32,624
tempfile sismigra_2018
save `sismigra_2018'



import delimited "$root\bases armo\raw\bra\sismigra_janeiro_dezembro_2025.csv",  clear
keep if pais_nascimento=="VENEZUELA" | pais_nacionalidade=="VENEZUELA" // 102,128 obs

append using `sismigra_2024'
append using `sismigra_2023'
append using `sismigra_2022'
append using `sismigra_2021'
append using `sismigra_2019_2020', force
append using `sismigra_2018', force


*tab dataregistro
*tab dataentrada


tab profissao

* Crear profesion3_ci y cinef13_ci a partir de profissao (string) - Brasil
* Fuente: Registros administrativos (ocupación → campo de educación, ISCED-F 2013)
* Nota: profissao es variable de OCUPACIÓN; el mapeo a campo educativo es aprox.
********************************************************************************

*==============================================================================
* 1. profesion3_ci
*==============================================================================

gen profesion3_ci = .

* --- 4: Educación ---
replace profesion3_ci = 4  if profissao == "PROFESSOR, OU ASSEMELHADO"

* --- 5: Artes ---
replace profesion3_ci = 5  if profissao == "ARTISTA, ATOR, MUSICO, OU ASSEMELHADO"
replace profesion3_ci = 5  if profissao == "FOTOGRAFO, CINEGRAFISTA, OU ASSEMELHADO"

* --- 6: Humanidades (excepto idiomas) ---
replace profesion3_ci = 6  if profissao == "SACERDOTE, OU MEMBRO ASSELHADO DE ORDENS, OU SEITAS RELIGIOSAS"

* --- 8: Ciencias Sociales y del Comportamiento ---
replace profesion3_ci = 8  if profissao == "PSICOLOGO, ANALISTA, SOCIOLOGO, ASSISTENTE SOCIAL, OU ASSEMELHADO"
replace profesion3_ci = 8  if profissao == "EMBAIXADOR, DIPLOMATA, OU ASSEMELHADO"
replace profesion3_ci = 8  if profissao == "OCUPANTE DE CARGO LEGISLATIVO, ( SENADOR , DEPUTADO OU VEREADOR )"

* --- 9: Periodismo e Información ---
replace profesion3_ci = 9  if profissao == "ESCRITOR, JORNALISTA, TRADUTOR, OU ASSEMELHADO"
replace profesion3_ci = 9  if profissao == "PUBLICITARIO, PROFISSIONAL DE RELACOES PUBLICAS, DESENHISTA, OU ASSEMELHADO"
replace profesion3_ci = 9  if profissao == "LOCUTOR, RADIALISTA, TELEPISTA, RADIOTELEGRAFISTA, TELEGRAFISTA, TELEFONISTA, OU ASSEMELHADO"
replace profesion3_ci = 9  if profissao == "BIBLIOTECARIO, TECNICO ARQUIVISTA, OU ASSEMELHADO"

* --- 10: Educación Comercial y Administración ---
replace profesion3_ci = 10 if profissao == "VENDEDOR VIAJANTE, PROPAGANDISTA, REPRESENTANTE COMERCIAL, COMISSIONISTA, OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "VENDEDOR OU EMPREGADO DE CASA COMERCIAL, COMERCIARIO, VENDEDOR AMBULANTE, VENDEDOR A DOMICILIO, JORNALEIRO, OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "EMPREGADO DE ESCRITORIO, SECRETARIO, BANCARIO SECURITARIO, ECOMOMIARIO, TAQUIGRAFO, RECEPCIONISTA, MECANOGRAFO ( DATILOGRAFO ), OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "CAIXA, TESOUREIRO, OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "ECONOMISTA, ATUARIO, CONTADOR, TECNICO EM CONTABILIDADE, AUDITOR, ESTATISTICO, ADMINISTRADOR, OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "COBRADOR, FISCAL, INSPETOR, OU ASSEMELHADO, NAO CLASSIFICADO SOB OUTRA DEMOMINACAO"
replace profesion3_ci = 10 if profissao == "ADMINISTRADOR OU FUNCIONARIO EXECUTIVO, DA ADMINISTRACAO PUBLICA, DIRETA OU INDIRETA, ( INCLUSIVE OCUPANTE DE CARGO ELETIVO )"
replace profesion3_ci = 10 if profissao == "DIRETOR , GERENTE OU PROPRIETARIO, DE CASA COMERCIAL, ATACADISTA OU VAREJISTA, EXPORTADORA OU IMPORTADORA, OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "CORRETOR OU AGENTE DE SEGUROS, CORRETOR OU AGENTE DE IMOBILIARIO, CORRETOR, AGENTE DE VENDA DE SERVICOS, LEILOEIRO, AVALIADOR, OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "DIRETOR , GERENTE OU PROPRIETARIO, DE INDUSTRIA DE EMPRESA, DE CONSTRUCAO, DE ELETRICIDADE, DE GAS, DE AGUA, DE ESGOTOS, DE EMPRESAS DE EXPLORACAO, DE MINAS OU PEDREIRAS, OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "DIRETOR , GERENTE OU PROPRIETARIO, DE HOSPITAL, DE EMPRESAS DE HOTELARIA, FORNECIMENTO DE REFEICOES, TURISMO, OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "DIRETOR , GERENTE OU PROPRIETARIO, DE EMPRESA DE TRANSPORTE, ARMAZENAGEM, COMUNICACOES, PRODUCAO CINEMATOGRAFICA, OU ASSEMELHADO"
replace profesion3_ci = 10 if profissao == "DIRETOR , GERENTE OU PROPRIETARIO, DE ESTABELECIMENTO FINANCEIRO, DE SEGUROS OU IMOBILIARIO, INCORPORADOR, OU ASSEMELHADO"

* --- 11: Derecho ---
replace profesion3_ci = 11 if profissao == "JURISTA, ADVOGADO, MAGISTRADO, PROMOTOR, OU ASSEMELHADO"
replace profesion3_ci = 11 if profissao == "TABELIAO, OFICIAL DE CARTORIO, OFICIAL DE JUSTICA, OU ASSEMELHADO"

* --- 12: Ciencias Biológicas y afines ---
* Nota: grupo mixto (biólogo, veterinario, zootecnista, agrónomo); se clasifica en Biológicas
replace profesion3_ci = 12 if profissao == "BIOLOGO, VETERINARIO, ZOOTECNISTA, AGRONOMO, OU ASSEMELHADO"

* --- 14: Ciencias Físicas ---
replace profesion3_ci = 14 if profissao == "QUIMICO, FISICO, GEOLOGO, OU OUTRO ESPECIALISTA, EM CIENCIAS FISICAS"

* --- 16: TIC ---
replace profesion3_ci = 16 if profissao == "PROGRAMADOR, ANALISTA, OU OUTRO TECNICO, NO PROCESSAMENTO ELETRONICO DE DADOS"

* --- 17: Ingeniería y Profesiones afines ---
* Nota: ARQUITETO incluido aquí porque el grupo también contiene ingenieros y agrimensores
replace profesion3_ci = 17 if profissao == "ARQUITETO, ENGENHEIRO, AGRIMENSOR, OU ASSEMELHADO"
replace profesion3_ci = 17 if profissao == "MECANICO, OPERADOR, AJUSTADOR, CHAPEADOR, LANTERNEIRO DE VEICULOS, BOMBEIRO HIDRAULICO, ENCANADOR, SOLDADOR, GALVANIZADOR, OU OUTRO TRABALHADOR EM METAIS, NAO CLASSIFICADO SOB OUTRA DENOMINACAO"
replace profesion3_ci = 17 if profissao == "ELETRICISTA, MECANICO ELETRICISTA, MECANICO DE ELETRONICA, REPARADOR DE APARELHOS, DE RADIO E TELEVISAO, DE INSTALACOES TELEFONICAS, E TELEGRAFICAS, OU ASSEMELHADO"
replace profesion3_ci = 17 if profissao == "GARIMPEIROS, TRABALHADOR DE MINAS OU PEDREIRA, BENEFICIADOR DE MINERAIS, PERFURADOR DE POCOS, TRABALHADOR NA EXTRACAO, DE GAS OU PETROLEO, OU ASSEMELHADO"
replace profesion3_ci = 17 if profissao == "OPERADOR DE MAQUINA ESTACIONARIA, DE GUINDASTE, DE MAQUINA DE TERRAPLANAGEM, DE EMPILHADEIRA, OU OUTRO OPERADOR ASSEMELHADO, LUBRIFICADOR OU GRAXEIRO DESSAS MAQUINAS"
replace profesion3_ci = 17 if profissao == "AERONAUTA, PILOTO, NAVEGADOR, COMISSARIO, AEROMOCA, MECAMICO, OU OUTRO TRABALHADOR, DA NAVEGACAO AEREA"

* --- 18: Industria y Procesamiento ---
replace profesion3_ci = 18 if profissao == "PADEIRO, CERVEJEIRO, ACOUGUEIRO, TRABALHADOR EM LATICINIOS, OU OUTRO TRABALHADOR, NA PRODUCAO DE ALIMENTOS OU BEBIDAS"
replace profesion3_ci = 18 if profissao == "DECORADOR, COSTUREIRO, ALFAIATE, MODISTA, PELETEIRO, TAPECEIRO, OU ASSEMELHADO"
replace profesion3_ci = 18 if profissao == "MECANICO DE PRECISAO, RELOJOEIRO, JOALHEIRO, OURIVES, OU ASSEMELHADO"
replace profesion3_ci = 18 if profissao == "INDUSTRIARIO OU SEVENTE, NAO CLASSIFICADO SOB OUTRA DEMOMINACAO"
replace profesion3_ci = 18 if profissao == "CARPINTEIRO, MARCENEIRO, TANOEIRO, OU ASSEMELHADO"
replace profesion3_ci = 18 if profissao == "EMPACOTADOR, ETIQUETADOR, OU ASSEMELHADO"
replace profesion3_ci = 18 if profissao == "VULCANIZADOR OU TRABALHADOR, DE FABRICACAO DE PNEUMATICA, TRABALHADOR DA FABRICACAO, DE INSTRUMENTOS MUSICAIS, OU OUTRO ARTESAO, OU TRABALHADOR, DOS DIVERSOS PROCESSOS DE PRODUCAO, NAO CLASSIFICADO SOB OUTRA DENOMINACAO"
replace profesion3_ci = 18 if profissao == "FUNDIDOR, LAMINADOR, FERREIRO, TREFILADOR, OU ASSEMELHADO DA PRODUCAO, E TRATAMENTO DE METAIS"
replace profesion3_ci = 18 if profissao == "TRABALHADOR DA FABRICACAO, DE INSTRUMENTOS MUSICAIS, ARTESAO OU TRABALHADOR, DOS DIVERSOS PROCESSOS DE PRODUCAO, NAO CLASSIFICADO SOB OUTRA DENOMINACAO"
replace profesion3_ci = 18 if profissao == "OLEEIRO, OPERADOR DE FORNO, MOLDADOR DE VIDRO, DE ARGILA, OU ASSEMELHADO"
replace profesion3_ci = 18 if profissao == "SAPATEIRO, CORREEIRO, COSEDOR DE COUROS, OU ASSEMELHADO"
replace profesion3_ci = 18 if profissao == "TRABALHADOR DA INDUSTRIA QUIMICA, DA INDUSTRIA DE PRODUDOS FARMACEUTICOS, E VETERINARIOS, DA INDUSTRIA DE PERFUMARIA, SABOES E VELAS, DA INDUSTRIA DE PRODUTOS, DE MATERIAS PLASTICAS, DA INDUSTRIA DE PAPEL E PALELAO, OU ASSEMELHADO"
replace profesion3_ci = 18 if profissao == "TIPOGRAFO, COMPOSITOR, IMPRESSOR, LINOTIPISTA, OPERADOR DE MAQUINA DE IMPRESSAO, GRAVADOR, ENCARDENADOR, OU ASSEMELHADO"
replace profesion3_ci = 18 if profissao == "FIANDEIRO, TECELAO, TECELAO DE MALHARIA, TINTUREIRO, OU ASSEMELHADO"
replace profesion3_ci = 18 if profissao == "TRABALHADOR NA INDUSTRIA DO FUMO"

* --- 19: Arquitectura y Construcción ---
replace profesion3_ci = 19 if profissao == "PEDREIRO, SERVENTE, LADRILHEIRO, GESSEIRO, VIDRACEIRO, OU ASSEMELHADO, A OUTRO TRABALHADOR DA CONSTRUCAO CIVIL, NAO CLASSIFICADO SOB OUTRA DEMOMINACAO"
replace profesion3_ci = 19 if profissao == "PINTOR, EMPAPELADOR, OU ASSEMELHADO, DA CONSTRUCAO CIVIL DE CONSERVACAO"

* --- 20: Agropecuario ---
replace profesion3_ci = 20 if profissao == "TRABALHADOR AGRICOLA, JARDINEIRO, OU ASSEMELHADO, AGRICULTOR, LAVRADOR"
replace profesion3_ci = 20 if profissao == "DIRETOR , GERENTE OU PROPRIETARIO, DE ESTABELECIMENTO AGRICOLA OU PECUARIO, ( AGRICULTOR , FAZENDEIRO , PECUARISTA ), OU ASSEMELHADO"

* --- 22: Pesca y acuicultura ---
* Nota: grupo incluye también lenhador (silvicultura); se clasifica en Pesca por ser el principal
replace profesion3_ci = 22 if profissao == "PESCADOR, LENHADOR, OU ASSEMELHADO"

* --- 24: Salud ---
replace profesion3_ci = 24 if profissao == "ENFERMEIRO, PARTEIRA, MASSAGISTA, NUTRICIONISTA, OU TECNICO PARAMEDICO"
replace profesion3_ci = 24 if profissao == "MEDICO, CIRURGIAO, DENTISTA, OU ASSEMELHADO"
replace profesion3_ci = 24 if profissao == "FARMACEUTICO, OU ASSEMELHADO"

* --- 25: Bienestar ---
replace profesion3_ci = 25 if profissao == "TRABALHADOR EM SERVICOS DE ESPORTES, OU DIVERSOES, NAO CLASSIFICADO SOB OUTRA DENOMINACAO"
replace profesion3_ci = 25 if profissao == "ATLETA, ESPORTISTA, OU ASSEMELHADO"

* --- 26: Servicios personales ---
replace profesion3_ci = 26 if profissao == "COZINHEIRO, MORDOMO, GOVERNANTA, CAMAREIRO, GARCAO, OU ASSEMELHADO"
replace profesion3_ci = 26 if profissao == "PORTEIRO, ZELADOR, ASCENSSORISTA, FAXINEIRO, EMPREGADO DE LIMPEZA, EMPREGADO DOMESTICO, OU ASSEMELHADO"
replace profesion3_ci = 26 if profissao == "BARBEIRO, CABELEIREIRO, ESTETICISTA, ESPECIALISTA DE INSTITUTO DE BELEZA, OU ASSEMELHADO"
replace profesion3_ci = 26 if profissao == "LAVADEIRO, LIMPADOR A SECO, PASSADOR, OU ASSEMELHADO"
replace profesion3_ci = 26 if profissao == "EMBALSAMADOR, OU EMPREGADO DE EMPRESA FUNERARIA"
replace profesion3_ci = 26 if profissao == "MANEQUIM, MODELO, OU ASSEMELHADO"

* --- 28: Servicios de seguridad ---
replace profesion3_ci = 28 if profissao == "PATRULHEIRO, VIGIA, GUARDA, BOMBEIRO, OU ASSEMELHADO"
replace profesion3_ci = 28 if profissao == "POLICIAS, DELEGADO, AGENTE, INVESTIGADOR, ESCRIVAO, PERITO, PAPILOSCOPISTA, OU ASSEMELHADO"
replace profesion3_ci = 28 if profissao == "MILITAR NA INATIVIDADE"
replace profesion3_ci = 28 if profissao == "MILITAR NA ATIVA"
replace profesion3_ci = 28 if profissao == "FUNCIONARIO DIPLOMATICO ESTRANGEIRO, ADIDO ESTRANGEIRO, MILITAR ESTRANGEIRO, OU ASSEMELHADO"

* --- 29: Servicios de transporte ---
replace profesion3_ci = 29 if profissao == "MOTORISTA, CONDUTOR, OU OUTRO TRABALHADOR, DE TRANSPORTE RODOVIARIO"
replace profesion3_ci = 29 if profissao == "OFICIAL, PILOTO, MAQUINISTA, MARINHEIRO, OU OUTRO TRABALHADOR, NA NAVEGACAO MARITIMA OU FLUVIAL"
replace profesion3_ci = 29 if profissao == "MAQUINISTA, FOGUISTA, CHEFE DE TREM, CHEFE DE ESTACAO, OU OUTRO TRABALHADOR, DE TRANSPORTE FERROVIARIO OU METROVIARIO"
replace profesion3_ci = 29 if profissao == "TRABALHADOR DE TRANSPORTE, OU COMUNICACOES, NAO CLASSIFICADO SOB OUTRA DENOMINACAO"
replace profesion3_ci = 29 if profissao == "PROPRIETARIO MOTORISTA, DE VEICULO DE TRANSPORTE DE PASSAGEIROS"
replace profesion3_ci = 29 if profissao == "PROPRIETARIO MOTORISTA, DE VEICULO DE TRANSPORTE DE CARGA"
replace profesion3_ci = 29 if profissao == "ESTIVADOR, CARREGADOR, OU ASSEMELHADO"
replace profesion3_ci = 29 if profissao == "CARTEIRO, MENSAGEIRO, OU ASSEMELHADO"

* --- missing: categorías no clasificables ---
* OUTRA OCUPACAO NAO CLASSIFICADA, MENOR, PRENDAS DOMESTICAS, SEM OCUPACAO,
* ESTUDANTE, APOSENTADO, BOLSISTA/ESTAGIARIO, PROFISSIONAL LIBERAL NAO CLASSIF.,
* FUNCIONARIO PUBLICO NAO CLASSIF., DEPENDENTE VIPER/VITEM, CAPITALISTA,
* DIRETOR NAO CLASSIF.

*--- Labels ---
capture label drop lbl_profesion3_ci
label define lbl_profesion3_ci ///
     1 "Programas y certificaciones básicas" ///
     2 "Alfabetización y Aritmética Elemental" ///
     3 "Competencias personales y desarrollo" ///
     4 "Educación" ///
     5 "Artes" ///
     6 "Humanidades (excepto idiomas)" ///
     7 "Idiomas" ///
     8 "Ciencias Sociales y del Comportamiento" ///
     9 "Periodismo e Información" ///
    10 "Educación Comercial y Administración" ///
    11 "Derecho" ///
    12 "Ciencias Biológicas y afines" ///
    13 "Medio Ambiente" ///
    14 "Ciencias Físicas" ///
    15 "Matemáticas y Estadística" ///
    16 "Tecnologías de la Información y la Comunicación (TIC)" ///
    17 "Ingeniería y Profesiones afines" ///
    18 "Industria y Procesamiento" ///
    19 "Arquitectura y Construcción" ///
    20 "Agropecuario" ///
    21 "Silvicultura" ///
    22 "Pesca y acuicultura" ///
    23 "Veterinaria" ///
    24 "Salud" ///
    25 "Bienestar" ///
    26 "Servicios personales" ///
    27 "Servicios de Higiene y Salud Ocupacional" ///
    28 "Servicios de seguridad" ///
    29 "Servicios de transporte", replace

label values profesion3_ci lbl_profesion3_ci
label var profesion3_ci "Área/campo de educación (ISCED-F 2013, agregado 3 dígitos, consecutivo)"

tab2xl profesion3_ci  using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(BRA2, replace)

*==============================================================================
* 2. cinef13_ci (derivada de profesion3_ci)
*==============================================================================

gen cinef13_ci = .
replace cinef13_ci = 0  if inlist(profesion3_ci, 1, 2, 3)
replace cinef13_ci = 1  if profesion3_ci == 4
replace cinef13_ci = 2  if inlist(profesion3_ci, 5, 6, 7)
replace cinef13_ci = 3  if inlist(profesion3_ci, 8, 9)
replace cinef13_ci = 4  if inlist(profesion3_ci, 10, 11)
replace cinef13_ci = 5  if inlist(profesion3_ci, 12, 13, 14, 15)
replace cinef13_ci = 6  if profesion3_ci == 16
replace cinef13_ci = 7  if inlist(profesion3_ci, 17, 18, 19)
replace cinef13_ci = 8  if inlist(profesion3_ci, 20, 21, 22, 23)
replace cinef13_ci = 9  if inlist(profesion3_ci, 24, 25)
replace cinef13_ci = 10 if inlist(profesion3_ci, 26, 27, 28, 29)

capture label drop lbl_cinef13_ci
label define lbl_cinef13_ci ///
     0 "Programas y certificaciones genéricos" ///
     1 "Educación" ///
     2 "Artes y Humanidades" ///
     3 "Ciencias Sociales, Periodismo e Información" ///
     4 "Administración de Empresas y Derecho" ///
     5 "Ciencias Naturales, Matemáticas y Estadística" ///
     6 "Tecnología de la Información y la Comunicación (TIC)" ///
     7 "Ingeniería, Industria y Construcción" ///
     8 "Agropecuario, Silvicultura, Pesca y Veterinaria" ///
     9 "Salud y bienestar" ///
    10 "Servicios", replace

label values cinef13_ci lbl_cinef13_ci
label var cinef13_ci "Campo amplio de educación (ISCED-F 2013, 1 dígito, consecutivo)"

tab2xl cinef13_ci  using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(BRA, replace)
