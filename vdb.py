from coord import coord
import numpy as np
from astroquery.vizier import Vizier
from compute import *
from utils import parse_date, parse_coord

def process_vdb(vdbname, fields, sun, ind, ra_interest, dec_interest, print_coord = True):
    
    lcol = 12
    
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
