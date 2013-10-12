# -*- coding: utf-8 -*-

# Copyright (C) 2011, 2013 Paavo Leinonen <paavo.leinonen@iki.fi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import wxt520
import sys
import hamfi
import socket
import threading
import time

class config:
    def __init__(self):
        self.params={}

    def loadfile(self,filename):
        f=open(filename,'rt')
        for r in f.readlines():
            r=r.strip()
            if len(r)<1:
                continue
            if r[0]=='#':
                continue
            pieces=r.split('=',1)
            if len(pieces)<2:
                self.params[pieces[0]]=True
            else:
                self.params[pieces[0]]=pieces[1]
        f.close()
        
    def getint(self,name,default=None):
        if name in self.params:
            return int(self.params[name])
        return default

    def get(self,name,default=None):
        if name in self.params:
            return self.params[name]
        return default

localconfig=config()

datamessage=""

class wxt_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def handle(self,conn):
	global datamessage
	prefix=localconfig.get('prefix','')
	locator=localconfig.get('locator','')

        w=wxt520.parser()
        while True:
            msg=conn.recv(4096)
            if w.feed(msg):
		datamessage=hamfi.hamfigenerator(w.measurements,prefix,locator)

    def run(self):
        backoff=1
        while True:
            try:
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		hostport=(localconfig.get('wxthost'), localconfig.getint('wxtport',7000))
		print("Connecting to %s:%d"%hostport)
                s.connect(hostport)
                print("Connected.")
                backoff=1 # connection succeeded
            except:
                print("Disconnected waiting %d seconds."%(backoff))
                time.sleep(backoff)
                backoff*=1.5
                if backoff>5*60:
                    backoff=5*60
                continue
            self.handle(s)
            s.close()
            



class listen_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global datamessage

        # open listening socket
        s_listen=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	hostport=(localconfig.get('listenhost',''), localconfig.getint('listenport',8000))
        s_listen.bind(hostport)
        s_listen.listen(10)

	print("Listening on %s:%d"%hostport)

        # process connections
        while True:
            c,source=s_listen.accept()
            print("Connection from %s:%d"%source)
            c.sendall(datamessage)
            c.close()


def main():
    for e in sys.argv[1:]:
        try:
            localconfig.loadfile(e)
            print("Loaded config %s"%(e))
        except:
            print("Loading of config %s failed"%(e))
            return

    l=listen_thread()
    l.daemon=True
    w=wxt_thread()
    w.daemon=True

    l.start()
    w.start()

    while True:
        time.sleep(10)
    
    

if __name__=='__main__':
    main()
