#!/usr/bin/env python

##
## Simple usage example of TorInfo
##

import os
import sys
import stat
import types

from twisted.python import log
from twisted.internet import reactor, defer
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import UNIXClientEndpoint
from zope.interface import implements

from txtorcon import TorProtocolFactory, TorInfo
from txtorcon.torinfo import MagicContainer, ConfigMethod

def more(x):
    print 'foo',x
    reactor.stop()

def setup_complete(info):
    print "Got info"
    info.dump()
    d = info.features.names()
    d.addCallback(more)
    
def setup_failed(arg):
    print "SETUP FAILED",arg
    reactor.stop()

def bootstrap(c):
    conf = TorInfo(c)
    conf.post_bootstrap.addCallback(setup_complete).addErrback(setup_failed)

point = None
try:
    if os.stat('/var/run/tor/control').st_mode & (stat.S_IRGRP | stat.S_IRUSR | stat.S_IROTH):
        print "using control socket"
        point = UNIXClientEndpoint(reactor, "/var/run/tor/control")
except OSError:
    pass

if point is None:
    point = TCP4ClientEndpoint(reactor, "localhost", 9051)
    
d = point.connect(TorProtocolFactory())
# do not use addCallbacks() here, in case bootstrap has an error
d.addCallback(bootstrap).addErrback(setup_failed)
reactor.run()