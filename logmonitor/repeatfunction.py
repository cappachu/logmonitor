
from threading import Thread, Event
import Queue
import time
import sys
import traceback


class RepeatFunctionThreadError(Exception):
    def __init__(self, traceback):
        self.traceback = traceback

    def __str__(self):
        return "Repeat Function Thread Error Traceback:\n" + self.traceback


class RepeatFunctionThread(Thread):
    """Thread that repeatedly calls function every interval seconds"""
    def __init__(self,interval,function,*args,**kwargs):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self._exceptionqueue = Queue.Queue()
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
            try:
                self.function(*self.args,**self.kwargs)
            except Exception as e:
                # any exceptions raised by the function are put in a queue
                error = RepeatFunctionThreadError(traceback.format_exc())
                self._exceptionqueue.put(error)

    def raise_any_exceptions(self):
        """Can be used by parent thread to capture any 
           exceptions raised by self.function"""
        try:
            error = self._exceptionqueue.get(block=False)
        except Queue.Empty:
            pass
        else:
            raise error  


