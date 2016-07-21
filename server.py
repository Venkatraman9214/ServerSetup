from twisted.application import service, internet
from twisted.python.log import ILogObserver
from twisted.internet import reactor, task
from createfile import createfile
import socket
import sys, os
import imageio
import pylab
from time import time
sys.path.append(os.path.dirname(__file__))
from kademlia.network import Server
from kademlia import log
from threading import Thread
import re


application = service.Application("kademlia")
application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)


ip_pool = ['10.0.0.2','10.0.0.3','10.0.0.4','10.0.0.5','10.0.0.6','10.0.0.7','10.0.0.8','10.0.0.9','10.0.0.10','10.0.0.11','10.0.0.12']
resourceDict = {}

st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
st.connect(('10.0.0.1', 8468)) 
local_ip = st.getsockname()[0]


# Request other's resources by sending a UDP broadcast
def resourceDiscovery():
    print "Sending broadcast request"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = "Hello,Give me your resources"
    sock.sendto(data, ('10.0.0.2', 8468))
    sock.sendto(data, ('10.0.0.3', 8468))
    sock.sendto(data, ('10.0.0.4', 8468))
    sock.sendto(data, ('10.0.0.5', 8468))
    sock.close()

    so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = '10.0.0.1'
    port = 8468 
    so.bind((host,port))
    i = 0
    while True:
        data, addr = so.recvfrom(1024)
        print "From: "+ str(addr) +"Recieved : "+ str(data)
        resourceDict[addr[0]] = data
        if data is not None:
            break
    so.close()  


def fileread():
    f = open('Textfile.txt','r')
    l = f.read(8120)
    return l

def done(result):
    print "Key result:", result
    reactor.stop()

def setDone(result, server):
    server.get("110").addCallback(done)

def bootstrapDone(found, server):
    print "*** Putting a value"
    server.set("110", fileread()).addCallback(setDone, server)
 
#resourceDiscovery()

if os.path.isfile('cache.pickle'):
    print "*** @ if block"
    #kserver = Server()
    kserver = Server.loadState('cache.pickle')
    kserver.bootstrap([("10.0.0.1", 8468)]).addCallback(bootstrapDone, kserver)
else:
    print "*** @ else block"
    kserver = Server()
    kserver.bootstrap([("10.0.0.1", 8468)]).addCallback(bootstrapDone, kserver)
kserver.saveStateRegularly('cache.pickle', 10)

server = internet.UDPServer(8468, kserver.protocol)
server.setServiceParent(application)







