import numpy as np
from coord import coord

def parse_date(date):
    tmp = date.split('/')
    return [int(tmp[0]), int(tmp[1]), int(tmp[2])]

def parse_coord(coo, type, div = ':'):
    tmp1 = coo.split(div)
    tmp = [float(t) for t in tmp1]
    if len(tmp) == 1:
        tmp.append(0)
        tmp.append(0)
    if len(tmp) == 2:
        tmp.append(0)

    c = coo[0]
    if c == '-':
        sgn = -1
    else:
        sgn = 1
    return coord(abs(tmp[0]), tmp[1], tmp[2], sgn, type)
