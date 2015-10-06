import urllib2
from bs4 import BeautifulSoup

def alex_se(fname = None):
    url = 'http://hea.iki.rssi.ru/~nik/ak/sun.htm'

    soup = BeautifulSoup(urllib2.urlopen(url).read())

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
    return records
