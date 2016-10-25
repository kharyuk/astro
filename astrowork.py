from astroquery.simbad import Simbad
from compute import *
from utils import parse_date, parse_coord
import time
import ephem
import datetime
from utils import parse_coord
import xlwt
import csv

CATLISTDIR = './text/'
CATLISTFILE = 'catalogue.csv'
OUTPUTDIR = './result/'
DEFAULTSETTINGSFILE = 'default_parameters.csv'

import six
import packaging
import packaging.version
import packaging.specifiers


def ephsun(date):
    # Moscow coordinates
    (lat, lon) = (55.7522200, 37.6155600) 

    date2 = date - datetime.timedelta(days=1)
    
    time = '21:00' #
    sun = ephem.Sun()
    #gatech = ephem.Observer()
    #gatech.lon, gatech.lat = str(lon), str(lat)
    
    gatech = date.strftime('%Y/%m/%d') + ' ' + time #, 

    sun.compute(gatech)
    sun1 = [parse_coord(str(sun.a_ra), 'ra'), parse_coord(str(sun.a_dec), 'deg')]
    
    gatech = date2.strftime('%Y/%m/%d') + ' ' + time # , '%d/%m/%Y'

    sun.compute(gatech)
    sun2 = [parse_coord(str(sun.a_ra), 'ra'), parse_coord(str(sun.a_dec), 'deg')]
    return sun2, sun1

def loadTableParameters(directory, filename):
    table = {}
    with open(directory+filename, 'rb') as csvfile:
        fid = csv.DictReader(csvfile, delimiter=',', quotechar="'")
        for row in fid:
            # angle distance
            vphi = row['vphi']
            if vphi.startswith('['):
                vphi = eval(vphi)
                phi_vec = True
            else:
                vphi = float(vphi)
                phi_vec = False
            # columns
            if len(row['columns']) == 0:
                columns = []
            else:
                columns = row['columns'].split('|')
            # name
            use_name = bool(row['use_name'])
            # fill in table
            table[row['code']] = {'vphi': vphi,
                                  'phi_vec': phi_vec,
                                  'columns': columns,
                                  'use_name': use_name}
                                  
    with open(CATLISTDIR+CATLISTFILE, 'rb') as csvfile:
        fid = csv.DictReader(csvfile, delimiter=',', quotechar="'")
        for row in fid:
            table[row['code']]['fullname'] = row['fullname']
            table[row['code']]['comment'] = row['comment']
    return table

def make_list_header(ws, code, code_table):
    style_string = "font: bold on"
    style = xlwt.easyxf(style_string)
    
    [rowx, colx] = [0, 0]
    ws.write(rowx, colx, code_table[code]['fullname'], style=style)
    rowx += 1
    ws.write(rowx, colx, code_table[code]['comment'].decode('utf8'), style=style)
    rowx += 1
    base = ['Date', 'Time']
    for x in base:
        ws.write(rowx, colx, x, style=style)
        colx += 1
    if code_table[code]['use_name']:
        ws.write(rowx, colx, 'Name', style=style)
        colx += 1
    for x in code_table[code]['columns']:
        ws.write(rowx, colx, x.upper(), style=style)
        colx += 1
    if code_table[code]['phi_vec']:
        ws.write(rowx, colx, 'Flux(V)', style=style)
        colx += 1
    base = ['Dist', 'RA', 'DEC']
    for x in base:
        ws.write(rowx, colx, x, style=style)
        colx += 1
    rowx += 1
    colx = 0
    return rowx, colx
    
def formulate_query(code, ra_interest, dec_interest):
    query = "cat in ('" + code + "')" + ' & '
    query += 'rah >= '+ str(ra_interest[0])  + ' & ' + 'rah < ' + str(ra_interest[1])+ ' & '
    query += 'dec > '+ str(dec_interest[0]) + ' & ' + 'dec < ' + str(dec_interest[1])
    return query

def write_row(ws, buffer_list, rowx, colx=0):
    for element in buffer_list:
        ws.write(rowx, colx, element)
        colx += 1
    rowx += 1
    colx = 0
    return rowx, colx

def main_process(code, day_start, day_end, mpf=12, directory=CATLISTDIR, filename=DEFAULTSETTINGSFILE):
    style_string = "font: bold on"
    style = xlwt.easyxf(style_string)
    
    code_table = loadTableParameters(directory, filename)
    
    curdate = day_start
    
    curmonth = curdate.month 
    wb = xlwt.Workbook()
    sheetname = curdate.strftime('%h') + ' ' + str(curdate.year)[-2:]
    sheet_num = 0
    ws = wb.add_sheet(sheetname)
    rowx, colx = make_list_header(ws, code, code_table)
    
    customSimbad = Simbad()
    if len(code_table[code]['columns']) > 0:
        customSimbad.add_votable_fields('id('+code+')')
    if code_table[code]['phi_vec']:
        customSimbad.add_votable_fields('flux(V)')
    customSimbad.ROW_LIMIT = -1
    #additionalSimbad = {}
    #for x in code_table[code]['columns']:
    #    additionalSimbad[x] = Simbad()
    #    additionalSimbad[x].add_votable_fields('id('+x+')')
    
    all_days = (day_end - day_start).days
    for numday in xrange(all_days):
        if curdate.month != curmonth:
            curmonth = curdate.month
            sheet_num += 1
            if sheet_num == mpf:
                filename = code.upper() + '_'
                filename += day_start.strftime('%d-%m-%Y')
                filename += '--'
                filename += (curdate-datetime.timedelta(days=1)).strftime('%d-%m-%Y')
                filename += '.xls'
                wb.save(OUTPUTDIR+filename)
                wb = xlwt.Workbook()
                sheet_num = 0
                day_start = curdate + datetime.timedelta(days=0)
            sheetname = curdate.strftime('%h') + ' ' + str(curdate.year)[-2:]
            ws = wb.add_sheet(sheetname)
            rowx, colx = make_list_header(ws, code, code_table)
            
        if code_table[code]['phi_vec']:
            vphi = code_table[code]['vphi'][0][1]
        else:
            vphi = code_table[code]['vphi']
    
        [[ra1, dec1], [ra2, dec2]] = ephsun(curdate)
        if dec1.f2s() < dec2.f2s():
            [c, d] = [dec1, dec2]
        else:
            [c, d] = [dec2, dec1]
        phi = coord(vphi,0,0,1,'deg')
        ra_interest = [ra1.f2hd(), ra2.f2hd()]
        dec_interest = [(c - phi).f2hd(), (d + phi).f2hd()]
        query = formulate_query(code, ra_interest, dec_interest)

        print query
        result = customSimbad.query_criteria(query)
        if result is not None:
            lenres = len(result)
            result.sort('RA')
        else:
            print "Day %d/%d [%s] finished w/o data" % (numday+1, all_days, curdate.strftime('%d-%m-%Y'))
            curdate = curdate + datetime.timedelta(days=1)
            continue
        for i in xrange(lenres):
            row = result[i]
            [ra, dec] = [row['RA'], row['DEC']]

            ra = parse_coord( ra, 'ra', ' ')
            dec = parse_coord( dec, 'deg', ' ')
            try:
                t = comp_time(ra1, ra2, ra)
            except:
                print ra1, ra2, ra, row['MAIN_ID']
                continue
            dist = comp_dist(curdate.day, curdate.month, t, dec)
            hdist = abs(dist.f2s() / 3600.)
            if code_table[code]['phi_vec']:
                refuse = True
                vmag = row['FLUX_V']
                if (str(vmag)!='--'):
                    for [vml, hdl] in code_table[code]['vphi']:
                        if vmag < vml:
                            if hdist >= hdl:
                                break
                            else:
                                refuse = False
                                break
                if refuse:
                    continue
            
            
            line = [curdate.strftime('%d/%m/%Y'), t.__str__(rpar=0)]
            name = row['MAIN_ID']
            if code_table[code]['use_name']:
                if name.startswith('NAME '):
                    name = name.replace("NAME ", '')
                line.append(name)
            alt_names = Simbad.query_objectids(row['MAIN_ID'])
            for colname in code_table[code]['columns']:
                locid = ''
                for an in alt_names:
                    if an['ID'].startswith(colname.upper()):
                        if len(locid) > 0:
                            locid += ' / '
                        lname = an['ID'].replace("NAME", '')
                        locid = locid + lname.replace("*", "") 
                line.append(locid)
            if code_table[code]['phi_vec']:
                line.append(str(row['FLUX_V']))
          
            line.append(str(dist))
            line.append(str(ra))
            line.append(str(dec))
            rowx, colx = write_row(ws, line, rowx, colx)
        curdate = curdate + datetime.timedelta(days=1)
        rowx, colx = write_row(ws, [''], rowx, colx)
        print "Day %d/%d finished" % (numday+1, all_days)
    filename = code.upper() + '_'
    filename += day_start.strftime('%d-%m-%Y')
    filename += '--'
    filename += day_end.strftime('%d-%m-%Y')
    filename += '.xls'
    wb.save(OUTPUTDIR+filename)
    return
    
if __name__ == '__main__':
    d1 = datetime.datetime.strptime('01/04/2016', '%d/%m/%Y')
    d2 = datetime.datetime.strptime('01/04/2018', '%d/%m/%Y')
    main_process('gcl', d1, d2)
