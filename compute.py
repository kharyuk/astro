import numpy as np
from coord import coord

star_day = 60*60*24#86164.090530833 #seconds
    
def sundec(N):
    tmp = np.sin(-23.44 * np.pi / 180)
    tmp *= np.cos(2*np.pi / 365.24 * ( N + 10) + 2*0.0167*np.sin(2*np.pi / 365.24*(N-2)))
    return np.arcsin(tmp)*180/np.pi

def numdays(day, month, vis = False):
    mns = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if vis:
        mns[1] +=1
    mns = np.array(mns)
    month -= 1
    tmp = mns[:month].sum()
    tmp += day
    return tmp - 1

def comp_time(sun1, sun2, sun3, star):
    st = star.f2s()
    s1 = sun1.f2s()
    s2 = sun2.f2s()
    s3 = sun3.f2s()
    assert (st > s1) and (s3 > st), 'Object is not in interval'
    if st < s2:
        sun = sun1
        ds = sun2 - sun1
        num = 0
    else:
        sun = sun2
        ds = sun3 - sun2
        num = 1
    point = star - sun # intersection path
    pra = point.f2s() # path in seconds
    vra = ds / star_day # velocity
    t = coord(0, 0, pra / vra)# time of intersection
    return t, num

def comp_dist(day, mon, time, obj_dec):
    N = numdays(day, mon)
    tm = time.f2s()
    N += tm / star_day
    sd = sundec(N)
    sun_dec = coord(0,0,abs(sd)*3600,np.sign(sd),'deg')
    return sun_dec - obj_dec
