import numpy as np
from coord import coord

def parse_date(date):
    tmp = date.split('/')
    return [int(tmp[0]), int(tmp[1]), int(tmp[2])]

def parse_coord(coo, type, div = ':'):
    tmp = coo.split(div)
    tmp = [float(t) for t in tmp]
    return coord(abs(tmp[0]), tmp[1], tmp[2], np.sign(tmp[0]), type)
