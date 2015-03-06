
from threading import Lock 

class BaseDisplay(object):
    def __init__(self):
        super(BaseDisplay, self).__init__()
    
    def show(self, message):
        """Override this method to display message.
        A messge is a list of text lines"""
        raise NotImplementedError(self.__class__.__name__ + '.show')


class StdDisplay(BaseDisplay):
    def __init__(self):
        BaseDisplay.__init__(self)
        self.lock = Lock()

    def show(self, message):
        with self.lock:
            if message:
                for line in message:
                    print line
