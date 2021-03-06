"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 """
import config
from DISClib.ADT import list as lt
from DISClib.DataStructures import listiterator as it
from DISClib.ADT import orderedmap as om
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import map as m
import datetime
assert config

"""
En este archivo definimos los TADs que vamos a usar,
es decir contiene los modelos con los datos en memoria


"""

# -----------------------------------------------------
# API del TAD Catalogo de accidentes
# -----------------------------------------------------

def newAnalyzer():
    """ Inicializa el analizador

    Crea una lista vacia para guardar todos los crimenes
    Se crean indices (Maps) por los siguientes criterios:
    -Fechas

    Retorna el analizador inicializado.
    """
    analyzer = {'accidents': None,
                'dateIndex': None
                }

    analyzer['accidents'] = lt.newList('SINGLE_LINKED', compareIds)
    analyzer['dateIndex'] = om.newMap(omaptype='RBT',
                                      comparefunction=compareDates)
    return analyzer

# Funciones para agregar informacion al catalogo

def addAccident(analyzer, accident):
    """
    """
    lt.addLast(analyzer['accidents'], accident)
    updateDateIndex(analyzer['dateIndex'], accident)
    return analyzer


def updateDateIndex(map, accident):
    """
    Se toma la fecha del accidente y se busca si ya existe en el arbol
    dicha fecha.  Si es asi, se adiciona a su lista de accidentes
    y se actualiza el indice de tipos de accidentes.

    Si no se encuentra creado un nodo para esa fecha en el arbol
    se crea y se actualiza el indice de tipos de accidentes
    """
    occurreddate = accident['severity']
    accidentdate = datetime.datetime.strptime(occurreddate, '%Y-%m-%d %H:%M:%S')
    entry = om.get(map, accidentdate.date())
    if entry is None:
        datentry = newDataEntry(accident)
        om.put(map, accidentdate.date(), datentry)
    else:
        datentry = me.getValue(entry)
    addDateIndex(datentry, accident)
    return map


def addDateIndex(datentry, accident):
    """
    Actualiza un indice de tipo de accidentes.  Este indice tiene una lista
    de accidentes y una tabla de hash cuya llave es el tipo de accidente y
    el valor es una lista con los accidentes de dicho tipo en la fecha que
    se está consultando (dada por el nodo del arbol)
    """
    lst = datentry['lstaccidents']
    lt.addLast(lst, accident)
    severityIndex = datentry['severityIndex']
    seventry = m.get(severityIndex, accident['severity'])
    if (seventry is None):
        entry = newSeverityEntry(accident['severity'], accident)
        lt.addLast(entry['lstseverities'], accident)
        m.put(severityIndex, accident['severity'], entry)
    else:
        entry = me.getValue(seventry)
        lt.addLast(entry['lstoffenses'], accident)
    return datentry


def newDataEntry(accident):
    """
    Crea una entrada en el indice por fechas, es decir en el arbol
    binario.
    """
    entry = {'severityIndex': None, 'lstaccidents': None}
    entry['severityIndex'] = m.newMap(numelements=30,
                                     maptype='PROBING',
                                     comparefunction=compareSeverities)
    entry['lstaccidents'] = lt.newList('SINGLE_LINKED', compareDates)
    return entry

def newSeverityEntry(severitygrp, accident):
    """
    Crea una entrada en el indice por tipo de accidente, es decir en
    la tabla de hash, que se encuentra en cada nodo del arbol.
    """
    seentry = {'severityy': None, 'lstseverities': None}
    seentry['severityy'] = severitygrp
    seentry['lstseverities'] = lt.newList('SINGLELINKED', compareSeverities)
    return seentry
# ==============================
# Funciones de consulta
# ==============================

def accidentsSize(analyzer):
    """
    Número de accidentes
    """
    return lt.size(analyzer['accidents'])


def indexHeight(analyzer):
    """
    Altura del arbol
    """
    return om.height(analyzer['dateIndex'])


def indexSize(analyzer):
    """
    Numero de elementos en el indice
    """
    return om.size(analyzer['dateIndex'])


def minKey(analyzer):
    """
    Llave mas pequena
    """
    return om.minKey(analyzer['dateIndex'])


def maxKey(analyzer):
    """
    Llave mas grande
    """
    return om.maxKey(analyzer['dateIndex'])


def getAccidentsByRange(analyzer, initialDate, finalDate):
    """
    Retorna el numero de accidentes en un rago de fechas.
    """
    lst = om.values(analyzer['dateIndex'], initialDate, finalDate)
    lstiterator = it.newIterator(lst)
    totaccidents = 0
    while (it.hasNext(lstiterator)):
        lstdate = it.next(lstiterator)
        totaccidents += lt.size(lstdate['lstaccidents'])
    return totaccidents


def getAccidentsBySeverity(analyzer, initialDate, offensecode):
    """
    Para una fecha determinada, retorna el numero de accidentes
    de manera organizada por su nivel de severidad.
    """
    accidentdate = om.get(analyzer['dateIndex'], initialDate)
    if accidentdate['key'] is not None:
        severitymap = me.getValue(accidentdate)['severityIndex']
        numseverities = m.get(severitymap, offensecode)
        if numseverities is not None:
            return m.size(me.getValue(numseverities)['lstseverities'])
        return 0

def getAccidentsBeforeDate(analyzer, initialDate):
    """
    Obtiene el numero de incidentes ocurridos antes de cierta fecha
    """
    org = analyzer["DateIndex"]
    leastDate = om.minKey(org)
    incidents = om.values(org, leastDate, initialDate)
    return incidents

def getAccidentsByHour(analyzer, maxkey, minkey):

    hRange = om.values(analyzer["hourIndex"], maxkey, minkey)
    iterator = it.newIterator(hRange)
    tot = 0
    Severity1 = 0
    Severity2 = 0
    Severity3 = 0 
    Severity4 = 0
    while it.hasNext(iterator):
        hour = it.next(iterator)
        for severity in range(1,5):
            severityEntry = m.get(hour["severityIndex"],severity)
            if severityEntry is not None:
                severity = me.getValue(severityEntry)
                size = lt.size(severity["lstSeverities"])
                if severity == 1:
                    Severity1 = Severity1+size
                elif severity == 2:
                    Severity2 = Severity2+size
                elif severity == 3:
                    Severity3 = Severity3+size
                else:
                    Severity4 = Severity4+size
                tot = Severity1 + Severity2 + Severity3 + Severity4
    return Severity1, Severity2, Severity3, Severity4, tot

# ==============================
# Funciones de Comparacion
# ==============================

def compareIds(id1, id2):
    """
    Compara dos accidentes
    """
    if (id1 == id2):
        return 0
    elif id1 > id2:
        return 1
    else:
        return -1


def compareDates(date1, date2):
    """
    Compara dos fechas
    """
    if (date1 == date2):
        return 0
    elif (date1 > date2):
        return 1
    else:
        return -1

def compareSeverities(severity1, severity2):
    """
    Compara dos tipos de severidades
    """
    severity = me.getKey(severity2)
    if (severity1 == severity):
        return 0
    elif (severity1 > severity):
        return 1
    else:
        return -1
