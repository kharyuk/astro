#from astroquery.simbad import Simbad
from compute import *
from simbad_query import Simbad
from utils import parse_date, parse_coord
import time
import ephem
import datetime
from utils import parse_coord
import xlwt
import csv
import os

CATLISTDIR = './text/'
CATLISTFILE = 'catalogue.csv'
OUTPUTDIR = './result/'
DEFAULTSETTINGSFILE = 'default_parameters.csv'


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
            vphi = eval(vphi)
            if len(vphi) == 1:
                if vphi[0][0] is None:            
                    phi_vec = False
                else:
                    phi_vec = True
            else:
                phi_vec = True
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
    ws.write(rowx, colx, code_table[code]['fullname'].decode('utf8'), style=style)
    rowx += 1
    ws.write(rowx, colx, code_table[code]['comment'].decode('utf8'), style=style)
    rowx += 1
    base = ['Date', 'Time']
    for x in base:
        ws.write(rowx, colx, x.decode('utf8'), style=style)
        colx += 1
    ws.write(rowx, colx, 'Code'.decode('utf8'), style=style)
    colx += 1
    if code_table[code]['use_name']:
        ws.write(rowx, colx, 'Name'.decode('utf8'), style=style)
        colx += 1
    for x in code_table[code]['columns']:
        ws.write(rowx, colx, x.upper().decode('utf8'), style=style)
        colx += 1
    if code_table[code]['phi_vec']:
        ws.write(rowx, colx, 'Flux(V)'.decode('utf8'), style=style)
        colx += 1
    base = ['Dist', 'RA', 'DEC']
    for x in base:
        ws.write(rowx, colx, x.decode('utf8'), style=style)
        colx += 1
    rowx += 1
    colx = 0
    return rowx, colx
    
def formulate_query(code, ra_interest, dec_interest):
    query = "cat in ('" + code + "')" + ' & '
    if ra_interest[0] < ra_interest[1]:
        query += '(rah >= '+ str(ra_interest[0])  + ' & ' + 'rah < ' + str(ra_interest[1])+ ') & '
    else:
        query += '(rah >= '+ str(ra_interest[0])  + ' | ' + 'rah < ' + str(ra_interest[1])+ ') & '
    query += 'dec > '+ str(dec_interest[0]) + ' & ' + 'dec < ' + str(dec_interest[1])
    return query

def write_row(ws, buffer_list, rowx, colx=0):
    for element in buffer_list:
        ws.write(rowx, colx, element.decode('utf8'))
        colx += 1
    rowx += 1
    colx = 0
    return rowx, colx

def aw_main_process(code, day_start, day_end, mpf=12,
                                           directory=CATLISTDIR,
                                           filename=DEFAULTSETTINGSFILE,
                                           progressBar=None):
    exists = os.path.isdir(OUTPUTDIR)
    if not exists:
        os.mkdir(OUTPUTDIR)
    
    exists = os.path.isdir(directory)
    exists = exists and os.path.isfile(directory+filename)
    if not exists:
        print "No directory (or file) with default_settigs"
    
    
    style_string = "font: bold on"
    style = xlwt.easyxf(style_string)
    
    code_table = loadTableParameters(directory, filename)
    
    curdate = day_start
    
    curmonth = curdate.month 
    wb = xlwt.Workbook()
    sheetname = curdate.strftime('%b') + ' ' + str(curdate.year)[-2:]
    sheet_num = 0
    ws = wb.add_sheet(sheetname.decode('utf8'))
    rowx, colx = make_list_header(ws, code, code_table)
    
    customSimbad = Simbad()
    if len(code_table[code]['columns']) > 0:
        customSimbad.addVotField('id('+code+')')
        #customSimbad.add_votable_fields('id('+code+')')
    if code_table[code]['phi_vec']:
        customSimbad.addVotField('flux(V)')
        #customSimbad.add_votable_fields('flux(V)')
    #customSimbad.ROW_LIMIT = -1
    #additionalSimbad = {}
    #for x in code_table[code]['columns']:
    #    additionalSimbad[x] = Simbad()
    #    additionalSimbad[x].add_votable_fields('id('+x+')')
    
    all_days = (day_end - day_start).days
    for numday in xrange(all_days):
        objects_per_day = 0
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
            sheetname = curdate.strftime('%b') + ' ' + str(curdate.year)[-2:]
            ws = wb.add_sheet(sheetname.decode('utf8'))
            rowx, colx = make_list_header(ws, code, code_table)
            
        vphi = code_table[code]['vphi'][0][1]
    
        [[ra1, dec1], [ra2, dec2]] = ephsun(curdate)
        if dec1.f2s() < dec2.f2s():
            [c, d] = [dec1, dec2]
        else:
            [c, d] = [dec2, dec1]
        phi = coord(vphi,0,0,1,'deg')
        ra_interest = [ra1.f2hd(), ra2.f2hd()]
        dec_interest = [(c - phi).f2hd(), (d + phi).f2hd()]
        query = formulate_query(code, ra_interest, dec_interest)

        result = customSimbad.query_criteria(query)
        if result is not None:
            lenres = len(result)
            #result.sort('RA')
        else:
            print "Day %d/%d finished w/o output" % (numday+1, all_days)
            if progressBar is not None:
                progressBar.setValue((numday+1.0) / all_days * 100)
            curdate = curdate + datetime.timedelta(days=1)
            continue
        lines = []
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
                #if (str(vmag)!='--'):
                if (str(vmag)!=''):
                    vmag = float(vmag)
                    for [vml, hdl] in code_table[code]['vphi']:
                        if vml is None:
                            if hdist >= hdl:
                                continue
                            else:
                                refuse = False
                                break
                        elif vmag < vml:
                            if hdist >= hdl:
                                continue
                            else:
                                refuse = False
                                break
                if refuse:
                    print 'refused: %s %s %f' % (row['MAIN_ID'], str(vmag), hdist)
                    continue
            
            
            line = [curdate.strftime('%d/%m/%Y'), t.__str__(rpar=0)]
            mainid = row['MAIN_ID']
            line.append(mainid)
            #alt_names = Simbad.query_objectids(row['MAIN_ID'])
            alt_names = customSimbad.query_object_ids(row['MAIN_ID'])
            if code_table[code]['use_name']:
                lname = ''
                for an in alt_names:
                    #if an['ID'].startswith('NAME '):
                    if an.startswith('NAME '):
                        if len(lname) > 0:
                            lname += ' / '
                        #lname += an['ID'].replace("NAME ", '')
                        lname += an.replace("NAME ", '')
                line.append(lname)
            for colname in code_table[code]['columns']:
                locid = ''
                for an in alt_names:
                    #if an['ID'].startswith(colname.upper() + ' '):
                    if an.startswith(colname.upper() + ' '):
                        if len(locid) > 0:
                            locid += ' / '
                        #locid = locid + an['ID'].replace("*", "") 
                        locid = locid + an.replace("*", "") 
                line.append(locid)
            if code_table[code]['phi_vec']:
                line.append(str(row['FLUX_V']))
          
            line.append(str(dist))
            line.append(str(ra))
            line.append(str(dec))
            lines.append(line)
            objects_per_day += 1
        curdate = curdate + datetime.timedelta(days=1)
        if objects_per_day > 0:
            lines = sorted(lines, key=lambda x: x[1])
            for line in lines:
                rowx, colx = write_row(ws, line, rowx, colx)
            rowx, colx = write_row(ws, [''], rowx, colx)
        print "Day %d/%d finished" % (numday+1, all_days)
        if progressBar is not None:
            progressBar.setValue((numday+1.0) / all_days * 100)
    filename = code.upper() + '_'
    filename += day_start.strftime('%d-%m-%Y')
    filename += '--'
    filename += day_end.strftime('%d-%m-%Y')
    filename += '.xls'
    full_filename = OUTPUTDIR+filename
    print full_filename
    wb.save(full_filename)
    return
    
if __name__ == '__main__':
    d1 = datetime.datetime.strptime('01/01/2015', '%d/%m/%Y')
    d2 = datetime.datetime.strptime('01/01/2038', '%d/%m/%Y')
    cat = [
           #'aco',
           #'gcl',
           #'hh',
           #'hip',
           #'lbn',
           'leda'#,
           #'ocl',
           #'pn'#,
           #'qso'#,
           #'snr'
           ]
    for c in cat:
        aw_main_process(c, d1, d2)
        
    #raise ConnectionError(e, request=request)
