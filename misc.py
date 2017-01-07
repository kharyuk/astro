import numpy as np
import requests
import urllib2
from bs4 import BeautifulSoup
import numpy as np

def alex_se(fname = None, loadfile = None):
    if loadfile is None:
        url = 'http://hea.iki.rssi.ru/~nik/ak/sun.htm'
        #proxy_handler = urllib2.ProxyHandler({})
        #opener = urllib2.build_opener(proxy_handler)
        #urllib2.install_opener(opener)


        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'
        request = urllib2.Request(url)
        request.add_header('User-agent', user_agent)


        response = urllib2.urlopen(request)

        soup = BeautifulSoup(response.read())

        txt = soup.pre.renderContents()
        lines = txt.splitlines()

        fields = []
        ln = lines[0].split() + lines[1].split()
        lenln = len(ln)
        for i in xrange(lenln/2):
            fields.append(ln[i])
            fields.append(ln[i + lenln/2])
        fields = filter(lambda x: (x!='*') and (x!='Sun'), fields)

        lenline = len(fields)
        sun_ephemeris = {}
        records = [[]]*lenline

        for line in lines[3:]:
            s = line.split()
            if len(s) != lenline:
                continue
            for i in xrange(lenline):
                records[i] = records[i] + [s[i]]
                
        if fname is not None:
            np.savez(fname, fields = fields, records = records)
    else:
        a = np.load(loadfile)
        records = a['records']
    return records

def harvardMPCExample():
    url = 'http://mpc.cfa.harvard.edu/ws/search'

    arg =  [['neo', 1], ['inclination_max', 2.0], ['spin_period_min', 5.0]]

    params = {}
    for i in range(1, len(arg)):
        params[arg[i][0]] = arg[i][1]

    r = requests.post(url, params, auth = ('mpc_ws', 'mpc!!ws'))

    #print r.text


    N = N_Epoch + 0.013967 * ( 2000.0 - Epoch ) + 3.82394E-5 * d

    # ecc = eccentricity; M - mean anomaly (deg); E - eccentric anomaly
    Eold = M + ecc*(180/np.pi) * np.sin(M) * ( 1.0 + ecc * np.cos(M) )
    Enew = Eold
    while Enew >= 0.05:
        Enew = Eold - ( Eold - ecc*(180/np.pi) * np.sin(Eold) - M ) / ( 1 - ecc * np.cos(Eold) )
        Eold = Enew
        # if not conv, ecc ~ 1 =>parabolic, not ell.


def g2j(r, g):
    rg = np.array([r, g])
    rg = np.reshape(rg, (-1,1))
    
    mat = np.array([[-0.60,  1.60],
                    [ 0.42,  0.58],
                    [ 1.15, -0.15]])
    bias = np.array([0.5, -0.03, 0.5])
    bias = np.reshape(bias, (-1,1))
    
    bvr = np.dot(mat, rg) + bias
    return bvr

def j2g(B, R):
    BR = np.array([B, R])
    BR = np.reshape(BR, (-1,1))
    
    mat = np.array([[-0.60,  1.60],
                    [ 1.15, -0.15]])
    bias = np.array([0.5, 0.5])
    bias = np.reshape(bias, (-1,1))
    
    invmat = np.linalg.inv(mat)
    
    rg = np.dot(invmat, BR - bias)
    return rg

def g2J(r, g):
    ret = -0.37*r + 1.37*g + 0.39
    return ret
