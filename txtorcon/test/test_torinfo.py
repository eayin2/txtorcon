import os
import shutil
import tempfile
import functools

from zope.interface import implements
from twisted.trial import unittest
from twisted.test import proto_helpers
from twisted.internet import defer, error
from twisted.python.failure import Failure

from txtorcon import TorControlProtocol, ITorControlProtocol, TorInfo

class FakeControlProtocol:
    """
    """
    
    implements(ITorControlProtocol)

    def __init__(self, answers):
        self.answers = answers
        self.post_bootstrap = defer.succeed(self)

    def get_info_raw(self, info):
        if len(self.answers) == 0:
            d = defer.Deferred()
            self.pending.append(d)
            return d
        
        d = defer.succeed(self.answers[0])
        self.answers = self.answers[1:]
        return d
    get_info = get_info_raw

class CheckAnswer:
    def __init__(self, test, ans):
        self.answer = ans
        self.test = test

    def __call__(self, x):
        self.test.assertTrue(x == self.answer)

class InfoTests(unittest.TestCase):
    
    def setUp(self):
        self.protocol = FakeControlProtocol([])

    def test_simple(self):
        self.protocol.answers.append('''info/names=
something a documentation string
multi/path a documentation string
''')
        info = TorInfo(self.protocol)
        self.assertTrue(hasattr(info, 'something'))
        self.assertTrue(hasattr(info, 'multi'))
        self.assertTrue(hasattr(getattr(info,'multi'), 'path'))

        self.protocol.answers.append('foo')

        d = info.something()
        d.addCallback(CheckAnswer(self, 'foo'))
        return d
    
    def test_with_arg(self):
        self.protocol.answers.append('''info/names=
multi/path/arg/* a documentation string
''')
        info = TorInfo(self.protocol)
        self.assertTrue(hasattr(info, 'multi'))
        self.assertTrue(hasattr(getattr(info,'multi'), 'path'))
        self.assertTrue(hasattr(getattr(getattr(info,'multi'), 'path'), 'arg'))

        self.protocol.answers.append('bar')

        try:
            info.multi.path.arg()
            self.assertTrue(False)
        except TypeError, e:
            pass
        
        d = info.multi.path.arg('quux')
        d.addCallback(CheckAnswer(self, 'bar'))
        return d