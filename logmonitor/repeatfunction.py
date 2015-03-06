
from threading import Thread, Event
import time

class RepeatFunction(Thread):
    """Thread that repeatedly calls function every interval seconds"""
    def __init__(self,interval,function,*args,**kwargs):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._terminate = Event()

    def stop(self):
        self._terminate.set()
   
    def run(self):
        next_call = time.time()
        while not self._terminate.isSet():
            next_call = next_call + self.interval;
            self._terminate.wait(next_call - time.time())
            self.function(*self.args,**self.kwargs)
