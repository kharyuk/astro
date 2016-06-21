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
