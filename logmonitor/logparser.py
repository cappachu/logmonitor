
import re
import datetime
import time
import os
from .utils import enum

# Fields of a line used for metrics and stats
LINE_DATA_FIELDS = enum('section', 'bytes', 'datetime', 'status')

class LogParseError(Exception):
    """Exception raised for parse errors"""
    def __init__(self, msg, line=None):
        self.msg = msg
        self.line = line

    def __str__(self):
        result = self.msg
        if self.line is not None:
            result = result + ", on line: %s" % self.line
        return result

class BaseLogParser(object):
    """Base class for following and parsing a text file"""
    # TODO add support for rotated log files
    def __init__(self, filepath):
        super(BaseLogParser, self).__init__()
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
                if linedata is not None: 
                    yield linedata

    def parse_line(self, line):
        """parse line is responsible returning a 
        dictionary containing a subset of the data 
        fields in the line formatted for convenience
        of computing monitoring metrics and stats"""
        raise NotImplementedError(self.__class__.__name__ + '.parseline')


class CommonLogParser(BaseLogParser):
    """Follows and Parses Common Log Format files"""
    def __init__(self, filepath):
        BaseLogParser.__init__(self, filepath)
        self.fieldnames = ['host', 'referrer', 
                           'user', 'datetime',
                           'request', 'status', 
                           'bytes']
        self.line_pattern = re.compile('([^ ]*) ([^ ]*) ([^ ]*) \[([^]]*)\] "([^"]*)" ([^ ]*) ([^ ]*)')

    def parse_line(self, line):
        line = line.strip()
        match = self.line_pattern.match(line.strip())
        if not match:
            raise LogParseError("Unexpected line format", line)
        datadict = dict(zip(self.fieldnames, match.groups()))
        return self.linedata(datadict)

    def parse_int(self, str_val):
        result = 0
        if str_val != '-':
            result = int(str_val)
        return result

    def linedata(self, datadict):
        """returns a dictionary with relevant values
        given a dictionary of fields corresponding to
        a log line"""
        linedata = {}
        # NOTE ignoring time zone
        time, zone = datadict['datetime'].split()
        linedata[LINE_DATA_FIELDS.datetime] = datetime.datetime.strptime(time, "%d/%b/%Y:%H:%M:%S") 
        # parse section 
        host = datadict['host']
        _, uri, _ = datadict['request'].split()
        uri_parts = uri.split('/')
        section = ''
        if len(uri_parts) > 2:
            section = uri_parts[1]
        section = host + '/' + section
        linedata[LINE_DATA_FIELDS.section] = section
        linedata[LINE_DATA_FIELDS.status] = self.parse_int(datadict['status'])
        linedata[LINE_DATA_FIELDS.bytes] = self.parse_int(datadict['bytes'])
        return linedata

        
class W3CLogParser(BaseLogParser):
    """Follows and Parses W3C Extended Log Format files"""
    def __init__(self, filepath):
        BaseLogParser.__init__(self, filepath)
        self.fieldnames = None

    def parse_line(self, line):
        line = line.strip()
        datadict = None
        if self.fieldnames is None:
            self.fieldnames = self.find_last_field_directive()
        words = line.strip().split()
        if len(words) > 0:
            # Field directive lines
            if words[0] == "#Fields:":
                self.fieldnames = words[1:]
            # convert entity lines to dictionaries
            elif words[0][0] != '#':
                datadict = dict(zip(self.fieldnames, words))
        # ignore non entity and field directive lines
        if datadict is None:
            return None

        return self.linedata(datadict)
    
    def parse_int(self, str_val):
        result = 0
        if str_val != '-':
            result = int(str_val)
        return result

    def parse_date(self, date_str):
        # Date Entry:
        # <date>  = 4<digit> "-" 2<digit> "-" 2<digit>
        date_val = None
        date_pattern = "%Y-%m-%d"
        date_val = datetime.datetime.strptime(date_str, date_pattern)
        return date_val

    def parse_time(self, time_str):
        # Time Entry:
        # <time>  = 2<digit> ":" 2<digit> [":" 2<digit> ["." *<digit>]
        time_val = None  
        time_pattern = re.compile(r"""
                                  ^(?P<hour>\d{2})          # 2 digit hour
                                  :(?P<minute>\d{2})         # 2 digit minute
                                  (:(?P<second>\d{2}))?      # optional 2 digit second
                                  (\.(?P<microsecond>\d+))?$ # optional multidigit microsecond
                                  """, re.VERBOSE)
        match = re.match(time_pattern, time_str)
        if match:
            time_dict = {k:int(v) for k,v in match.groupdict().items() if v is not None}
            # NOTE ignoring microsecond
            if time_dict['second'] is None:
                time_val = datetime.time(time_dict['hour'], time_dict['minute'])
            else:
                time_val = datetime.time(time_dict['hour'], time_dict['minute'], time_dict['second'])
        return time_val


    def linedata(self, datadict):
        linedata = {}
        # parse section
        host = datadict.get('cs-host', datadict.get('s-ip', '')) 
        uri = datadict.get('cs-uri-path', datadict.get('cs-uri', datadict.get('cs-uri-stem', '')))
        uri_parts = uri.split('/')
        section = ''
        if len(uri_parts) > 2:
            section = uri_parts[1]
        section = host + '/' + section
        linedata[LINE_DATA_FIELDS.section] = section
        # TODO check whether lines may have only one of date and time
        date_val = self.parse_date(datadict['date'])
        time_val = self.parse_time(datadict['time'])
        status_val = self.parse_int(datadict.get('sc-status', datadict.get('status')))
        bytes_val = self.parse_int(datadict.get('sc-bytes', datadict.get('bytes')))
        datetime_val = datetime.datetime.combine(date_val, time_val)
        linedata[LINE_DATA_FIELDS.datetime] = datetime_val
        linedata[LINE_DATA_FIELDS.status] = status_val
        linedata[LINE_DATA_FIELDS.bytes] = bytes_val
        return linedata

    def find_last_field_directive(self):
        """Traverses the file in reverse finding last Field directive"""
        fieldnames = None
        # save current position
        position = self.logfile.tell()
        for line in self.readlines_reverse():
            words = line.strip().split()
            if len(words) > 0 and words[0] == "#Fields:":
                fieldnames = words[1:]
                break
        # go back to saved position
        self.logfile.seek(position)
        return fieldnames
    
    def readlines_reverse(self):
        """Generator that yields lines from a file in reverse"""
        # TODO read in larger blocks
        # TODO verify logfile is valid file object
        self.logfile.seek(0, os.SEEK_END)
        position = self.logfile.tell()
        line = ''
        while position >= 0:
            self.logfile.seek(position)
            next_char = self.logfile.read(1)
            if next_char == os.linesep: 
                yield line[::-1]
                line = ''
            else:
                line += next_char
            position -= 1
        yield line[::-1]
