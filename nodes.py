import socket
import random
from multiprocessing import Process

mult = 0
node = []

class Peer:
    nodeid = 0
    state = 1
    __privatekey = 0

    def __init__(self, nodeid):
        self.nodeid = nodeid
        self.state = 1

    def printid(self):
        print self.nodeid

    def servercode(self):
        global mult
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 3202
        s.bind(('', port))
        print "socket binded to %s" %(port)
        s.listen(5)
        while mult < 100:
            print "socket is listening", mult
            #while True:
            c, addr = s.accept()
            print 'Got connection from', addr
            c.send('Thank you for connecting ')
            c.close()
            mult +=1
        s.close()

    def clientcode(self):
        global mult
        while mult < 100:
            print 'client'
            s = socket.socket()
            port = 3202
            s.connect(('127.0.0.1', port))
            print s.recv(1024)
            s.close()
            mult += 1

for i in range(5):
    x = random.randint(12000, 30000)
    node.append(Peer(x))
    node[i].printid()

#p1 = Process(target = node[1].servercode)
#p1.start()
#p2 = Process(target = node[2].clientcode)
#p2.start()
