
import re
import datetime
import time

class LogParser(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def tail(self, logfile):
        """Generator that yields lines in a file starting at the end"""
        logfile.seek(0,2)
        while True:
            line = logfile.readline()
            if not line:
                time.sleep(0.1)
                continue
            if line:
                yield line

    @property
    def fields(self):
        fields = ['host', 'ignore', 'user', 'date', 'request', 'status', 'size']
        return fields


    def parse_line(self, line):
        # TODO compile RE in class or closure 
        line_pattern = re.compile('([^ ]*) ([^ ]*) ([^ ]*) \[([^]]*)\] "([^"]*)" ([^ ]*) ([^ ]*)')
        match = line_pattern.match(line)
        if not match:
            return None
        linedata = dict(zip(self.fields, match.groups()))
        # NOTE ignoring time zone
        time, zone = linedata['date'].split()
        # add new time field
        linedata['time'] = datetime.datetime.strptime(time, "%d/%b/%Y:%H:%M:%S") 
        return linedata

    def parsedlines(self):
        """Tails common log format file and yields dictionaries 
        corresponding to log lines"""
        with open(self.filepath, "rU") as logfile:
            loglines = self.tail(logfile)
            for line in loglines:
                linedata = self.parse_line(line)
                yield linedata
