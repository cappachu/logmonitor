
from threading import Lock 
from clint.textui import puts, colored
from .notifier import MESSAGE_TYPES
import curses

class BaseDisplay(object):
    """Base class for text output"""
    def __init__(self):
        super(BaseDisplay, self).__init__()
    
    def show(self, message):
        """Override this method to display message.
        A message is a list of text lines"""
        raise NotImplementedError(self.__class__.__name__ + '.show')


class StdDisplay(BaseDisplay):
    """Standard Display for text output"""
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


class WindowDisplay(BaseDisplay):
    """Displays text in windows using curses"""
    def __init__(self, window):
        BaseDisplay.__init__(self)
        self._window = window
        self._setup_gui()
        self.lock = Lock()

    def show(self, message):
        with self.lock:
            if message.type == MESSAGE_TYPES.summary:
                # clear subwindow
                self.left_subwindow.erase()
                for line in message.lines:
                    self.write_line(line+'\n', self.left_subwindow, scroll=False)
                self.left_subwindow.border()
                self.left_subwindow.refresh()
            elif message.type == MESSAGE_TYPES.alert:
                for line in message.lines:
                    self.write_line(line+'\n', self.right_subwindow)
                self.right_subwindow.border()
                self.right_subwindow.refresh()

    def _setup_gui(self):
        """Setup left and right curses windows"""
        curses.curs_set(0)
        height, width = self._window.getmaxyx()
        self.left_subwindow = curses.newwin(height, width/3, 0, 0)
        self.right_subwindow = curses.newwin(height, 2*width/3, 0, width/3)
        self.left_subwindow.border()
        self.left_subwindow.refresh()
        self.right_subwindow.border()
        self.right_subwindow.refresh()
    
    def line_2_sublines(self, line, window_width):
        """Splits a text line into pieces that fit 
        in the width of a window"""
        sublines = [line]
        if len(line) > window_width:
            first = line[0:window_width - 1] + "\n"
            rest = window_width - (len("> ") + 1)
            remaining = ["> " + line[i:i + rest] + "\n"
                         for i in range(window_width - 1, len(line), rest)]
            remaining[-1] = remaining[-1][0:-1]
            sublines = [first] + remaining
        return sublines

    
    def write_line(self, line, subwindow, scroll=True):
        """Write line to subwindow, splitting line into sublines
        that fit in the subwindow if necessary"""
        height, width = subwindow.getmaxyx()
        window_width = width - 2
        y,x = subwindow.getyx()
        if y == 0 and x == 0:
            subwindow.move(1,0)
        for subline in self.line_2_sublines(line, window_width):
            y, x = subwindow.getyx()
            # stop if scrolling is disabled and window is full
            if y >= height - 1 and not scroll:
                return
            if y >= height - 1:
                # scroll up when window is full
                subwindow.move(1, 1)
                subwindow.deleteln()
                subwindow.move(y - 1, 1)
                subwindow.deleteln()
                subwindow.addstr(subline)
            else:
                subwindow.move(y, x + 1)
                subwindow.addstr(subline)



