
import re
import datetime
import time


class BaseLogParser(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.logfile = None

    def follow(self, logfile):
        """Generator that yields lines in a file starting at the end"""
        logfile.seek(0,2)
        while True:
            line = logfile.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

    def parsedlines(self):
        """Tails common log format file and yields dictionaries 
        corresponding to log lines"""

        if self.logfile is None:
            # open file in universal newline mode
            self.logfile = open(self.filepath, "rU")
                
        with self.logfile:
            loglines = self.follow(self.logfile)
            for line in loglines:
                linedata = self.parse_line(line)
                yield linedata

    def parseline(self):
        raise NotImplementedError(self.__class__.__name__ + '.parseline')


class CommonLogParser(BaseLogParser):
    def __init__(self, filepath):
        BaseLogParser.__init__(self, filepath)

        self.fields = ['host', 'ignore', 'user', 'date', 'request', 'status', 'size']
        self.line_pattern = re.compile('([^ ]*) ([^ ]*) ([^ ]*) \[([^]]*)\] "([^"]*)" ([^ ]*) ([^ ]*)')

    def parse_line(self, line):
        match = self.line_pattern.match(line)
        if not match:
            # log error
            return None
        linedata = dict(zip(self.fields, match.groups()))
        # NOTE ignoring time zone
        time, zone = linedata['date'].split()
        # add new time field
        linedata['time'] = datetime.datetime.strptime(time, "%d/%b/%Y:%H:%M:%S") 
        return linedata
