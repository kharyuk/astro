import requests
import xml.etree.ElementTree as ET

class Simbad():
    '''
    Fields:
        - timeout
        - cser
        - header
        - vot_fields
    '''
    
    def __init__(self,
                 timeout=500
                 ):
        self.timeout = timeout
        
        self.headers = {}
        self.headers['User-Agent'] = 'Astro junctions (Sun & static objects)'

        self.cser = 'simbad.u-strasbg.fr'
        
        self.vot_fields = ['MAIN_ID',
                           'RA',
                           'DEC']

    def make_prefix(self, name='vot1'):
        assert len(name) > 0
        assert isinstance(name, str)
        prefix = 'votable ' + name + ' {\n'
        for field in self.vot_fields:
            prefix += field + '\n'
        prefix += '}\n'
        return prefix, name
    
    def query_criteria(self, criteria):
        prefix, name = self.make_prefix()
        query_string = prefix + '\n'
        query_string += 'votable open ' + name + '\n'
        query_string += 'query sample ' + criteria + '\n'
        query_string += 'votable close'
        data = dict(script=query_string)
        pfrom = 'http://' + self.cser + '/simbad/sim-script'
        res = requests.get(pfrom, params=data, timeout=self.timeout, headers=self.headers)
        resp = self.parse_queried(res.text)
        resp = sorted(resp, key=lambda x: x['RA'])
        return resp
    
    def query_object_ids(self, name):
        query_string = 'format object f1'
        query_string += ' "'+'%IDLIST[%-30*\|'
        query_string = query_string[:-1]
        query_string += 'n]"\n'
        query_string += 'query id ' + name + '\n'
        query_string += 'format display f1'
        data = dict(script=query_string)
        pfrom = 'http://' + self.cser + '/simbad/sim-script'
        res = requests.get(pfrom, params=data, timeout=self.timeout, headers=self.headers)
        resp = self.parse_queried_ids(res.text)
        return resp
    
    def addVotField(self, fields):
        assert isinstance(fields, (str, list, tuple))
        if isinstance(fields, str):
            loc_fields = [fields]
        else:
            loc_fields = fields
        for field in loc_fields:
            if field in self.vot_fields:
                print field + ": duplicate"
            else:
                self.vot_fields.append(field)
        return
    
    def delVotField(self, fields):
        assert isinstance(fields, (str, list, tuple))
        if isinstance(fields, str):
            loc_fields = [fields]
        else:
            loc_fields = fields
        for field in loc_fields:
            if field not in self.vot_fields:
                print field + ": not presented"
            else:
                self.vot_fields.remove(field)
        return
    
    def parse_queried(self, res):
        str1 = '::data::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::'
        res = res.split(str1, 1)[1]
        while res.startswith('\n'):
            res = res[1:]
        root = ET.fromstring(res)
        cols = []
        for child in root[1][0]:
            if len(child.keys()) > 0:
                cols.append(child.attrib['ID'])
        res = []
        for q in root[1][0][-1][0]:
            tmp = {}
            i = 0
            for p in q:
                string = p.text
                if string is None:
                    string = ''
                #if cols[i] in ['DEC', 'RA']:
                #    string = string.replace(' ', ':')
                tmp[cols[i]] = string
                i += 1
            res.append(tmp)
        return res
    
    def parse_queried_ids(self, res):
        str1 = '::data::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::'
        res = res.split(str1, 1)[1]
        while res.startswith('\n'):
            res = res[1:]
        res = res.split('\n')
        if isinstance(res, str):
            res = [res]
        result = []
        for l in xrange(len(res)):
            while res[l].endswith(' '):
                res[l] = res[l][:-1]
            if len(res[l]) > 0:
                result.append(res[l])
        return result
        
if __name__ == '__main__':
    crit = 'cat in (hip) & rah > 0.5 & rah < 0.51'
    customSimbad = Simbad()
    customSimbad.addVotField(['flux(V)', 'id(ngc)'])
    resp = customSimbad.query_criteria(crit)
    print resp

    resp2 = customSimbad.query_object_ids('HD 107259')
    print resp2
