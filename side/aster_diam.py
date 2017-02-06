# coding: utf8
import xlwt
import urllib
#import ephem
from bs4 import BeautifulSoup
import numpy as np

_DBMPC = 'all.edb'

def write_row(ws, buffer_list, rowx, colx=0):
    for element in buffer_list:
        ws.write(rowx, colx, element.decode('utf8'))
        colx += 1
    rowx += 1
    colx = 0
    return rowx, colx

# thanks to https://github.com/typpo/asterank/blob/master/data/pipeline/run/60_jpl/jpl_lookup.py
def jpl_diam(objname):
    src = urllib.urlopen('http://ssd.jpl.nasa.gov/sbdb.cgi?sstr=%s;cad=1' % objname ).read()            
    soup = BeautifulSoup(src.replace('cellspacing="0"0', ''), 'html5lib')

    p = soup.find(text='diameter')
    if p is not None:
        diam = p.find_parent('td').next_sibling.next_sibling.next_sibling.next_sibling.find('font').next  
    else:
        diam = '--'
    return str(diam)
    
if __name__ == '__main__':
    wb = xlwt.Workbook()
    ws = wb.add_sheet(_DBMPC)
    style_string = "font: bold on"
    style = xlwt.easyxf(style_string)
    [rowx, colx] = [0, 0]
    ws.write(rowx, colx, 'Астероиды: диаметры (JPL)'.decode('utf8'), style=style)
    rowx += 1
    ws.write(rowx, colx, 'Asteroids: diameters (JPL)'.decode('utf8'), style=style)
    rowx += 1
    ws.write(rowx, colx, 'Name'.decode('utf8'), style=style)
    colx += 1
    ws.write(rowx, colx, 'Diameter'.decode('utf8'), style=style)
    rowx += 1
    colx = 0
    
    with open(_DBMPC, 'r+') as f:
        r = f.readlines()
    
    while r[0].startswith('#'):
        r = r[1:]
    max_entry = len(r)
    i = 0
    tcpy = []
    for db_entry in r:
        i += 1

        #dbE = ephem.readdb(db_entry)
        name = db_entry.split(',')[0]
        diam = jpl_diam(name)
        rowx, colx = write_row(ws, [name, diam], rowx)
        print "%i/%i: %s %s" % (i, max_entry, name, diam)
        tcpy.append([name, diam])
        if ((i % 10) == 0):
            np.savez_compressed("buf_aster_diam", data=tcpy)
    
    full_filename = 'aster_diam.xls'
    
    wb.save(full_filename)
