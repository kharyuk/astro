# coding: utf8

import ephem
from coord import coord

import numpy as np
import sys
import math
from scipy.optimize import brentq

from compute import *
from utils import parse_date, parse_coord
import time
import ephem
import datetime
from utils import parse_coord
import xlwt
import csv

import urllib
from bs4 import BeautifulSoup

#_URLMPC = 'http://mpc.cfa.harvard.edu/ws/search'

#_DBMPC = 'side/large.edb'
_DBMPC = 'side/all.edb'
OUTPUTDIR = './result/'
    
def ephobj(obj, date):
    # Moscow coordinates
    (lat, lon) = (55.7522200, 37.6155600) 

    date2 = date - datetime.timedelta(days=1)
    
    time = '21:00' #
    
    gatech1 = date.strftime('%Y/%m/%d') + ' ' + time #, 

    obj.compute(gatech1)
    #obj1 = [parse_coord(str(obj.a_ra), 'ra'), parse_coord(str(obj.a_dec), 'deg')]
    obj1 = [obj.a_ra, obj.a_dec]
    
    gatech2 = date2.strftime('%Y/%m/%d') + ' ' + time # , '%d/%m/%Y'

    obj.compute(gatech2)
    #obj2 = [parse_coord(str(obj.a_ra), 'ra'), parse_coord(str(obj.a_dec), 'deg')]
    obj2 = [obj.a_ra, obj.a_dec]
    return obj2, obj1

def make_list_header(ws):
    style_string = "font: bold on"
    style = xlwt.easyxf(style_string)
    
    [rowx, colx] = [0, 0]
    ws.write(rowx, colx, 'Астероиды'.decode('utf8'), style=style)
    rowx += 1
    ws.write(rowx, colx, 'Asteroids'.decode('utf8'), style=style)
    rowx += 1
    base = ['Date',
            'Time',
            'No.',
            'Name',
            'Diameter',
            'Distance',
            'RA',
            'DEC']
    for x in base:
        ws.write(rowx, colx, x.decode('utf8'), style=style)
        colx += 1
    rowx += 1
    colx = 0
    return rowx, colx

def write_row(ws, buffer_list, rowx, colx=0):
    for element in buffer_list:
        ws.write(rowx, colx, element.decode('utf8'))
        colx += 1
    rowx += 1
    colx = 0
    return rowx, colx
    
def get_db(dbfnm, max_entry, skip=None):
    rv = []
    with open(dbfnm, 'r+') as f:
        r = '#'
        while r.startswith('#'):
            r = f.readline()
        for idx in xrange(max_entry):
            if skip is not None:
                if idx in skip:
                    continue
            r = f.readline()
            rv.append(r)
    return rv
    
def find_inter(date, obj1, obj2):
    def func(x):
        obj1.compute(x)
        obj2.compute(x)
        ra1 = obj1.a_ra * 12./np.pi
        ra2 = obj2.a_ra * 12./np.pi
        
        dist = ra2 - ra1
        if abs(dist) > 12.:
            if ra1 < ra2:
                dist -= 24.
            else:
                dist += 24
        return dist
        
    date_prev = date - datetime.timedelta(days=1)
    
    time = '21:00' 
    
    gatech2 = date.strftime('%Y/%m/%d') + ' ' + time 
    gatech1 = date_prev.strftime('%Y/%m/%d') + ' ' + time

    a = ephem.date(gatech1)
    b = ephem.date(gatech2)
    t0 = brentq(func, a, b)

    time = coord(0, 0, (t0 - a)*24.*60.*60., 1, 'ra')
    return t0, time
    
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

def as_main_work(day_start,
                 day_end,
                 mpf=12,
                 declim=16.,
                 max_entry=412,
                 dbfnm = _DBMPC,
                 progressBar=None):
    
    style_string = "font: bold on"
    style = xlwt.easyxf(style_string)
    
    curdate = day_start
    
    curmonth = curdate.month 
    wb = xlwt.Workbook()
    sheetname = curdate.strftime('%h') + ' ' + str(curdate.year)[-2:]
    sheet_num = 0
    ws = wb.add_sheet(sheetname.decode('utf8'))
    rowx, colx = make_list_header(ws)
    
    all_days = (day_end - day_start).days
    
    db = get_db(dbfnm, max_entry, skip=None)
    for numday in xrange(all_days):
        objects_per_day = 0
        if curdate.month != curmonth:
            curmonth = curdate.month
            sheet_num += 1
            if sheet_num == mpf:
                filename = 'Asteroids_'
                filename += day_start.strftime('%d-%m-%Y')
                filename += '--'
                filename += (curdate-datetime.timedelta(days=1)).strftime('%d-%m-%Y')
                filename += '.xls'
                wb.save(OUTPUTDIR+filename)
                wb = xlwt.Workbook()
                sheet_num = 0
                day_start = curdate + datetime.timedelta(days=0)
            sheetname = curdate.strftime('%h') + ' ' + str(curdate.year)[-2:]
            ws = wb.add_sheet(sheetname.decode('utf8'))
            rowx, colx = make_list_header(ws)
            
        lines = []
        for db_entry in db:
            if len(db_entry) < 2:
                break
            aster = ephem.readdb(db_entry)
            sun = ephem.Sun()
            [[aster1_ra, aster1_dec], [aster2_ra, aster2_dec]] = ephobj(aster, curdate)
            [[sun1_ra, sun1_dec], [sun2_ra, sun2_dec]] = ephobj(sun, curdate)
            
            
            sun1_ra = float(sun1_ra) * 12./np.pi
            sun2_ra = float(sun2_ra) * 12./np.pi
            if sun2_ra < sun1_ra:
                sun2_ra += 24.
            
            aster1_ra = float(aster1_ra) * 12./np.pi
            aster2_ra = float(aster2_ra) * 12./np.pi
            if abs(aster1_ra - aster2_ra) > 12.:
                if aster1_ra < aster2_ra:
                    aster1_ra += 24.
                else:
                    aster2_ra += 24.
            
            
            dif_ra1 = min(aster1_ra, aster2_ra) - sun1_ra
            dif_ra2 = max(aster1_ra, aster2_ra) - sun2_ra
            
            
            '''
            print sun1_ra, sun2_ra
            print aster1_ra, aster2_ra
            print dif_ra1, dif_ra2
            print
            '''
            if dif_ra1 * dif_ra2 > 0:
                continue
            t0, time = find_inter(curdate, aster, sun)
            sun.compute(t0)
            aster.compute(t0)
            if abs(sun.a_ra - aster.a_ra)* 12./np.pi > 1e-3:
                continue
                
            line = [curdate.strftime('%d/%m/%Y'), time.__str__(rpar=0)]
            #print t0, time
            name = db_entry.split(',')[0]
            [nom, name] = name.split(' ', 1)
            line.append(nom)
            line.append(name)
            diam = jpl_diam(name)
            line.append(diam)
            
            aster_ra = str(aster.a_ra)
            aster_dec = str(aster.a_dec)
            dist = ephem.degrees(aster.a_dec - sun.a_dec) 
            if abs(dist) * 180. / np.pi > declim:
                continue
            line.append(str(dist))
            line.append(aster_ra)
            line.append(aster_dec)
            
            lines.append(line)
            
            objects_per_day += 1
        curdate = curdate + datetime.timedelta(days=1)
        if objects_per_day > 0:
            lines = sorted(lines, key=lambda x: x[-2])
            for line in lines:
                rowx, colx = write_row(ws, line, rowx, colx)
            rowx, colx = write_row(ws, [''], rowx, colx)
        print "Day %d/%d finished" % (numday+1, all_days)
        if progressBar is not None:
            progressBar.setValue((numday+1.0) / all_days * 100)
    filename = 'Asteroids_'
    filename += day_start.strftime('%d-%m-%Y')
    filename += '--'
    filename += day_end.strftime('%d-%m-%Y')
    filename += '.xls'
    full_filename = OUTPUTDIR+filename
    print full_filename
    wb.save(full_filename)
    return

if __name__ =='__main__':
    day_start = datetime.date(2017, 1, 1)
    day_end = datetime.date(2018, 1, 1)  #day_start + datetime.timedelta(days=5)
    as_main_work(day_start,
                 day_end,
                 mpf=12,
                 declim=16.,
                 #max_entry=412,
                 max_entry=727916,
                 dbfnm = _DBMPC,
                 progressBar=None)

