'''
@file
Programa:           Que resuelve el modelo base del Artículo de Ramakumar1986
                    a traves de Python.
Objetivo:           Incorporar GAMS a Python para usar interfaz gráfica y más
                    operaciones de las librerias de Python.
Fecha:              24-06-2021 V1
Diseñó:             Ing. Sergio Isaías Silva Márquez.
'''
## --------------------V1 fecha 24/06/2021
# Resuelve el problema de GAMS

## --------------------V2 fecha 07/08/2021
# Añade capacidad de escoger cual función será FO (C,CO2)
# Añade interfaz gráfica para el usuario
# Incluye pestañas de configuración
# Versión funcional, escoger a voluntad las energías y las tareas para el diseño
# Guarda archivo "output.txt" con los resultados

## --------------------V3 fecha 19/08/2021
# Añade Función Social y parámetros
# Capacidad de maximinzar o minimizar cualquier función
# Añade "MODEL STATUS" y avisa al usuario cuando el modelo no tiene solución
# Guarda archivo "input.txt" donde se guardan los valores ingresados por el usuario
#
# V3.1
# Agregada la pestaña de Resolver

## --------------------V4 fecha 03/10/2021
# Añadido métodos de optimización multiobjetivo: Lexicográfico y Ponderación
# Se añaden ponderaciones a los criterios sociales con AHP
# Archivo de salida de gams en: C:\Users\USUARIO\AppData\Local\Temp\tmpXXXXXXXX
#

## --------------------V5 fecha 10/10/2021
# Añadido métodos de optimización multiobjetivo: Por Metas (Goals) y Mínima Distancia (Método Generador)
# 
# 
#

## --------------------V6 fecha 16/10/2021
# Añadido métodos de optimización multiobjetivo: Ponderacion 2, Por Compromiso
# Genera grafica con los optimos y archivo con los valores de las FO con los w1,w2,w3
# 
#

from gams import *
import sys
import subprocess
import os
import numpy as np
from tabulate import tabulate
import PySimpleGUI as sg
import operator

## -----------------------------------------Interfaz gráfica-------------------------------------------- ##

#sg.ChangeLookAndFeel('SystemDefaultForReal')
#sg.ChangeLookAndFeel('Dark')
#sg.ChangeLookAndFeel('LightBrown13')
sg.ChangeLookAndFeel('LightGrey6')
sg.popup_quick_message('Cargando parámetros', auto_close=True, non_blocking=True)

def collapse(layout, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this seciton visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key))

## Encabezados de tablas
energias=('Biogas','Fotovoltaicos','Aerogeneración','Hidroeléctrica','Térmica Carbón','Térmica Combustoleo','Gas Natural','Disponible1',
          'Disponible2','Disponible3')
task=('Cocinar', 'Motor DC', 'Electricidad AC', 'Cargar Baterias')

Xenergia=('X '+energias[0],'X '+energias[1],'X '+energias[2],'X '+energias[3],'X '+energias[4],'X '+energias[5],
          'X '+energias[6],'X '+energias[7],'X '+energias[8],'X '+energias[9])
Renergia=('R '+energias[0],'R '+energias[1],'R '+energias[2],'R '+energias[3],'R '+energias[4],'R '+energias[5],
          'R '+energias[6],'R '+energias[7],'R '+energias[8],'R '+energias[9])
Utareas=('U '+task[0], 'U '+task[1], 'U '+task[2], 'U '+task[3])
Ptareas=('P '+task[0], 'P '+task[1], 'P '+task[2], 'P '+task[3])

VidaUtil=('VU '+energias[0],'VU '+energias[1],'VU '+energias[2],'VU '+energias[3],'VU '+energias[4],'VU '+energias[5],
          'VU '+energias[6],'VU '+energias[7],'VU '+energias[8],'VU '+energias[9])
Mtto=('M '+energias[0],'M '+energias[1],'M '+energias[2],'M '+energias[3],'M '+energias[4],'M '+energias[5],
          'M '+energias[6],'M '+energias[7],'M '+energias[8],'M '+energias[9])

## Listas para comparacion

inBiogas = [[sg.Text('X (vol m^3/año)  '),sg.I('102200', size=(13,1), k=Xenergia[0])],
            [sg.Text('R (kWh/m^3)          '),sg.I('5.55',size=(10,1), k=Renergia[0])]            ]
inPV = [[sg.Text('X ( m^2/año)  '),sg.I('1000000', size=(13,1), k=Xenergia[1])],
            [sg.Text('R (kWh/m^2)      '),sg.I('203',size=(10,1), k=Renergia[1])]           ]
inWindTurbine = [[sg.Text('X ( m^2/año)  '),sg.I('1000000', size=(13,1), k=Xenergia[2])],
            [sg.Text('R (kWh/m^2)      '),sg.I('88.74',size=(10,1), k=Renergia[2])]            ]
inWaterHead = [[sg.Text('X (vol m^3/año)  '),sg.I('36500', size=(13,1), k=Xenergia[3])],
            [sg.Text('R (kWh/m^3)          '),sg.I('0.027',size=(10,1), k=Renergia[3])]            ]
inCarbon = [[sg.Text('X (kgcomb/año)  '),sg.I('1000', size=(13,1), k=Xenergia[4])],
            [sg.Text('R (kWh/kg comb)    '),sg.I('5.3982096',size=(10,1), k=Renergia[4])]            ]
inCombustoleo = [[sg.Text('X (barril/año)  '),sg.I('1000', size=(13,1), k=Xenergia[5])],
            [sg.Text('R (kWh/barril)     '),sg.I('1777.0866',size=(10,1), k=Renergia[5])]           ]
inGN = [[sg.Text('X (m^3/año)  '),sg.I('1000', size=(13,1), k=Xenergia[6])],
            [sg.Text('R (kWh/m^3)     '),sg.I('11.5',size=(10,1), k=Renergia[6])]            ]
inDispo1 = [[sg.Text('X (u/año)  '),sg.I('', size=(13,1), k=Xenergia[7])],
            [sg.Text('R (kWh/u)     '),sg.I('',size=(10,1), k=Renergia[7])]            ]
inDispo2 = [[sg.Text('X (u/año)  '),sg.I('', size=(13,1), k=Xenergia[8])],
            [sg.Text('R (kWh/u)     '),sg.I('',size=(10,1), k=Renergia[8])]            ]
inDispo3 = [[sg.Text('X (u/año)  '),sg.I('', size=(13,1), k=Xenergia[9])],
            [sg.Text('R (kWh/u)     '),sg.I('',size=(10,1), k=Renergia[9])]            ]

inUcocinar = [[sg.Text('U (kWh/año)'),sg.I('255500', size=(7,1), k=Utareas[0])],
            [sg.Text('Preqmax (kW)  '),sg.I('100',size=(4,1), k=Ptareas[0])]            ]
inUmotor = [[sg.Text('U (kWh/año)'),sg.I('146000', size=(7,1), k=Utareas[1])],
            [sg.Text('Preqmax (kW)  '),sg.I('80',size=(4,1), k=Ptareas[1])]            ]
inUac = [[sg.Text('U (kWh/año)'),sg.I('54750', size=(7,1), k=Utareas[2])],
            [sg.Text('Preqmax (kW)  '),sg.I('30',size=(4,1), k=Ptareas[2])]            ]
inUbaterias = [[sg.Text('U (kWh/año)'),sg.I('3650', size=(7,1), k=Utareas[3])],
            [sg.Text('Preqmax (kW)  '),sg.I('2',size=(4,1), k=Ptareas[3])]            ]

inBiogasVU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[0])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[0])] ]
inPVVU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[1])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[1])] ]
inWindTurbineVU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[2])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[2])] ]
inWaterHeadVU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[3])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[3])] ]
inCarbonVU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[4])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[4])] ]
inCombustoleoVU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[5])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[5])] ]
inGNVU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[6])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[6])] ]
inDispo1VU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[7])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[7])] ]
inDispo2VU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[8])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[8])] ]
inDispo3VU = [[sg.Text('años vida util'),sg.I('20', size=(4,1), k=VidaUtil[9])],
            [sg.Text(  '% mtto        '),sg.I('5',size=(4,1), k=Mtto[9])] ]

#Contenido de la pestaña 1
tab1_layout =  [
    [sg.Text('Diseño Sustentable de una Central Eléctrica', size=(48, 1), justification='center', font=("Helvetica", 18), relief=sg.RELIEF_RIDGE)],
    [sg.Text('Introducir los parámetros del diseño')],
    [sg.Frame(layout=[
                    [sg.Checkbox(energias[0], size=(22,1),default=True,key=energias[0]),
                     sg.Checkbox(energias[1],size=(24,1),default=True,key=energias[1]),
                     sg.Checkbox(energias[2],size=(22,1),default=True,key=energias[2])],
                    [collapse(inBiogas, 'inBiogas'),
                     collapse(inPV, 'inPV'),
                     collapse(inWindTurbine, 'inWindTurbine')],
                    [sg.Text('_' * 94)],
                    
                    [sg.Checkbox(energias[3],size=(22,1),default=True,key=energias[3]),
                     sg.Checkbox(energias[4],size=(24,1),default=True,key=energias[4]),
                     sg.Checkbox(energias[5],size=(22,1),default=True,key=energias[5])],
                    [collapse(inWaterHead, 'inWaterHead'),
                     collapse(inCarbon, 'inCarbon'),
                     collapse(inCombustoleo, 'inCombustoleo')],
                    [sg.Text('_' * 94)],
                    
                    [sg.Checkbox(energias[6],size=(22,1),default=True,key=energias[6]),
                     sg.Checkbox(energias[7],size=(24,1),key=energias[7]),
                     sg.Checkbox(energias[8],size=(22,1),key=energias[8])],
                    [collapse(inGN, 'inGN'),
                     collapse(inDispo1, 'inDispo1'),
                     collapse(inDispo2, 'inDispo2')],
                    [sg.Text('_' * 94)],

                    [sg.Checkbox(energias[9],size=(22,1),key=energias[9])],
                    [collapse(inDispo3, 'inDispo3')],
                    ],
                     title='Energías disponibles',title_color='green', relief=sg.RELIEF_SUNKEN)],
    ]

#Contenido de la pestaña 2
MAX_ROWS, MAX_COLS, COL_HEADINGS = 10, 4, (' ','      Cocinar', '   Motor DC', '  Electricidad', 'Cargar batería')
ROWS=('Biogas','PV','Aerogeneración','Hidroeléctrica','Carbón','Combustóleo','Gas Natural','Disponible1'
      ,'Disponible2','Disponible3')
eficiencia=((0.6,0  ,0.27,0  ),
            (0  ,0.4,0.9 ,0.6),
            (0  ,0.5,0.8 ,0  ),
            (0  ,0  ,0.6 ,0  ),
            (0.6,0  ,0.49,0  ),
            (0  ,0  ,0.49,0  ),
            (0.6,0  ,0.27,0  ),
            (0  ,0  ,0   ,0  ),
            (0  ,0  ,0   ,0  ),
            (0  ,0  ,0   ,0  ))
diversidad=(1.4,
            1.2,
            1.2,
            1  ,
            1  ,
            1  ,
            1  ,
            1  ,
            1  ,
            1  ,)
tablaef =[[sg.T(q, size=(10, 1)) for w,q in enumerate(COL_HEADINGS)]] + \
	 [[sg.T(ROWS[r], size=(11, 1)) ] + [sg.Input(eficiencia[r][c],size=(11, 1),
                                                     justification='c',
                                                     key=('ef'+str(r), 'ef'+str(c),))
                                            for c in range(MAX_COLS)] for r in range(MAX_ROWS)]

tab2_layout =  [
                 [sg.Text('Detalle de las tareas')],
                 [sg.Frame(layout=[
                                     [sg.Checkbox(task[0], size=(15,1),default=True, key=task[0]),
                                      sg.Checkbox(task[1],size=(15,1),default=True,key=task[1]),
                                      sg.Checkbox(task[2],size=(16,1),default=True,key=task[2]),
                                      sg.Checkbox(task[3],size=(15,1),default=True,key=task[3])],
                                     [collapse(inUcocinar, 'inUcocinar'),
                                      collapse(inUmotor, 'inUmotor'),
                                      collapse(inUac, 'inUac'),
                                      collapse(inUbaterias, 'inUbaterias')],],
                           title='Tareas',title_color='orange',relief=sg.RELIEF_SUNKEN)
                 ],
                 [sg.Frame(layout=[
                                   [collapse(tablaef, '-tablaef-')]],
                                     title='Eficiencia de la tecnología',title_color='green', relief=sg.RELIEF_SUNKEN)
                 ],
                 [sg.Frame(layout=[
                                     [sg.T(energias[0], size=(7,1)),
                                      sg.T(energias[1],size=(10,1)),
                                      sg.T(energias[2],size=(11,1)),
                                      sg.T(energias[3],size=(10,1)),
                                      sg.T(energias[4],size=(12,1))],
                                     [sg.Text(' d'),sg.I(diversidad[0], size=(4,1), k='di '+energias[0]),
                                      sg.Text('  d'),sg.I(diversidad[1], size=(4,1), k='di '+energias[1]),
                                      sg.Text('       d'),sg.I(diversidad[2], size=(4,1), k='di '+energias[2]),
                                      sg.Text('          d'),sg.I(diversidad[3], size=(4,1), k='di '+energias[3]),
                                      sg.Text('       d'),sg.I(diversidad[4], size=(4,1), k='di '+energias[4])],
                                     [sg.T(energias[5], size=(17,1)),
                                      sg.T(energias[6],size=(10,1)),
                                      sg.T(energias[7],size=(10,1)),
                                      sg.T(energias[8],size=(10,1)),
                                      sg.T(energias[9],size=(10,1))],
                                      [sg.Text('    d'),sg.I(diversidad[5], size=(4,1), k='di '+energias[5]),
                                      sg.Text('                     d'),sg.I(diversidad[6], size=(4,1), k='di '+energias[6]),
                                      sg.Text('      d'),sg.I('', size=(4,1), k='di '+energias[7]),
                                      sg.Text('       d'),sg.I('', size=(4,1), k='di '+energias[8]),
                                      sg.Text('       d'),sg.I('', size=(4,1), k='di '+energias[9]),],
                                     ],
                           title='Factor de diversidad',title_color='blue',relief=sg.RELIEF_SUNKEN)
                  ]
                                     
                ]

#Contenido de la pestaña 3 Costos
Pc=((80,0,600,0),(0,10000,9000,9000),(0,5000,5250,0),(0,0,1500,0),(50,0,760,0),(0,0,760,0),
            (90,0,600,0),(0,0,0,0),(0,0,0,0),(0,0,0,0))
tablaPc =[[sg.T(q, size=(10, 1)) for w,q in enumerate(COL_HEADINGS)]] + \
	 [[sg.T(ROWS[r], size=(11, 1)) ] + [sg.Input(Pc[r][c],size=(11, 1),
                                                     justification='c',
                                                     key=('Pc '+str(r), 'Pc '+str(c),))
                                            for c in range(MAX_COLS)] for r in range(MAX_ROWS)]

tab3_layout =  [
                 [sg.Frame(layout=[
                                     [sg.T(energias[0], size=(16,1)),
                                      sg.T(energias[1],size=(17,1)),
                                      sg.T(energias[2],size=(16,1)),
                                      sg.T(energias[3],size=(10,1))],
                                     [collapse(inBiogasVU, 'inBiogasVU'),
                                      collapse(inPVVU, 'inPVVU'),
                                      collapse(inWindTurbineVU, 'inWindTurbineVU'),
                                      collapse(inWaterHeadVU, 'inWaterHeadVU')],
                                     [sg.T(energias[4], size=(16,1)),
                                      sg.T(energias[5],size=(17,1)),
                                      sg.T(energias[6],size=(16,1)),
                                      sg.T(energias[7],size=(10,1))],
                                     [collapse(inCarbonVU, 'inCarbonVU'),
                                      collapse(inCombustoleoVU, 'inCombustoleoVU'),
                                      collapse(inGNVU, 'inGNVU'),
                                      collapse(inDispo1VU, 'inDispo1VU')],
                                     [sg.T(energias[8], size=(16,1)),
                                      sg.T(energias[9],size=(10,1))],
                                     [collapse(inDispo2VU, 'inDispo2VU'),
                                      collapse(inDispo3VU, 'inDispo3VU'),
                                      sg.Text(  'Tasa de intéres  '),sg.I('0.1',size=(4,1), k='Tasainteres')],
                                     ],
                                     title='Costos financieros y mantenimiento',title_color='orange', relief=sg.RELIEF_SUNKEN)
                 ],
                 [sg.Frame(layout=[
                                   [collapse(tablaPc, '-tablaPc-')]],
                                     title='Costos de generar en dolares/kW',title_color='green', relief=sg.RELIEF_SUNKEN)
                 ],
                ]

#Contenido de la pestaña 4 FACTOR DE EMISION
tab4_layout = [
    [sg.Text('Introducir los Factores de Emisión')],
    [sg.Frame(layout=[
                [sg.Text('Biogas', size=(16,1)), sg.Text('Factor de emisión'), sg.I('1.204444',size=(8,1), key='fe_'+energias[0]), sg.Text('kg CO2/m^3', size=(10,1))  ],
                    
                [sg.Text('PV',size=(16,1)), sg.Text('Factor de emisión'), sg.I('5.07500',size=(8,1), key='fe_'+energias[1]), sg.Text('kg CO2/m^2', size=(10,1))],
                    
                [sg.Text('Wind Turbine',size=(16,1)),sg.Text('Factor de emisión'), sg.I('1.24230',size=(8,1), key='fe_'+energias[2]), sg.Text('kg CO2/m^2', size=(10,1))],
                    
                [sg.Text('Water Head',size=(16,1)), sg.Text('Factor de emisión'), sg.I('0.01371',size=(8,1), key='fe_'+energias[3]), sg.Text('kg CO2/m^3', size=(10,1))],
                    
                [sg.Text('Térmica-Carbón',size=(16,1)), sg.Text('Factor de emisión'), sg.I('2.72',size=(8,1), key='fe_'+energias[4]), sg.Text('kg CO2/kgcarbon', size=(13,1))],

                [sg.Text('Térmica-Combustóleo', size=(16,1)),sg.Text('Factor de emisión'), sg.I('492.3836',size=(8,1), key='fe_'+energias[5]), sg.Text('kg CO2/barril', size=(10,1))],

                [sg.Text('Gas Natural',size=(16,1)),           sg.Text('Factor de emisión'), sg.I('2.72',size=(8,1), key='fe_'+energias[6]), sg.Text('kg CO2/m^3', size=(10,1))],
                
                [sg.Text('Disponible1',size=(16,1)),           sg.Text('Factor de emisión'), sg.I('',size=(8,1), key='fe_'+energias[7]),sg.Text('kg CO2/u', size=(10,1))],

                [sg.Text('Disponible2',size=(16,1)),           sg.Text('Factor de emisión'), sg.I('',size=(8,1), key='fe_'+energias[8]),sg.Text('kg CO2/u', size=(10,1))],

                [sg.Text('Disponible3',size=(16,1)),           sg.Text('Factor de emisión'), sg.I('',size=(8,1), key='fe_'+energias[9]),sg.Text('kg CO2/u', size=(10,1))],
                ],
                 title='Factores de emisión',title_color='blue', relief=sg.RELIEF_SUNKEN)]
    ]

#Contenido de la pestaña Factor social
Tfs=((1,1,1,1,1,1,1,5,1,1),
     (1,4,4,1,1,3,1,1,3,5),
     (5,4,3,3,3,2,5,1,4,4),
     (4,2,5,5,5,1,3,2,2,3),
     (3,2,1,5,5,1,1,1,1,1),
     (3,2,1,5,5,1,1,1,1,1),
     (3,2,1,5,5,1,1,1,2,2),
     (0,0,0,0,0,0,0,0,0,0),
     (0,0,0,0,0,0,0,0,0,0),
     (0,0,0,0,0,0,0,0,0,0),
     (0.0809,0.1955,0.0361,0.2731,0.2057,0.0456,0.0485,0.0381,0.0385,0.0376))
aspectos=('1','2','3','4','5','6','7','8','9','10')
MAX_COLSTFS, COL_HEADINGS = 10, ('','','     1','       2','       3','','4','5','6','7','8','9','10')
ROWS=('Biogas','PV','Aerogeneración','Hidroeléctrica','Carbón','Combustóleo','Gas Natural','Disponible1'
      ,'Disponible2','Disponible3','Peso Aspecto ')
tablaTfs =[[sg.T(q, size=(4, 1)) for w,q in enumerate(COL_HEADINGS)]] + \
	 [[sg.T(ROWS[r], size=(11, 1)) ] + [sg.Input(Tfs[r][c],size=(5, 1),
                                                     justification='c',
                                                     key=('fs '+str(r), 'fs '+str(c),))
                                            for c in range(MAX_COLSTFS)] for r in range(MAX_ROWS+1)]
tab5_layout =  [
                 [sg.Frame(layout=[
                                   [collapse(tablaTfs, '-tablaTfs-')],
                                   [sg.Text('-' * 51),sg.Text('Encabezado de la tabla:'),sg.Text('-' * 51)],
                                   [sg.Text('1: Acceso y transferencia de tecnología ',size=(35, 1)),sg.Text('2: Desarrollo de conocimientos científicos ')],
                                   [sg.Text('3: Impacto de belleza paisajística ',size=(35, 1)),sg.Text('4: Costo de producción de energía ')],
                                   [sg.Text('5: Incremento de empleos ',size=(35, 1)),sg.Text('6: Impacto en el uso del suelo ')],
                                   [sg.Text('7: Disminución del impacto hídrico ',size=(35, 1)),sg.Text('8: Se detiene o disminuye la contaminación ')],
                                   [sg.Text('9: Impacto en la flora ',size=(35, 1)),sg.Text('10: Impacto en la fauna ')],
                                   [sg.Text('-' * 55),sg.Text('Escala de medida:'),sg.Text('-' * 55)],
                                   [sg.Text('                            1: Muy poco '),sg.Text('2: Poco '),sg.Text('3: Regular '),sg.Text('4: Bueno '),sg.Text('5: Mucho')],
                                   [sg.Text('-' * 30),sg.Text('Para mayor información revisar el Manual de Usuario'),sg.Text('-' * 30)]
                                   ],
                                     title='Parametros Sociales',title_color='green', relief=sg.RELIEF_SUNKEN)
                 ],
                ]
#Pestaña modelo Optimización simple
tab1 = [[sg.Text('Selecciona el objetivo')],
        [sg.InputCombo(('max', 'min'),size=(15, 1),default_value='min',key='SIMPLE_OBJETIVO'),
         sg.InputCombo(('C', 'CO2','S'), size=(17, 1),default_value='C',key='SIMPLE_FO')]
       ]
wn1=0.6555
wn2=0.1577
wn3=0.1867

#Pestaña modelo Ponderación
tab2 = [  [sg.Text('C w1'),sg.Input(str(wn1),key='wn1',size=(6,1), enable_events=True),
              sg.Text('CO2 w2'),sg.Input(str(wn2),key='wn2',size=(6,1), enable_events=True),
              sg.Text('S w3'),sg.Input(str(wn3),key='wn3',size=(6,1), enable_events=True)
           ],
           [sg.Button('Corregir          '),
            sg.Text(size=(25,1), key='-OUTPUT-')]
        ]

#Pestaña modelo Lexicográfico
tab3 = [[sg.Text('Selecciona el objetivo'),sg.InputCombo(('maxS-minC-minCO2','maxS-minCO2-minC','minC-minCO2-maxS',
                                                          'minC-maxS-minCO2','minCO2-minC-maxS','minCO2-maxS-minC'),
                                                         size=(17, 1),default_value='maxS-minC-minCO2',key='LEX_FO')],
        [sg.Text('Holgura Lexicografica %',size=(18,1)),
         sg.Text('FO1:'), sg.I('50',size=(4,1), key='HFO1'),
         sg.Text('FO2:'), sg.I('50',size=(4,1), key='HFO2')]]

#Pestaña modelo Por Metas
tab4 = [[sg.Text('Introduce las metas para cada Función',size=(30,1))],
        [sg.Text('G1 C:'), sg.I('149010',size=(8,1), key='G1'),
         sg.Text('G2 CO2:'), sg.I('174190',size=(8,1), key='G2'),
         sg.Text('G3 S:'), sg.I('90',size=(3,1), key='G3')]]

#Pestaña modelo Mínima Distancia
tab5 = [[sg.Text('No es necesario configurar')]]

#Pestaña modelo Ponderación Múltiples soluciones
tab6 = [[sg.Text('Numero de puntos:'), sg.I('11',size=(4,1), key='iteracion')]]

#Pestaña modelo Por Compromiso Múltiples soluciones
tab7 = [[sg.Text('Numero de puntos:'), sg.I('11',size=(4,1), key='iteracion1')]]

#Pestaña modelo e-constraint Múltiples soluciones
tab8 = [[sg.Text('Numero de puntos:'), sg.I('11',size=(4,1), key='iteracion2')]]

#Pestaña modelo e-constraint Múltiples soluciones
tab9 = [[sg.Text('Numero de iteraciones:'), sg.I('11',size=(4,1), key='iteracion3')]]

tab_group_layout = [[sg.Tab('Opt. simple', tab1,visible=False, key='-TAB1-'),
                     sg.Tab('Ponderación', tab2,visible=False, key='-TAB2-'),
                     sg.Tab('Lexicográfico', tab3,visible=False, key='-TAB3-'),
                     sg.Tab('Por Metas', tab4,visible=False, key='-TAB4-'),
                     sg.Tab('Mín. Distancia', tab5,visible=False, key='-TAB5-'),
                     sg.Tab('Pond. Múlt. Sol', tab6,visible=False, key='-TAB6-'),
                     sg.Tab('Por Compromiso', tab7,visible=False, key='-TAB7-'),
                     sg.Tab('e-constraint', tab8,visible=False, key='-TAB8-'),
                     sg.Tab('e-constraint+compromiso', tab9,visible=False, key='-TAB9-')
                     ]]

tab_group_master = sg.TabGroup(tab_group_layout,enable_events=True,size=(640, 60),  key='-TABGROUP-')

#Pestaña de resolución
tab6_layout =  [ [sg.Text('En este apartado selecciona la Función Objetivo a optimizar')],
                 [sg.Column([
                             [sg.Frame(layout=[
                                               [sg.Text('C:     Costos en dolares por año')],
                                               [sg.Text('CO2: Emisiones de CO2 en toneladas por año')],
                                               [sg.Text('S:     Factor social medida en puntos sociales por año')]
                                               ],
                                       title='Funciones',title_color='green', pad=(20,0),relief=sg.RELIEF_SUNKEN
                                       ),
                              sg.Frame(layout=[
                                               [sg.Text('1: Optimización Simple')],
                                               [sg.Text('2: Ponderación')],
                                               [sg.Text('3: Lexicográfico')],
                                               [sg.Text('4: Por Metas')],
                                               [sg.Text('5: Mínima Distancia')],
                                               [sg.Text('6: Ponderación Múltiples soluciones')],
                                               [sg.Text('7: Por Compromiso')],
                                               [sg.Text('8: e-constraint')],
                                               [sg.Text('9: e-constraint + por compromiso')]
                                               ],
                                       title='Métodos',title_color='red',pad=(20,0), relief=sg.RELIEF_SUNKEN
                                       )
                              ]
                             ], pad=(0,0))
                  ],
                 
                 [sg.Column([
                             [sg.Text('Método a desempeñar:'),
                              sg.InputCombo(('1','2','3', '4', '5','6','7','8','9'),size=(15, 1),default_value='1',key='OBJETIVO'),
                              sg.Button('Select')],
                             [tab_group_master]
                             ],pad=(20,0)
                            )
                  ],
                 
                 [sg.Text('')],
                 [sg.Text('Decimales: '),sg.I('3',size=(3,1), key='redondeo')]  ,          
                 [sg.Text('-' * 164)],
                 [sg.Text('-' * 65),sg.Text('>'),sg.Submit('Optimizar',tooltip='Iniciar el cálculo'),sg.Text('<'),sg.Text('-' * 65)] ,
                 [sg.Text('-' * 164)],
                 [sg.Text('Los datos ingresados se guardan en "input.txt"')],
                 [sg.Text('La solución óptima se guarda en: '),sg.I('output',size=(20,1), key='archivo'),
                  sg.Text('.txt')]
                ]

#Contenido de la ventana
layout = [[sg.TabGroup([[sg.Tab('Fuentes de Energía', tab1_layout), sg.Tab('Tareas', tab2_layout),
                         sg.Tab('Costos', tab3_layout),sg.Tab('Ambiental', tab4_layout),
                         sg.Tab('Social', tab5_layout),sg.Tab('Resolución', tab6_layout)]],selected_title_color='brown',key='pestaña')]]

window = sg.Window('Ventana de Diseño V6', layout, default_element_size=(50, 1), grab_anywhere=False)
tab_keys = ('-TAB1-','-TAB2-','-TAB3-', '-TAB4-', '-TAB5-','-TAB6-','-TAB7-','-TAB8-','-TAB9-') 
while True:             # Event Loop
    event, valores = window.read()
    #print(event, values)
    wn1=valores['wn1']
    wn2=valores['wn2']
    wn3=valores['wn3']
    if wn1=='' or wn1=='.':
        wn1=0
    if wn2=='' or wn2=='.':
        wn2=0
    if wn3=='' or wn3=='.':
        wn3=0
    wn1=float(wn1)
    wn2=float(wn2)
    wn3=float(wn3)
    
    if event == sg.WIN_CLOSED or event == 'Optimizar':
        break
    
    if event == 'Select':
        window[tab_keys[int(valores['OBJETIVO'])-1]].select()

    if event == 'Corregir          ' and ((wn1+wn2+wn3)>1.0001 or (wn1+wn2+wn3)<0.99):
        output_window = window
        wn1=1/3
        wn2=1/3
        wn3=1/3
        output_window['-OUTPUT-'].update('Valores Ajustados')
        output_window['wn1'].update(str(wn1))
        output_window['wn2'].update(str(wn2))
        output_window['wn3'].update(str(wn3))
    else:
        output_window = window
        if ((wn1+wn2+wn3)>1.0001 or (wn1+wn2+wn3)<0.99):
            output_window['-OUTPUT-'].update('Debes corregir: '+ str(wn1+wn2+wn3))
        else:    
            output_window['-OUTPUT-'].update('Correcto: '+ str(wn1+wn2+wn3))

window.close()

#################################################################################################
## ----------------Se obtienen los valores ingresados por el usuario-------------------------- ##

Recursos={}
for i in valores:
    if valores.get(i)==True:
        if i in energias:
            Recursos.setdefault(i,1)
Recursos_i=list(Recursos.keys())

Tareas={}
for i in valores:
    if valores.get(i)==True:
        if i in task:
            Tareas.setdefault(i,1)
Tareas_j=list(Tareas.keys())

xi={}
for i in Recursos_i:
    if 'X '+i in valores:
        xi.setdefault(i,float(valores.get('X '+i)))
Ri={}
for i in Recursos_i:
    if 'R '+i in valores:
        Ri.setdefault(i,float(valores.get('R '+i)))
Uj={}
for j in Tareas_j:
    if 'U '+j in valores:
        Uj.setdefault(j,float(valores.get('U '+j)))
Poj={}
for j in Tareas_j:
    if 'P '+j in valores:
        Poj.setdefault(j,float(valores.get('P '+j)))

#Creación matriz eficiencia
eficiencian = [[valores[('ef'+str(row),'ef'+str(col))] for col in range(MAX_COLS)] for row in range(MAX_ROWS)]
matrizn={}
for x,y in enumerate(energias):
	for w,q in enumerate(task):
		matrizn.setdefault((y,q),eficiencian[x][w])
nij={}
for q,w in  matrizn:
    for e in Recursos_i:
        for r in Tareas_j:
            if (q,w)==(e,r):
                nij.setdefault((q,w),float(matrizn.get((q,w))))
#Creación matriz kij
k1ij={}  
for i in Recursos_i:
    for j in Tareas_j:
        if float(nij.get((i,j)))>0:
            k1ij.setdefault((i,j),float(Uj.get(j))/(8760*float(Poj.get(j))))
        else:
            k1ij.setdefault((i,j),0.00000000000001)

#Creación matriz Pcij
Pcn = [[valores[('Pc '+str(row),'Pc '+str(col))] for col in range(MAX_COLS)] for row in range(MAX_ROWS)]
matrizpc={}  
for x,y in enumerate(energias):
	for w,q in enumerate(task):
		matrizpc.setdefault((y,q),Pcn[x][w])
Pcij={}
for q,w in  matrizpc:
    for e in Recursos_i:
        for r in Tareas_j:
            if (q,w)==(e,r):
                Pcij.setdefault((q,w),float(matrizpc.get((q,w))))
#Creación matriz n(i,j) vida útil en años
VUn={}  #########VidaUtil
for x,y in enumerate(energias):
	for w,q in enumerate(task):  
		VUn.setdefault((y,q),valores.get('VU '+y))
VU={}
for q,w in  VUn:
    for e in Recursos_i:
        for r in Tareas_j:
            if (q,w)==(e,r):
                VU.setdefault((q,w),float(VUn.get((q,w))))

#Creación matriz m(i,j) % para mantenimiento
mn={}  #########VidaUtil
for x,y in enumerate(energias):
	for w,q in enumerate(task):  
		mn.setdefault((y,q),valores.get('M '+y))
mij={}
for q,w in  mn:
    for e in Recursos_i:
        for r in Tareas_j:
            if (q,w)==(e,r):
                mij.setdefault((q,w),float(mn.get((q,w)))/100)
                
#Creación matriz t(i,j) tasa de carga
tasa=float(valores.get('Tasainteres'))
factor1=(1+tasa)
tij={}
for i in Recursos_i:
    for j in Tareas_j:
        tij.setdefault((i,j),(tasa*(factor1**VU.get((i,j))))/((factor1**VU.get((i,j)))-1)+mij.get((i,j)) )

#Creación matriz a(i,j)
aij={}
for i in Recursos_i:
    for j in Tareas_j:
        if k1ij.get((i,j))==1:
            aij.setdefault((i,j),0)
        else:
            aij.setdefault((i,j),(tij.get((i,j))*Pcij.get((i,j)))/(8760*k1ij.get((i,j)))    )

#Creación matriz k(i)
ki={}
for i in Recursos_i:
    suma=0
    cuenta=0
    for j in Tareas_j:
        if k1ij.get((i,j))==1:
            suma=suma+0
        else:
            suma=suma+k1ij.get((i,j))
            cuenta=cuenta+1
    ki.setdefault(i,suma/cuenta)

#Creación matriz d(i)
di={}
for i in Recursos_i:
        di.setdefault(i,float(valores.get('di '+i)))

#Creción de la parte social
Aspectos_ii=['1','2','3','4','5','6','7','8','9','10']
Socialii = [[valores[('fs '+str(row),'fs '+str(col))] for col in range(MAX_COLSTFS)] for row in range(MAX_ROWS+1)]
matrizsocial={}  
for x,y in enumerate(energias):
	for w,q in enumerate(Aspectos_ii):
		matrizsocial.setdefault((y,q),Socialii[x][w])
fsiii={}
for q,w in  matrizsocial:
    for e in Recursos_i:
        for r in Aspectos_ii:
            if (q,w)==(e,r):
                fsiii.setdefault((q,w),float(matrizsocial.get((q,w))))
pond_ii={}
for x,y in enumerate(Aspectos_ii):
    pond_ii.setdefault(str(y),float(Socialii[10][x]))

HOL1=1+float(valores.get('HFO1'))/100
HOL2=1+float(valores.get('HFO2'))/100

wn1=float(valores.get('wn1'))
wn2=float(valores.get('wn2'))
wn3=float(valores.get('wn3'))

g1=float(valores.get('G1'))
g2=float(valores.get('G2'))
g3=float(valores.get('G3'))

OBJETIVO=valores.get('SIMPLE_OBJETIVO')
METODO=valores.get('OBJETIVO')
iteraciones=[]

if METODO=='1':
    FO=valores.get('SIMPLE_FO')
if METODO=='2':
    FO='Ponderacion'
if METODO=='3':
    FO=valores.get('LEX_FO')
if METODO=='4':
    FO='GOALS'
if METODO=='5':
    FO='MINDISTANCIA'
if METODO=='6':
    FO='POND2'
    iteracion=int(valores.get('iteracion'))
    for t in range(iteracion):
        iteraciones.append(str(t+1))
if METODO=='7':
    FO='PORCOMPROMISO'
    iteracion=int(valores.get('iteracion1'))
    for t in range(iteracion):
        iteraciones.append(str(t+1))
if METODO=='8':
    FO='e-constraint'
    iteracion=int(valores.get('iteracion2'))
    for t in range(iteracion):
        iteraciones.append(str(t+1))
if METODO=='9':
    FO='e-constraint + por compromiso'
    iteracion=int(valores.get('iteracion3'))
    for t in range(iteracion):
        iteraciones.append(str(t+1))

        

#Creacion matriz Factor de Emision
feij= {}
for i in Recursos_i:
    for j in Tareas_j:
        if 'fe_'+i in valores:
            feij.setdefault((i,j),float(valores.get('fe_'+i)))

#################################################################################################

def get_model_text():
    return '''
  Sets
       i   Recursos
       j   Tareas
       ii  Aspectos
       it1  iteraciones 
       it2  iteraciones 

  Parameters
       x(i)    Capacidad de las fuentes
       R(i)    Factor de energía
       U(j)    Energia de tarea por año
       Po(j)   Máxima potencia de salida
       k(i)    Carga de la planta
       d(i)    Factor de diversidad
       n(i,j)  Eficiencia de las combinaciones de tareas y recursos
       k1(i,j) Factor de carga tareas y recursos
       a(i,j)  Valores de costo en $ por kWh
       fe(i,j) Factor de Emision
       fs(i,ii)  Factor de Social
       pond(ii) Peso de los factores sociales
       HFO1    HOLGURA FO1
       HFO2    HOLGURA FO2
       FCup    Valor up de C    /180000/
       FCO2up  Valor up de CO2  /130000/
       FSup    Valor up de S    /95/
       FClow   Valor low de C   /140000/
       FCO2low  Valor low de CO2 /97500/
       FSlow   Valor low de S   /80/
       w1      Factor de peso
       w2      Factor de peso
       w3      Factor de peso
       
       G1      Meta
       G2      Meta
       G3      Meta
       G1n     META 1N /0.5/
       G2n     META 2N /0.5/
       G3n     META 3N /0.5/

       Z1nOP   UTOPICO  /0/
       Z2nOP   UTOPICO  /0/
       Z3nOP   UTOPICO  /0/
       eC      epsilon  /0/
       eCO2    epsilon  /0/
       eS      epsilon /0/
       ;

       
$if not set gdxincname $abort 'no include file name for data file provided'
$gdxin %gdxincname%
$load i j ii x R U Po k d n k1 a fe fs pond HFO1 HFO2 w1 w2 w3 G1 G2 G3 it1 it2
$gdxin

  Variables
       CO2       EmisionesCO2
       C         Costo anual
       S         Peso Social
       FOSmax    Valor max Z1
       FOCmax    Valor max Z2
       FOCO2max  Valor max Z3
       Z         Funcion objetivo normalizada
       Z1n       Objetivo C normalizado
       Z2n       Objetivo CO2 normalizado
       Z3n       Objetivo S normalizado;
       
  Positive Variable q(i,j);

  Equations
     cost        Costos
     rest1(j)    Energia
     rest2(i)    Recurso
     rest3(i)    Potencia
     ambiental   Emisiones
     social      PonderajeSocial
     RlexS       Restriccion lexicografica
     RlexC       Restriccion lexicografica
     RlexCO2     Restriccion lexicografica
     FOn         FO normalizada
     FO1n        FC normalizado
     FO2n        FCO2 normalizado
     FO3n        FS normalizado
     GOAL        FO Por Metas
     MINDIS      FO Minima Distancia
     Reps1       Restriccion C
     Reps2       Restriccion CO2
     Reps3       Restriccion S
     ;

  rest1(j) ..   sum(i,R(i)*n(i,j)*q(i,j))  =e=     U(j);
  rest2(i) ..   sum(j, q(i,j))  =l=  x(i) ;
  rest3(i) ..   (1/(k(i)))*sum(j, q(i,j))-(1/(d(i)))*sum(j, q(i,j)/k1(i,j)) =g= 0 ;

  cost ..        C   =e=  sum(i, R(i)*sum(j,a(i,j)*q(i,j))) ;
  ambiental ..   CO2 =e=sum((i,j),q(i,j)*fe(i,j));
  social..       S   =e=10*sum(i,sum(j,R(i)*q(i,j)*n(i,j)/U(j))*sum(ii,fs(i,ii)*pond(ii)));

  RlexS..    S=G=FOSmax;
  RlexC..    C=L=FOCmax;
  RlexCO2..  CO2=L=FOCO2max;

  FOn..     Z =E= Z1n*w1+Z2n*w2+Z3n*w3;
  FO1n..    Z1n =E= (C-FClow)/(FCup-FClow);
  FO2n..    Z2n =E= (CO2-FCO2low)/(FCO2up-FCO2low);
  FO3n..    Z3n =E= (FSup-S)/(FSup-FSlow);

  GOAL..    Z =E= abs(Z1n - G1n) + abs(Z2n - G2n) + abs(Z3n - G3n);

  MINDIS..  Z =E= sqrt( (Z1n)**2 + (Z2n)**2 + (Z3n)**2 );

  Model modeloSIMPLE /cost,rest1,rest2,rest3,ambiental,social/ ;
  SOLVE modeloSIMPLE using LP min C;   FClow=C.L;
  SOLVE modeloSIMPLE using LP max C;   FCup=C.L;
  SOLVE modeloSIMPLE using LP min CO2;   FCO2low=CO2.L;
  SOLVE modeloSIMPLE using LP max CO2;   FCO2up=CO2.L;
  SOLVE modeloSIMPLE using LP min S;   FSlow=S.L;
  SOLVE modeloSIMPLE using LP max S;   FSup=S.L;

  G1n = (G1-FClow)/(FCup-FClow);
  G2n = (G2-FCO2low)/(FCO2up-FCO2low);
  G3n = (FSup-G3)/(FSup-FSlow);

  Reps1.. C   =L= eC;
  Reps2.. CO2 =L= eCO2;
  Reps3.. S   =G= eS; 
  
  Model GOALS /cost,rest1,rest2,rest3,ambiental,social,FO1n,FO2n,FO3n,GOAL/;

  Model MIND  /cost,rest1,rest2,rest3,ambiental,social,FO1n,FO2n,FO3n,MINDIS/;
  
  Model modeloS    /modeloSIMPLE,RlexS/;
  
  Model modeloSC   /modeloS,RlexC/;
  Model modeloSCO2 /modeloS,RlexCO2/;
  
  Model modeloC    /modeloSIMPLE,RlexC/;
  
  Model modeloCCO2 /modeloC,RlexCO2/;
  Model modeloCS   /modeloC,RlexS/;
  
  Model modeloCO2  /modeloSIMPLE,RlexCO2/;
  
  Model modeloCO2C /modeloCO2,RlexC/;
  Model modeloCO2S /modeloCO2,RlexS/;

  Model ponderado  /modeloSIMPLE,FOn,FO1n,FO2n,FO3n/;
  
  Scalar ms 'model status', ss 'solve status'; '''

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ws = GamsWorkspace(system_directory = sys.argv[1])
    else:
        #ws = GamsWorkspace(system_directory ='/opt/gams/gams36.2_linux_x64_64_sfx')
        ws = GamsWorkspace()
    
    # create new GamsDatabase instance
    db = ws.add_database()
    
    i = db.add_set("i", 1, "Recursos")
    for p in Recursos_i:
        i.add_record(p)
    
    j = db.add_set("j", 1, "Tareas")
    for T in Tareas_j:
        j.add_record(T)

    ii = db.add_set("ii", 1, "Aspectos")
    for T in Aspectos_ii:
        ii.add_record(T)
        
    x = db.add_parameter_dc("x", [i], "Capacidad de las fuentes")
    for p in Recursos_i:
        x.add_record(p).value = xi[p]

    R = db.add_parameter_dc("R", [i], "Factor de energia")
    for p in Recursos_i:
        R.add_record(p).value = Ri[p]

    U = db.add_parameter_dc("U", [j], "Energia de tarea por año")
    for T in Tareas_j:
        U.add_record(T).value = Uj[T]

    Po = db.add_parameter_dc("Po", [j], "Máxima potencia de salida")
    for T in Tareas_j:
        Po.add_record(T).value = Poj[T]

    k = db.add_parameter_dc("k", [i], "Carga de la planta")
    for p in Recursos_i:
        k.add_record(p).value = ki[p]

    d = db.add_parameter_dc("d", [i], "Factor de diversidad")
    for p in Recursos_i:
        d.add_record(p).value = di[p]        
    
    n = db.add_parameter_dc("n", [i,j], "Eficiencia de las combinaciones de tareas y recursos")
    for s, v in iter(nij.items()):
        n.add_record(s).value = v

    k1 = db.add_parameter_dc("k1", [i,j], "Factor de carga tareas y recursos")
    for s, v in iter(k1ij.items()):
        k1.add_record(s).value = v

    a = db.add_parameter_dc("a", [i,j], "Valores de costo capital en $ por kW")
    for s, v in iter(aij.items()):
        a.add_record(s).value = v

    fe = db.add_parameter_dc("fe", [i,j], "Factor de emision")
    for s, v in iter(feij.items()):
        fe.add_record(s).value = v

    fs = db.add_parameter_dc("fs", [i,ii], "Factor de Social")
    for s, v in iter(fsiii.items()):
        fs.add_record(s).value = v

    pond = db.add_parameter_dc("pond", [ii], "Peso de los factores sociales")
    for p in Aspectos_ii:
        pond.add_record(p).value = pond_ii[p]
        
    HFO1= db.add_parameter("HFO1", 0, "HOLGURA FO1")
    HFO1.add_record().value = HOL1
    
    HFO2= db.add_parameter("HFO2", 0, "HOLGURA FO2")
    HFO2.add_record().value = HOL2

    w1= db.add_parameter("w1", 0, "Factor de peso")
    w1.add_record().value = wn1

    w2= db.add_parameter("w2", 0, "Factor de peso")
    w2.add_record().value = wn2

    w3= db.add_parameter("w3", 0, "Factor de peso")
    w3.add_record().value = wn3

    gg1= db.add_parameter("G1", 0, "Meta")
    gg1.add_record().value = g1

    gg2= db.add_parameter("G2", 0, "Meta")
    gg2.add_record().value = g2

    gg3= db.add_parameter("G3", 0, "Meta")
    gg3.add_record().value = g3

    it1 = db.add_set("it1", 1, "iteraciones")
    for T in iteraciones:
        it1.add_record(T)

    it2 = db.add_set("it2", 1, "iteraciones")
    for T in iteraciones:
        it2.add_record(T)

    #Configuración para resolver el código correctamente
    cp = ws.add_checkpoint()
    prog = ws.add_job_from_string(get_model_text())
    opt = ws.add_options()
    opt.defines["gdxincname"] = db.name
    opt.all_model_types = "cplex"
    prog.run(opt, databases = db, checkpoint=cp)
    
    # Minimiza una función a voluntad, C, CO2, S
    if (FO=='C' and METODO=='1'):
        prog = ws.add_job_from_string("solve modeloSIMPLE "+OBJETIVO+" C use lp; ms=modeloSIMPLE.modelstat; ss=modeloSIMPLE.solvestat;", cp)
    if (FO=='CO2' and METODO=='1'):
        prog = ws.add_job_from_string("solve modeloSIMPLE "+OBJETIVO+" CO2 use lp; ms=modeloSIMPLE.modelstat; ss=modeloSIMPLE.solvestat;", cp)
    if (FO=='S' and METODO=='1'):
        prog = ws.add_job_from_string("solve modeloSIMPLE "+OBJETIVO+" S use lp; ms=modeloSIMPLE.modelstat; ss=modeloSIMPLE.solvestat;", cp)

    # Optimización mediante método Ponderación    
    if (FO=='Ponderacion' and METODO=='2'):
        prog = ws.add_job_from_string("solve ponderado using lp min Z; ms=ponderado.modelstat; ss=ponderado.solvestat;", cp)    
        
    # Optimización mediante método lexicográfico
    if (FO=='maxS-minC-minCO2' and METODO=='3'):
        prog = ws.add_job_from_string("solve modeloSIMPLE max S use lp; ms=modeloSIMPLE.modelstat; ss=modeloSIMPLE.solvestat; FOSmax.LO = S.L*HFO1-S.L;"+
                                      "Solve modeloS using lp min C; ms=modeloS.modelstat; ss=modeloS.solvestat; FOCmax.UP = C.L*HFO2;"+
                                      "Solve modeloSC using lp min CO2; ms=modeloSC.modelstat; ss=modeloSC.solvestat;", cp)
    if (FO=='maxS-minCO2-minC' and METODO=='3'):
        prog = ws.add_job_from_string("solve modeloSIMPLE max S use lp; ms=modeloSIMPLE.modelstat; ss=modeloSIMPLE.solvestat; FOSmax.LO = S.L*HFO1-S.L;"+
                                      "Solve modeloS using lp min CO2; ms=modeloS.modelstat; ss=modeloS.solvestat; FOCO2max.UP = CO2.L*HFO2;"+
                                      "Solve modeloSCO2 using lp min C; ms=modeloSCO2.modelstat; ss=modeloSCO2.solvestat;", cp)
    if (FO=='minC-minCO2-maxS' and METODO=='3'):
        prog = ws.add_job_from_string("solve modeloSIMPLE min C use lp; ms=modeloSIMPLE.modelstat; ss=modeloSIMPLE.solvestat; FOCmax.UP = C.L*HFO1;"+
                                      "Solve modeloC using lp min CO2; ms=modeloC.modelstat; ss=modeloC.solvestat; FOCO2max.UP = CO2.L*HFO2;"+
                                      "Solve modeloCCO2 using lp max S; ms=modeloCCO2.modelstat; ss=modeloCCO2.solvestat;", cp)
    if (FO=='minC-maxS-minCO2' and METODO=='3'):
        prog = ws.add_job_from_string("solve modeloSIMPLE min C use lp; ms=modeloSIMPLE.modelstat; ss=modeloSIMPLE.solvestat; FOCmax.UP = C.L*HFO1;"+
                                      "Solve modeloC using lp max S; ms=modeloC.modelstat; ss=modeloC.solvestat; FOSmax.LO = S.L*HFO2;"+
                                      "Solve modeloCS using lp min CO2; ms=modeloCS.modelstat; ss=modeloCS.solvestat;", cp)
    if (FO=='minCO2-minC-maxS' and METODO=='3'):
        prog = ws.add_job_from_string("solve modeloSIMPLE min CO2 use lp; ms=modeloSIMPLE.modelstat; ss=modeloSIMPLE.solvestat; FOCO2max.UP = CO2.L*HFO1;"+
                                      "Solve modeloCO2 using lp min C; ms=modeloCO2.modelstat; ss=modeloCO2.solvestat; FOCmax.UP = C.L*HFO2;"+
                                      "Solve modeloCO2C using lp max S; ms=modeloCO2C.modelstat; ss=modeloCO2C.solvestat;", cp)
    if (FO=='minCO2-maxS-minC' and METODO=='3'):
        prog = ws.add_job_from_string("solve modeloSIMPLE min CO2 use lp; ms=modeloSIMPLE.modelstat; ss=modeloSIMPLE.solvestat; FOCO2max.UP = CO2.L*HFO1;"+
                                      "Solve modeloCO2 using lp max S; ms=modeloCO2.modelstat; ss=modeloCO2.solvestat; FOSmax.LO = S.L*HFO2;"+
                                      "Solve modeloCO2S using lp min C; ms=modeloCO2S.modelstat; ss=modeloCO2S.solvestat;", cp)

    # Optimización mediante método por metas
    if (FO=='GOALS' and METODO=='4'):
        prog = ws.add_job_from_string("option dnlp=CONOPT4;solve GOALS using dnlp min Z; ms=GOALS.modelstat; ss=GOALS.solvestat;", cp)

    # Optimización mediante método mínima distancia
    if (FO=='MINDISTANCIA' and METODO=='5'):
        prog = ws.add_job_from_string("solve MIND using nlp min Z; ms=MIND.modelstat; ss=MIND.solvestat;", cp)

    # Optimización mediante método ponderacion
    instrucciones6=''' parameter profitz1(it2,it1),profitz2(it2,it1),profitz3(it2,it1),profitw1,profitw2,profitw3
          CP valorpasado /0/,CO2P valorpasado /0/,SP valorpasado /0/,
          CA valorACTUAL /0/,CO2A valorACTUAL /0/,SA valorACTUAL /0/;
loop(it1,
if((ord(it1)-1)/(card(it1)-1)=0,
 w1=1e-10
else
 w1=(ord(it1)-1)/(card(it1)-1);
);
   loop(it2,
       if(ord(it2)<=ord(it1),
         w2 = 1e-10;

       else
         w2 = (ord(it2)-ord(it1))/(card(it2)-1)
         );
       if((1-w1-w2)=0,
         w3=1e-10
       else
         w3= 1-w1-w2;
        );
       if(ord(it2)>=ord(it1),
          solve ponderado using LP min Z;
          CA=C.L;
          CO2A=CO2.L;
          SA=S.L;       
          if( ((CA <> CP) AND (CO2A <> CO2P) AND (SA <> SP)) ,
              CP=CA; CO2P=CO2A; SP=SA;
              profitw1(it2,it1)=w1;
              profitw2(it2,it1)=w2;
              profitw3(it2,it1)=w3;
              profitz1(it2,it1)=C.L;
              profitz2(it2,it1)=CO2.L;
              profitz3(it2,it1)=S.L;
             );
         );
       );
);
execute_unload "results.gdx" FClow,FCup,FCO2low,FCO2up,FSlow,FSup,profitz1,profitz2,profitz3,
                             profitw1,profitw2,profitw3
'''  
    if (FO=='POND2' and METODO=='6'):
        prog = ws.add_job_from_string(instrucciones6, cp)

# Optimización mediante método POR COMPROMISO
    instrucciones7='''parameter C11   /0/,   C12 /0/,   C13 /0/,
          CO221 /0/, CO222 /0/, CO223 /0/,
          S31   /0/,   S32 /0/,   S33 /0/;
SOLVE modeloSIMPLE using LP min C;
   FClow=C.L;     C11=C.L;     C12=CO2.L;   C13=S.L;
SOLVE modeloSIMPLE using LP min CO2;
   FCO2low=CO2.L; CO221=CO2.L; CO222=CO2.L; CO223=S.L;
SOLVE modeloSIMPLE using LP max S;
   FSup=S.L;      S31=C.L;     S32=CO2.L;   S33=S.L;
*SELECCIONA FSlow DE LA MATRIZ
IF(C13>CO223,
   FSlow=CO223;
ELSE
   IF(C13>S33,
     FSlow=S33;
   ELSE
     FSlow=C13;
   );
);
*SELECCIONA FCup DE LA MATRIZ
IF(C11<CO221,
   FCup=CO221;
ELSE
   IF(C11<S31,
     FCup=S31;
   ELSE
     FCup=C11;
   );
);

*SELECCIONA FCO2up DE LA MATRIZ
IF(C12<CO222,
   FCO2up=CO222;
ELSE
   IF(C12<S32,
     FCO2up=S32;
   ELSE
     FCO2up=C12;
   );
);

parameter profitz1(it2,it1),profitz2(it2,it1),profitz3(it2,it1),profitw1,profitw2,profitw3
          CP valorpasado /0/,CO2P valorpasado /0/,SP valorpasado /0/,
          CA valorACTUAL /0/,CO2A valorACTUAL /0/,SA valorACTUAL /0/;
loop(it1,
if((ord(it1)-1)/(card(it1)-1)=0,
 w1=1e-10
else
 w1=(ord(it1)-1)/(card(it1)-1);
);
   loop(it2,
       if(ord(it2)<=ord(it1),
         w2 = 1e-10;
       else
         w2 = (ord(it2)-ord(it1))/(card(it2)-1)
         );
       if((1-w1-w2)=0,
         w3=1e-10
       else
         w3= 1-w1-w2;
        );
       if(ord(it2)>=ord(it1),
          solve ponderado using LP min Z;
          CA=C.L;
          CO2A=CO2.L;
          SA=S.L;       
          if( ((CA <> CP) AND (CO2A <> CO2P) AND (SA <> SP)) ,
              CP=CA; CO2P=CO2A; SP=SA;
              profitw1(it2,it1)=w1;
              profitw2(it2,it1)=w2;
              profitw3(it2,it1)=w3;
              profitz1(it2,it1)=C.L;
              profitz2(it2,it1)=CO2.L;
              profitz3(it2,it1)=S.L;
             );
         );
       );
);
execute_unload "results.gdx" FClow,FCup,FCO2low,FCO2up,FSlow,FSup,profitz1,profitz2,profitz3,
                             profitw1,profitw2,profitw3
'''  
    if (FO=='PORCOMPROMISO' and METODO=='7'):
        prog = ws.add_job_from_string(instrucciones7, cp)

# Optimización mediante método e-constraint
    instrucciones8='''parameter C11   /0/,   C12 /0/,   C13 /0/,
          CO221 /0/, CO222 /0/, CO223 /0/,
          S31   /0/,   S32 /0/,   S33 /0/;
SOLVE modeloSIMPLE using LP min C;
   FClow=C.L;     C11=C.L;     C12=CO2.L;   C13=S.L;
SOLVE modeloSIMPLE using LP min CO2;
   FCO2low=CO2.L; CO221=CO2.L; CO222=CO2.L; CO223=S.L;
SOLVE modeloSIMPLE using LP max S;
   FSup=S.L;      S31=C.L;     S32=CO2.L;   S33=S.L;

*SELECCIONA FSlow DE LA MATRIZ
IF(C13>CO223,
   FSlow=CO223;
ELSE
   IF(C13>S33,
     FSlow=S33;
   ELSE
     FSlow=C13;
   );
);
*SELECCIONA FCup DE LA MATRIZ
IF(C11<CO221,
   FCup=CO221;
ELSE
   IF(C11<S31,
     FCup=S31;
   ELSE
     FCup=C11;
   );
);
*SELECCIONA FCO2up DE LA MATRIZ
IF(C12<CO222,
   FCO2up=CO222;
ELSE
   IF(C12<S32,
     FCO2up=S32;
   ELSE
     FCO2up=C12;
   );
);


*MODEL e1 MAX S, PRIORIZA C Y CO2
Model e1 /modeloSIMPLE,Reps1,Reps2/ ;
*MODEL e2 MIN CO2, PRIORIZA C Y S
Model e2 /modeloSIMPLE,Reps1,Reps3/ ;
*MODEL e3 MIN C, PRIORIZA CO2 Y S
Model e3 /modeloSIMPLE,Reps2,Reps3/ ;

parameter profitz1(it2,it1),profitz2(it2,it1),profitz3(it2,it1),profite1,profite2
          CP valorpasado /0/,CO2P valorpasado /0/,SP valorpasado /0/,
          CA valorACTUAL /0/,CO2A valorACTUAL /0/,SA valorACTUAL /0/;

loop(it1,
    eC = FClow + (ord(it1)-1)*(FCup-FClow)/(card(it1)-1)
    loop(it2,
       eCO2 = FCO2low + (ord(it2)-1)*(FCO2up-FCO2low)/(card(it2)-1)
       solve e1 using LP MAX S;  ms=e1.modelstat; ss=e1.solvestat;

       if (ms=1 or ms=2 or ms=7 or ms=8 or ms=15 or ms=16 or ms=17,
                CA=C.L;
                CO2A=CO2.L;
                SA=S.L;
                if( ((CA <> CP) or (CO2A <> CO2P) or (SA <> SP)) ,
                    CP=CA; CO2P=CO2A; SP=SA;
                    profite1(it2,it1)=eC;
                    profite2(it2,it1)=eCO2;
                    profitz1(it2,it1)=C.L;
                    profitz2(it2,it1)=CO2.L;
                    profitz3(it2,it1)=S.L;
           );
       );
    );
);

*display FClow,FCup,FCO2low,FCO2up,FSlow,FSup,profitz1,profitz2,profitz3,profite1,profite2;
execute_unload "results-econtraint.gdx" FClow,FCup,FCO2low,FCO2up,FSlow,FSup,profitz1,profitz2,profitz3,profite1,profite2;

loop(it1,
    eC = FClow + (ord(it1)-1)*(FCup-FClow)/(card(it1)-1)
    loop(it2,
       eS = FSlow + (ord(it2)-1)*(FSup-FSlow)/(card(it2)-1)
       solve e2 using LP min CO2;  ms=e2.modelstat; ss=e2.solvestat;

       if (ms=1 or ms=2 or ms=7 or ms=8 or ms=15 or ms=16 or ms=17,
                CA=C.L;
                CO2A=CO2.L;
                SA=S.L;
                if( ((CA <> CP) or (CO2A <> CO2P) or (SA <> SP)) ,
                    CP=CA; CO2P=CO2A; SP=SA;
                    profite1(it2,it1)=eC;
                    profite2(it2,it1)=eCO2;
                    profitz1(it2,it1)=C.L;
                    profitz2(it2,it1)=CO2.L;
                    profitz3(it2,it1)=S.L;
           );
       );
    );
);

*display FClow,FCup,FCO2low,FCO2up,FSlow,FSup,profitz1,profitz2,profitz3,profite1,profite2;
execute_unload "results-econtraint2.gdx" FClow,FCup,FCO2low,FCO2up,FSlow,FSup,profitz1,profitz2,profitz3,profite1,profite2;
loop(it1,
    eCO2 = FCO2low + (ord(it1)-1)*(FCO2up-FCO2low)/(card(it1)-1)
    loop(it2,
       eS = FSlow + (ord(it2)-1)*(FSup-FSlow)/(card(it2)-1)
       solve e3 using LP min C;  ms=e3.modelstat; ss=e3.solvestat;

       if (ms=1 or ms=2 or ms=7 or ms=8 or ms=15 or ms=16 or ms=17,
                CA=C.L;
                CO2A=CO2.L;
                SA=S.L;
                if( ((CA <> CP) or (CO2A <> CO2P) or (SA <> SP)) ,
                    CP=CA; CO2P=CO2A; SP=SA;
                    profite1(it2,it1)=eC;
                    profite2(it2,it1)=eCO2;
                    profitz1(it2,it1)=C.L;
                    profitz2(it2,it1)=CO2.L;
                    profitz3(it2,it1)=S.L;
           );
       );
    );
);

*display FClow,FCup,FCO2low,FCO2up,FSlow,FSup,profitz1,profitz2,profitz3,profite1,profite2;
execute_unload "results-econtraint3.gdx" FClow,FCup,FCO2low,FCO2up,FSlow,FSup,profitz1,profitz2,profitz3,profite1,profite2;
'''  
    if (FO=='e-constraint' and METODO=='8'):
        prog = ws.add_job_from_string(instrucciones8, cp)


# Optimización mediante método e-constraint + por compromiso
    instrucciones9='''parameter C11   /0/,   C12 /0/,   C13 /0/,
          CO221 /0/, CO222 /0/, CO223 /0/,
          S31   /0/,   S32 /0/,   S33 /0/;
SOLVE modeloSIMPLE using LP min C;
   FClow=C.L;     C11=C.L;     C12=CO2.L;   C13=S.L;
SOLVE modeloSIMPLE using LP min CO2;
   FCO2low=CO2.L; CO221=CO2.L; CO222=CO2.L; CO223=S.L;
SOLVE modeloSIMPLE using LP max S;
   FSup=S.L;      S31=C.L;     S32=CO2.L;   S33=S.L;

*SELECCIONA FSlow DE LA MATRIZ
IF(C13>CO223,
   FSlow=CO223;
ELSE
   IF(C13>S33,
     FSlow=S33;
   ELSE
     FSlow=C13;
   );
);
*SELECCIONA FCup DE LA MATRIZ
IF(C11<CO221,
   FCup=CO221;
ELSE
   IF(C11<S31,
     FCup=S31;
   ELSE
     FCup=C11;
   );
);
*SELECCIONA FCO2up DE LA MATRIZ
IF(C12<CO222,
   FCO2up=CO222;
ELSE
   IF(C12<S32,
     FCO2up=S32;
   ELSE
     FCO2up=C12;
   );
);


Model e2 /modeloSIMPLE,Reps1,Reps2/ ;

parameter profitz1(it2,it1),profitz2(it2,it1),profitz3(it2,it1),
          profitz1e(it2,it1),profitz2e(it2,it1),profitz3e(it2,it1),
          profite1,profite2,profitw1,profitw2,profitw3
          CP valorpasado /0/,CO2P valorpasado /0/,SP valorpasado /0/,
          CA valorACTUAL /0/,CO2A valorACTUAL /0/,SA valorACTUAL /0/;

*Modelo por compromiso
loop(it1,
if((ord(it1)-1)/(card(it1)-1)=0,
 w1=1e-10
else
 w1=(ord(it1)-1)/(card(it1)-1);
);
   loop(it2,
       if(ord(it2)<=ord(it1),
         w2 = 1e-10;
       else
         w2 = (ord(it2)-ord(it1))/(card(it2)-1)
         );
       if((1-w1-w2)=0,
         w3=1e-10
       else
         w3= 1-w1-w2;
        );
       if(ord(it2)>=ord(it1),
          solve ponderado using LP min Z;
          CA=C.L;
          CO2A=CO2.L;
          SA=S.L;       
          if( ((CA <> CP) AND (CO2A <> CO2P) AND (SA <> SP)) ,
              CP=CA; CO2P=CO2A; SP=SA;
              profitw1(it2,it1)=w1;
              profitw2(it2,it1)=w2;
              profitw3(it2,it1)=w3;
              profitz1(it2,it1)=C.L;
              profitz2(it2,it1)=CO2.L;
              profitz3(it2,it1)=S.L;
             );
         );
       );
);
*Modelo por compromiso

*Modelo e-constraint
loop(it1,
    eC = FClow + (ord(it1)-1)*(FCup-FClow)/(card(it1)-1)
    loop(it2,
       eCO2 = FCO2low + (ord(it2)-1)*(FCO2up-FCO2low)/(card(it2)-1)
       solve e2 using LP MAX S; ms=e2.modelstat; ss=e2.solvestat;
       if (ms=1 or ms=2 or ms=7 or ms=8 or ms=15 or ms=16 or ms=17,
                CA=C.L;
                CO2A=CO2.L;
                SA=S.L;
                if( ((CA <> CP) and (CO2A <> CO2P) and (SA <> SP)) ,
                    CP=CA; CO2P=CO2A; SP=SA;
                    profite1(it2,it1)=eC;
                    profite2(it2,it1)=eCO2;
                    profitz1e(it2,it1)=C.L;
                    profitz2e(it2,it1)=CO2.L;
                    profitz3e(it2,it1)=S.L;
           );
       );
    );
);
*Modelo e-constraint
execute_unload "results.gdx" FClow,FCup,FCO2low,FCO2up,FSlow,FSup,
                             profitz1e,profitz2e,profitz3e,profite1,profite2,
                             profitz1,profitz2,profitz3,profitw1,profitw2,profitw3
'''  
    if (FO=='e-constraint + por compromiso' and METODO=='9'):
        prog = ws.add_job_from_string(instrucciones9, cp)
        

    prog.run(opt, databases = db)
    modelstatus=float(str(prog.out_db["ms"].find_record().value))
    solucionlevel={}
    solucionmarginal={}
    for rec in prog.out_db["q"]:
        ##print("q(" + rec.key(0) + ", " + rec.key(1) + "):   Valor= " + str(rec.level) + " Marginal= " + str(rec.marginal))
        solucionlevel.setdefault((rec.key(0),rec.key(1)),round(float(str(rec.level)),2))
        solucionmarginal.setdefault((rec.key(0),rec.key(1)),float(str(rec.marginal)))
colum1=list(solucionlevel.keys())
colum2=list(solucionlevel.values())
nameoutput=valores.get('archivo')
redondeo=int(valores.get('redondeo'))

if modelstatus==1 or modelstatus==2 or modelstatus==7 or modelstatus==8 or modelstatus==15 or modelstatus==16 or modelstatus==17:
    if (METODO=='1' or METODO=='2' or METODO=='3' or METODO=='4' or METODO=='5'):
        print("Model Status: " + str(prog.out_db["ms"].find_record().value))
        print("Función Objetivo: " + FO)
        if OBJETIVO=='Lexicografico':
            print("Método empleado: " + OBJETIVO)
        if OBJETIVO=='Ponderacion':
            print("Método empleado: " + OBJETIVO)
            
        ValorC=prog.out_db["C"].find_record().level
        ValorCO2=prog.out_db["CO2"].find_record().level
        ValorS=prog.out_db["S"].find_record().level
        
        
        print("Valor de la Función   C: " + str(round(ValorC,redondeo)) + " dólares")
        
        print("Valor de la Función CO2: " + str(round(ValorCO2,redondeo)) + " T/año")
        
        print("Valor de la Función   S: " + str(round(ValorS,redondeo)) + " Puntos")
        ValorS=prog.out_db["S"].find_record().level
        if FO=='Ponderacion':
           print("Valor de la Función   Z: " + str(prog.out_db["Z"].find_record().level) + " ")
           print("Valor de la Función   Cn: " + str(prog.out_db["Z1n"].find_record().level) + " Objetivo C normalizado")
           print("Valor de la Función   CO2n: " + str(prog.out_db["Z2n"].find_record().level) + " Objetivo CO2 normalizado")
           print("Valor de la Función   Sn: " + str(prog.out_db["Z3n"].find_record().level) + " Objetivo S normalizado")
        

        Resultado={}

        for x,i in enumerate(Recursos_i):
            for q,j in enumerate(Tareas_j):
                Resultado.setdefault((i,j),round(float(solucionlevel.get((i,j))),redondeo))
        Resultados=list(Resultado.items())

        Resultados=np.column_stack((colum1,colum2))    
        # enca=['Recurso', 'Tarea','Recurso destinado','Valor Marginal']  #ENCABEZADO CON COLUMNA VALOR MARGINAL
        enca=['Recurso','Tarea', 'Recurso destinado']

        print(tabulate(Resultados,
                       headers=enca,
                       tablefmt='fancy_grid',
                       stralign='left',
                       numalign='center',
                       floatfmt='.'+str(redondeo)+'f'))

        f = open (nameoutput+'.txt','w')
        resumen=str(tabulate(Resultados,headers=enca,stralign='left',numalign='center',floatfmt='.3f'))
        f.write('Función Objetivo: '+FO+'\n'+
                'Valor de la Función   C: ' + str(round(ValorC,redondeo)) + ' dólares'+'\n'+
                'Valor de la Función   CO2: ' + str(round(ValorCO2,redondeo))+ ' T/año' +'\n' +
                'Valor de la Función   S: ' + str(round(ValorS,redondeo))+ ' Puntos Sociales' +'\n' +
                resumen)
        f.close()

        g= open('input.txt', 'w')
        valoresout=str('Recurso'+'\n'+tabulate(xi.items())+'\n'+'\n'+
                       'Factor R'+'\n'+tabulate(Ri.items())+'\n'+'\n'+
                       'Energía por año Uj'+'\n'+tabulate(Uj.items())+'\n'+'\n'+
                       'Potencia max requerida Poj'+'\n'+tabulate(Poj.items())+'\n'+'\n'+
                       'Eficiencia'+'\n'+tabulate(nij.items())+'\n'+'\n'+
                       'Factor de Carga tarea/recurso'+'\n'+tabulate(Ri.items())+'\n'+'\n'+
                       'Costos de capital P(i,j)'+'\n'+tabulate(Pcij.items())+'\n'+'\n'+
                       'Vida Útil'+'\n'+tabulate(VU.items())+'\n'+'\n'+
                       'Mantenimiento'+'\n'+tabulate(mij.items())+'\n'+'\n'+
                       'Tasa de intéres'+'\n'+str(tasa)+'\n'+'\n'+
                       'Factor de emision'+'\n'+tabulate(feij.items())+'\n'+'\n'+
                       'Factores Sociales'+'\n'+tabulate(fsiii.items())+'\n'
                       )
        g.write(valoresout)
        g.close()
    if (METODO=='8'):
        from mpl_toolkits.mplot3d import axes3d
        import matplotlib.pyplot as plt
        db2 = ws.add_database_from_gdx("results-econtraint.gdx")
        profz1 = { tuple(rec.keys):rec.value for rec in db2["profitz1"] }
        profz2 = { tuple(rec.keys):rec.value for rec in db2["profitz2"] }
        profz3 = { tuple(rec.keys):rec.value for rec in db2["profitz3"] }
        profe1 = { tuple(rec.keys):rec.value for rec in db2["profite1"] }
        profe2 = { tuple(rec.keys):rec.value for rec in db2["profite2"] }
        # Definimos los datos
        x = list(profz1.values())
        y = list(profz2.values())
        z = list(profz3.values())
        e11 = list(profe1.values())
        e21 = list(profe2.values())
        Optimos1=[]
        Optimos1=np.column_stack((x,y,z,e11,e21))
        

        db3 = ws.add_database_from_gdx("results-econtraint2.gdx")
        profz12 = { tuple(rec.keys):rec.value for rec in db3["profitz1"] }
        profz22 = { tuple(rec.keys):rec.value for rec in db3["profitz2"] }
        profz32 = { tuple(rec.keys):rec.value for rec in db3["profitz3"] }
        profe12 = { tuple(rec.keys):rec.value for rec in db3["profite1"] }
        profe22 = { tuple(rec.keys):rec.value for rec in db3["profite2"] }
        # Definimos los datos
        x2 = list(profz12.values())
        y2 = list(profz22.values())
        z2 = list(profz32.values())
        e12 = list(profe12.values())
        e22 = list(profe22.values())
        Optimos2=[]
        Optimos2=np.column_stack((x2,y2,z2,e12,e22))

        db4 = ws.add_database_from_gdx("results-econtraint3.gdx")
        profz13 = { tuple(rec.keys):rec.value for rec in db4["profitz1"] }
        profz23 = { tuple(rec.keys):rec.value for rec in db4["profitz2"] }
        profz33 = { tuple(rec.keys):rec.value for rec in db4["profitz3"] }
        profe13 = { tuple(rec.keys):rec.value for rec in db4["profite1"] }
        profe23 = { tuple(rec.keys):rec.value for rec in db4["profite2"] }
        # Definimos los datos
        x3 = list(profz13.values())
        y3 = list(profz23.values())
        z3 = list(profz33.values())
        e13 = list(profe13.values())
        e23 = list(profe23.values())
        Optimos3=[]
        Optimos3=np.column_stack((x3,y3,z3,e13,e23))
        
        figura = plt.figure()
        # Creamos el plano 3D
        grafica = figura.add_subplot(111, projection='3d')

        x.extend(x2)
        x.extend(x3)
        y.extend(y2)
        y.extend(y3)
        z.extend(z2)
        z.extend(z3)
        
        #Guarda los datos de salida
        ##        En .txt
        f = open (nameoutput+'.txt','w')
        enca=['C','CO2', 'S','eC','eCO2']
        print(tabulate(Optimos1,headers=enca,stralign='left',numalign='center',floatfmt='.3f'))
        resumen=str(tabulate(Optimos1,headers=enca,stralign='left',numalign='center',floatfmt='.3f'))
        f.write(resumen)
        f.close()
      
        # Agregamos los puntos en el plano 3D
        grafica.scatter(x, y, z, c='g', marker='o')
        grafica.set_title('Óptimos generados '+FO)
        grafica.set_xlabel('eje x: Costos')
        grafica.set_ylabel('eje y: Emisiones')
        grafica.set_zlabel('eje z: Social')

        #segunda gráfica
        figura2 = plt.figure(2)
        plt.suptitle('Óptimos generados '+FO)
        grafica2 = figura2.add_subplot((221))
        grafica2.plot(x,y,'g^')
        grafica2.set_xlabel('Costos')
        grafica2.set_ylabel('Emisiones')
        
        grafica2 = figura2.add_subplot((222))
        grafica2.plot(x,z,'bs')
        grafica2.set_xlabel('Costos')
        grafica2.set_ylabel('Social')
        
        grafica2 = figura2.add_subplot((223))
        grafica2.plot(y,z,'ro')
        grafica2.set_xlabel('Emisiones')
        grafica2.set_ylabel('Social')

        grafica2 = figura2.add_subplot(224, projection='3d')
        grafica2.scatter(x, y, z, c='g', marker='o',label = 'e-constraint')
      


        
        # Mostramos el gráfico
        plt.show()
    if (METODO=='9'):
        from mpl_toolkits.mplot3d import axes3d
        import matplotlib.pyplot as plt
        db2 = ws.add_database_from_gdx("results.gdx")
        profz1 = { tuple(rec.keys):rec.value for rec in db2["profitz1"] }
        profz2 = { tuple(rec.keys):rec.value for rec in db2["profitz2"] }
        profz3 = { tuple(rec.keys):rec.value for rec in db2["profitz3"] }
        profw1 = { tuple(rec.keys):rec.value for rec in db2["profitw1"] }
        profw2 = { tuple(rec.keys):rec.value for rec in db2["profitw2"] }
        profw3 = { tuple(rec.keys):rec.value for rec in db2["profitw3"] }


        profz1e = { tuple(rec.keys):rec.value for rec in db2["profitz1e"] }
        profz2e = { tuple(rec.keys):rec.value for rec in db2["profitz2e"] }
        profz3e = { tuple(rec.keys):rec.value for rec in db2["profitz3e"] }    
        profe1 = { tuple(rec.keys):rec.value for rec in db2["profite1"] }
        profe2 = { tuple(rec.keys):rec.value for rec in db2["profite2"] }
            
        # Creamos el plano 3D
        figura = plt.figure(1)
        grafica = figura.add_subplot(111, projection='3d')

        # Definimos los datos 
        x = list(profz1.values())
        y = list(profz2.values())
        z = list(profz3.values())
        w11 = list(profw1.values())
        w12 = list(profw2.values())
        w13 = list(profw3.values())
        OptimosComp=[]
        OptimosComp=np.column_stack((x,y,z,w11,w12,w13))
        
        x2 = list(profz1e.values())
        y2 = list(profz2e.values())
        z2 = list(profz3e.values())
        e11 = list(profe1.values())
        e12 = list(profe2.values())
        Optimose=[]
        Optimose=np.column_stack((x2,y2,z2,e11,e12))
        
        # Agregamos los puntos en el plano 3D
        grafica.scatter(x, y, z, c='g', marker='o',label = 'Por compromiso')
        grafica.scatter(x2, y2, z2, c ='r', marker='o',label = 'e-constraint')
        grafica.set_title('Óptimos generados '+FO)
        grafica.set_xlabel('eje x: Costos')
        grafica.set_ylabel('eje y: Emisiones')
        grafica.set_zlabel('eje z: Social')
        grafica.legend()
        
        figura2 = plt.figure(2)
        plt.suptitle('Óptimos generados '+FO)
        grafica2 = figura2.add_subplot((221))
        grafica2.plot(x2,y2,'g^')
        grafica2.set_xlabel('Costos')
        grafica2.set_ylabel('Emisiones')
        
        grafica2 = figura2.add_subplot((222))
        grafica2.plot(x2,z2,'bs')
        grafica2.set_xlabel('Costos')
        grafica2.set_ylabel('Social')
        
        grafica2 = figura2.add_subplot((223))
        grafica2.plot(y2,z2,'ro')
        grafica2.set_xlabel('Emisiones')
        grafica2.set_ylabel('Social')

        grafica2 = figura2.add_subplot(224, projection='3d')
        grafica2.scatter(x, y, z, c='g', marker='o',label = 'Por compromiso')
        grafica2.scatter(x2, y2, z2, c ='r', marker='o',label = 'e-constraint')
        

        #Guarda los datos de salida
        ##        En .txt
        f = open (nameoutput+'.txt','w')
        enca=['C','CO2', 'S','w1','w2','w3']
        print(tabulate(OptimosComp,headers=enca,stralign='left',numalign='center',floatfmt='.3f'))
        resumen1=str(tabulate(OptimosComp,headers=enca,stralign='left',numalign='center',floatfmt='.3f'))
        enca=['C','CO2', 'S','eC','eCO2']
        print(tabulate(Optimose,headers=enca,stralign='left',numalign='center',floatfmt='.3f'))
        resumen2=str(tabulate(Optimose,headers=enca,stralign='left',numalign='center',floatfmt='.3f'))
        f.write(resumen1+'\n'+resumen2)
        f.close()
      
        # Mostramos el gráfico
        plt.show()
    sg.Popup('Terminado, revisa el comand window para ver los resultados')

elif modelstatus==0:
    if (METODO=='6' or METODO=='7'):
        from mpl_toolkits.mplot3d import axes3d
        import matplotlib.pyplot as plt
        db2 = ws.add_database_from_gdx("results.gdx")
        profz1 = { tuple(rec.keys):rec.value for rec in db2["profitz1"] }
        profz2 = { tuple(rec.keys):rec.value for rec in db2["profitz2"] }
        profz3 = { tuple(rec.keys):rec.value for rec in db2["profitz3"] }
        profw1 = { tuple(rec.keys):rec.value for rec in db2["profitw1"] }
        profw2 = { tuple(rec.keys):rec.value for rec in db2["profitw2"] }
        profw3 = { tuple(rec.keys):rec.value for rec in db2["profitw3"] }
        figura = plt.figure()
        # Creamos el plano 3D
        grafica = figura.add_subplot(111, projection='3d')

        # Definimos los datos de prueba
        x = list(profz1.values())
        y = list(profz2.values())
        z = list(profz3.values())
        w11 = list(profw1.values())
        w12 = list(profw2.values())
        w13 = list(profw3.values())
        Optimos=[]
        Optimos=np.column_stack((x,y,z,w11,w12,w13))

        #Guarda los datos de salida
        ##        En .txt
        f = open (nameoutput+'.txt','w')
        enca=['C','CO2', 'S','w1','w2','w3']
        print(tabulate(Optimos,headers=enca,stralign='left',numalign='center',floatfmt='.3f'))
        resumen=str(tabulate(Optimos,headers=enca,stralign='left',numalign='center',floatfmt='.3f'))
        f.write(resumen)
        f.close()
        
        # Agregamos los puntos en el plano 3D
        grafica.scatter(x, y, z, c='g', marker='o')
        grafica.set_title('Óptimos generados '+FO)
        grafica.set_xlabel('eje x: Costos')
        grafica.set_ylabel('eje y: Emisiones')
        grafica.set_zlabel('eje z: Social')
    ##    grafica.legend()

        #segunda gráfica
        figura2 = plt.figure(2)
        plt.suptitle('Óptimos generados '+FO)
        grafica2 = figura2.add_subplot((221))
        grafica2.plot(x,y,'g^')
        grafica2.set_xlabel('Costos')
        grafica2.set_ylabel('Emisiones')
        
        grafica2 = figura2.add_subplot((222))
        grafica2.plot(x,z,'bs')
        grafica2.set_xlabel('Costos')
        grafica2.set_ylabel('Social')
        
        grafica2 = figura2.add_subplot((223))
        grafica2.plot(y,z,'ro')
        grafica2.set_xlabel('Emisiones')
        grafica2.set_ylabel('Social')

        grafica2 = figura2.add_subplot(224, projection='3d')
        grafica2.scatter(x, y, z, c='g', marker='o')

        
        # Mostramos el gráfico
        plt.show()
else:
    sg.Popup('No tiene soluciones factibles')
    print("Model Status: " + str(modelstatus) +', Revisar archivo reporte carpeta TEMP')







