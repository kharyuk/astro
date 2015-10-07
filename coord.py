# Class for coordinates
# can be used for hours/degree variables
import numpy as np


class coord():
    h = None
    m = None
    s = None
    sign = None
    hlim = None
    mlim = None
    slim = None
    type = None
    
    def truncate(self, h, m, s):
        d = np.trunc(s / self.slim)
        s = s % self.slim
        m += d
        d = np.trunc(m / self.mlim)
        m = m % self.mlim
        h += d
        d = np.trunc(h / self.hlim)
        h = h % self.hlim
        return [int(h), int(m), float(s)]
    
    def f2s(self):
        [h,m,s] = [self.h, self.m, self.s]
        m += h*self.mlim
        s += m*self.slim
        return s*self.sign

    def f2hd(self):
        g = self.f2s()
        g /= (self.slim * self.mlim)
        return g
    
    def __init__(self, a, b, c,sign = 1, type = 'ra'):
        self.sign = sign
        self.type = type
        if type == 'ra':
            self.hlim = 24.
            self.mlim = 60.
            self.slim = 60.
        elif type == 'deg':
            self.hlim = 360.
            self.mlim = 60.
            self.slim = 60.
        else:
            print 'Unknown type'
        [self.h, self.m, self.s] = self.truncate(abs(a), abs(b), abs(c))
        return
    
    def __str__(self):
        if self.type == 'ra':
            sg = ' '
        elif self.sign > 0:
            sg = '+'
        elif self.sign < 0:
            sg = '-'
        else:
            sg = ' '
        [sh, sm, ss] = [str(self.h), str(self.m), str(round(self.s, 2))]
        if len(sh) < 2:
            sh = ' ' + sh
        if len(sm) < 2:
            sm = ' ' + sm
        ss = ss.split('.')
        if len(ss[0]) < 2:
            ss[0] = ' ' + ss[0]
        if len(ss[1]) == 1:
            ss[1] = ss[1] + ' '
        if len(ss[1]) == 0:
            ss[1] = '  '
        ss = ss[0] + '.' + ss[1]
            
        return sg+ sh + ':' + sm + ':' + ss
    
    def __repr__(self):
        return self.type + ':  ' + self.__str__()
    
    def __add__(self, c):
        #[h, m, s] = [self.h + c.h, self.m + c.m, self.s + c.s]
        #coo = self.truncate(h, m, s)
        assert self.type == c.type, "Bad types"
        s1 = self.f2s()
        s2 = c.f2s()
        s3 = s1 + s2
        return coord(0,0,abs(s3),np.sign(s3), type = self.type)
    
    def __sub__(self, c):
        assert self.type == c.type, "Bad types"
        s1 = self.f2s()
        s2 = c.f2s()
        s3 = s1 - s2
        return coord(0,0,abs(s3),np.sign(s3),  type = self.type)
    
    def __div__(self, t):
        s = self.f2s()
        return abs(s / t)
