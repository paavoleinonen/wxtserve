# Copyright (C) 2011 Paavo Leinonen <paavo.leinonen@iki.fi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

def CRC_calculate(str):
    crc=0
    for c in str:
        ch=ord(c)
        for i in range(8):
            if ((crc&1)^(ch&1)):
                crc=(crc>>1)^0xa001
            else:
                crc>>=1
            ch>>=1    
    return chr(0x40|(crc>>12))+chr(0x40|((crc>>6)&0x3f))+chr(0x40|(crc&0x3f))

def CRC_check(str):
    crc=CRC_calculate(str[:-3])
    if (crc!=str[-3:]):
        return False
    return True
