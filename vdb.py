from coord import coord
import numpy as np
from astroquery.vizier import Vizier
from compute import *
from utils import parse_date, parse_coord

def process_vdb(vdbname, gfields, sun, ind, ra_interest, dec_interest, print_coord = True, print_head = True):
    
    lcol = 12
    fields = [] + gfields
    fields.append('RAJ2000')
    fields.append('DEJ2000')
    v = Vizier(columns = fields, catalog = vdbname)
    v.ROW_LIMIT = -1
    result = v.query_constraints(catalog = vdbname, RAJ2000 = ra_interest, DEJ2000 = dec_interest)
    #result[result.keys()[0]].pprint()

    numobjs = len(result[0])
    twelveoc = 12*60*60
    tms = twelveoc*np.array([1., 3., 4.])

    prline = '==========' + '=' + '============'
    prhead = 'Date      ' + ' ' + ' Time       '
    
    l = len(fields)
    if not print_coord:
        l -= 2
        
    for i in xrange(l):
        prline = prline + '=' + '='*lcol
        tmp = fields[i]
        if len(tmp) < lcol:
            tmp = tmp + ' '*(lcol - len(tmp))
        prhead = prhead + ' ' + tmp
    prhead = prhead + ' ' + 'Dec distance'
    prline = prline + '=' + '============'
     
    if print_head:   
        print prline
        print prhead
        print prline
    
    for i in xrange(numobjs):
        ri = result[0][i].as_void()
        ri= list(ri)
        ri=ri[:-2]
        [ra, dec] = [ri[-2], ri[-1]]
        ra = parse_coord( ra, 'ra', ' ')
        dec = parse_coord( dec, 'deg', ' ')
        t, num = comp_time(sun[ind-1][1], sun[ind][1], sun[ind+1][1], ra)
        t = t.f2s()

        if num > 0:
            t += 2*twelveoc
        tmp = tms - t
        sz = tmp[tmp > 0].size
        if sz == 1:
            idx = ind+1
        elif sz == 2:
            idx = ind
        elif sz == 3:
            idx = ind-1
        t = coord(0, 0, t + twelveoc, 1, 'ra')
        if idx == ind:
            curdate = sun[idx][0]
            tmp = str(curdate[0])
            if len(tmp) <  2:
                tmp = ' ' + tmp
            date = '' + tmp + '/'
            tmp = str(curdate[1])
            if len(tmp) < 2:
                tmp = ' ' + tmp
            date = date + tmp + '/' + str(curdate[2])
            dist = comp_dist(curdate[0], curdate[1], t, dec)

            printer = '' + date + ' ' + str(t)
            
            stri = [str(x) for x in ri[:-2]]
            if print_coord:
                stri = stri + [str(ra), str(dec)]
            
            for x in stri:
                if len(x) < lcol:
                    x = ' '*(lcol - len(x)) + x
                printer = printer + ' ' + x
            printer = printer + ' ' + str(dist)
            print printer

def handle_date(date, records, catalogue, vphi = 15):
    mdays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    sun = []
    for i in xrange(len(records[0])):
        sun.append([parse_date(records[0][i]), parse_coord(records[1][i], 'ra'), parse_coord(records[2][i], 'deg')])
    ay = sun[ 0][0][-1]
    by = sun[-1][0][-1]
    
    if len(date) == 3:
        im = 1 # index of month
        iy = 2 # index of year (in date list)
       
    elif len(date) == 2:
        im = 0
        iy = 1
    
    assert (date[im] >   0) and (date[im] <= 12), "Inccorect month value"
    assert (date[iy] >= ay) and (date[iy] <= by), "Selected year is not presented in current sun ephemeris"
    
    if catalogue == 'V/50':
        fields = ['Name', 'HD', 'Vmag']
        entry_phrase = "Catalogue V50: stars with m <= 6.5"
    elif catalogue == 'VII/239A/icpos':
        entry_phrase = "\nCatalogue VII/239A/icpos: mean position of NGC/IC objects"
        fields = ['NGC/IC']
    else:
        print "Unknown catalogue"
        return None
    
    if date[iy] % 4 == 0:
        mdays[1] += 1
    
    if len(date) == 3:
        days = [date[0]]
    elif len(date) == 2:
        days = range(1, mdays[date[im]-1] + 1)
        
    for ind0, row in enumerate(sun):
        if [days[0], date[im], date[iy]] in row:
            break
            
    print entry_phrase

    for ind in xrange(ind0, ind0 + len(days)):

        ra_interest = str(sun[ind-1][1]) + '..' + str(sun[ind+1][1])
        a = sun[ind-1][2]
        b = sun[ind+1][2]
        if a.f2s() < b.f2s():
            c = a
            d = b
        else:
            c = b
            d = a

        phi = coord(vphi,0,0,1,'deg')

        dec_interest = str(c - phi) + '..' + str(d + phi)

        ra_interest = ra_interest.replace(' ', '')
        dec_interest = dec_interest.replace(' ', '')

        if ind != ind0:
            prhead = False
        else:
            prhead= True
        process_vdb(catalogue, fields, sun, ind, ra_interest, dec_interest, print_head = prhead)
        print
