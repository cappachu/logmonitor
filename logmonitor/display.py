
from threading import Lock 
from clint.textui import puts, colored
from .notifier import MESSAGE_TYPES

class BaseDisplay(object):
    def __init__(self):
        super(BaseDisplay, self).__init__()
    
    def show(self, message):
        """Override this method to display message.
        A message is a list of text lines"""
        raise NotImplementedError(self.__class__.__name__ + '.show')


class StdDisplay(BaseDisplay):
    def __init__(self):
        BaseDisplay.__init__(self)
        self.lock = Lock()

    def show(self, message):
        with self.lock:
            if message.type == MESSAGE_TYPES.summary:
                for line in message.lines:
                    puts(line)
            elif message.type == MESSAGE_TYPES.alert:
                for line in message.lines:
                    puts(colored.red(line))

class CursesDisplay(BaseDisplay):
    pass
