# -*- coding: utf-8 -*-

# Copyright (C) 2011, 2013 Paavo Leinonen <paavo.leinonen@iki.fi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import sdi12

import time

class measurement:
    def __init__(self,name,value,unit,longname='',timestamp=None):
        if timestamp:
            self.timestamp=timestamp
        else:
            self.timestamp=time.time()
        self.value=value
        self.unit=unit
        self.longname=longname
        self.name=name

    def __str__(self):
        return "%s %s %s (%s)"%(self.name,str(self.value),self.unit,self.longname)


class stats:
    def __init__(self):
        self.messages=0
        self.crc_error=0
        self.parse_error=0
        self.since=time.time()
    
    def message(self):
        self.messages+=1

    def error_crc(self):
        self.crc_error+=1

    def error_parse(self):
        self.parse_error+=1

    def age(self):
        return self.since-time.time()

    def __str__(self):
        return "processed %d messages in %d seconds (CRC: %d, parse: %d)"%\
            (self.messages,self.age(),self.crc_error,self.parse_error)


class measurementparser:
    def __init__(self,longname='',units=None):
        self.units=units
        self.longname=longname

    def parse(self,key,value):
        if not self.units:
            return measurement(key,value,"",self.longname)

        munit=value[-1]
        if munit=='#':
            return None # No valid measurement data
        
        mvalue=value[:-1]
        mvalue=float(mvalue)

        if munit in self.units:
            munit=self.units[munit]
   
        return measurement(key,mvalue,munit,self.longname)

        
unit_MKSN={'M':'m/s','K':'km/h','S':'mph','N':'knots'}
unit_D={'D':'degrees'}
unit_HPBMI={'H':'hPa','P':'Pa','B':'bar','M':'mmHg','I':'inHg'}
unit_CF={'C':'°C','F':'°F'}
unit_P={'P':'%RH'}
unit_MI={'M':'mm','I':'in'}
unit_S={'S':'s'}
unit_rain_intensity={'M':'mm/h','I':'in/h'}
unit_hail_accumulation={'M':'hits/cm²','I':'hits/in²','H':'hits'}
unit_V={'V':'V'}
unit_hail_intensity={'M':'hits/cm²h','I':'hits/in²h','H':'hits/h'}

measurementlookup={
    'Sn':measurementparser('Wind speed minimum',unit_MKSN),
    'Sm':measurementparser('Wind speed average',unit_MKSN),
    'Sx':measurementparser('Wind speed maximum',unit_MKSN),

    'Dn':measurementparser('Wind direction minimum',unit_D),
    'Dm':measurementparser('Wind direction average',unit_D),
    'Dx':measurementparser('Wind direction maximum',unit_D),

    'Pa':measurementparser('Air pressure',unit_HPBMI),

    'Ta':measurementparser('Air temperature',unit_CF),
    'Tp':measurementparser('Internal temperature',unit_CF),

    'Ua':measurementparser('Relative humidity',unit_P),

    'Rc':measurementparser('Rain accumulation',unit_MI),
    'Rd':measurementparser('Rain duration',unit_S),
    'Ri':measurementparser('Rain intensity',unit_rain_intensity),

    'Hc':measurementparser('Hail accumulation',unit_hail_accumulation),
    'Hd':measurementparser('Hail duration',unit_S),
    'Hi':measurementparser('Hail intensity',unit_hail_intensity),
    'Hp':measurementparser('Hail peak intensity',unit_hail_intensity),

    'Th':measurementparser('Heating temperature',unit_CF),

    'Vh':measurementparser('Heating voltage',unit_V),
    'Vs':measurementparser('Supply voltage',unit_V),
    'Vr':measurementparser('3.3 V reference voltage',unit_V),

    'Id':measurementparser('Information')
    }


class parser:
    def __init__(self):
        self.stats=stats()
        self.measurements={}
        self.reset()

    def reset(self):
        self.indata=''
        
    def feed(self,data):
        self.indata+=data
        while True:
            row,rest=self.indata.split('\n',1)
            if not rest:
                break # No complete row in buffer, exit
            self.indata=rest
            row=row.strip()

            self.stats.message()

            # "aR1,Dn=1....\r\n" without checksum
            # "ar1,Dn=1....???\r\n with checksum
            # a==address -- ignored
            # 1==message type -- ignored
            
            if row[1]=='r':
                if not sdi12.CRC_check(row):
                    self.stats.error_crc()
                    continue # CRC mismatch, ignore row
                row=row[:-3]

            parseerror=False
            pieces=row.split(',')
            for p in pieces[1:]:
                try:
                    k,v=p.split('=')
                    if k in measurementlookup:
                        m=measurementlookup[k].parse(k,v)
                        if m==None:
                            if k in self.measurements:
                                del self.measurements[k]
                        else:
                            self.measurements[k]=m
                    else:
                        print "Unknown: %s"%(k)
                except ValueError:
                    parseerror=True
                    continue

            if parseerror:
                self.stats.error_parse()



f=open("input.txt","rt")
p=parser()

for r in f.readlines():
    p.feed(r)

for m in p.measurements:
    print "%s %s"%(m,p.measurements[m])

print p.stats

f.close()
