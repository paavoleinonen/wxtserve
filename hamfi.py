# -*- coding: utf-8 -*-

# Copyright (C) 2011 Paavo Leinonen <paavo.leinonen@iki.fi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import time

def hamfigenerator(data,prefix="",locator=""):
	d=[]	
	for e in data:
		m=data[e]
		r=[]
		r.append(prefix+m.name)
		r.append(str(m.value))
		r.append(m.unit)
		r.append(time.strftime("%Y%m%d%H%M%S",time.gmtime(m.timestamp))) #timestamp
		r.append(locator)
		r.append("") #asl
		r.append(m.longname)

		resultrow=';'.join(r)
		d.append(resultrow)


	if len(d)>0:
		d.append("")
	return "\n".join(d)
		
