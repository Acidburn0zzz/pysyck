
import unittest
import syck
import threading
import cStringIO

# NOTE: Highly unscientific test!
N = 10000
M = 50000

DATA_FOR_PARSER = '- ~\n'*M
DATA_FOR_EMITTER = syck.Seq([syck.Scalar('a scalar') for k in range(M)])

class MyThread(threading.Thread):

    def __init__(self, N):
        threading.Thread.__init__(self)
        self.value = N
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            self.value -= 1

    def done(self):
        return self.value < 0

class TestThreads(unittest.TestCase):

    def testParser(self):
        thread = MyThread(N)
        thread.start()
        syck.parse(DATA_FOR_PARSER)
        thread.stop()
        #print "testParser value:", thread.value
        self.assert_(thread.done())

    def testEmitter(self):
        thread = MyThread(N)
        thread.start()
        syck.emit(DATA_FOR_EMITTER)
        thread.stop()
        #print "testEmitter value:", thread.value
        self.assert_(thread.done())

