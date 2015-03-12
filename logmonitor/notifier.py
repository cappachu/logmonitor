
import datetime
from .logparser import LINE_DATA_FIELDS
from .utils import enum


MESSAGE_TYPES = enum('summary', 'alert')

class Message(object):
    """Messages sent to Displays by Notifiers"""
    def __init__(self, lines, type):
        super(Message, self).__init__()
        self.lines = lines
        self.type = type


class BaseNotifier(object):
    """Base class for notifiers, responsible for sending
    messages to displays"""
    def __init__(self, display):
        super(BaseNotifier, self).__init__()
        self.display = display

    def insert_data(self, data):
        raise NotImplementedError(self.__class__.__name__ + '.insert_data')
    
    @property
    def message(self):
        raise NotImplementedError(self.__class__.__name__ + '.message')

    def notify(self): 
        self.display.show(self.message)


class SummaryNotifier(BaseNotifier):
    """Responsible for collecting information about popular
    website sections and summary stats and forwarding them to display"""
    def __init__(self, display):
        BaseNotifier.__init__(self, display)
        self.section_2_hits = {}
        self.bytes = 0
        self.error_code_count = 0

    def insert_data(self, linedata):
        section = linedata[LINE_DATA_FIELDS.section]
        self.section_2_hits[section] = self.section_2_hits.get(section, 0) + 1
        self.bytes += linedata[LINE_DATA_FIELDS.bytes]
        statuscode = linedata[LINE_DATA_FIELDS.status]
        # 400 and above status codes are errors 
        if statuscode >= 400:
            self.error_code_count += 1

    def purge_data(self):
        self.section_2_hits = {}
        self.error_code_count = 0
        self.bytes = 0

    @property
    def message(self):
        # copy data (to return) and purge 
        section_2_hits = self.section_2_hits.copy()
        error_code_count = self.error_code_count
        bytes = self.bytes
        self.purge_data()
        
        lines = ["-" * 25,
                 "*** SUMMARY ***",
                 "",
                 "Total Kilobytes Transferred: %d" % (bytes/1024),
                 "HTTP Errors: %d" % error_code_count,
                 ""
                 ]
        if section_2_hits:
            lines.append("Popular Sections:")
            for section, hits in section_2_hits.items():
                lines.append("%s : %d hits" % (section, hits))
        lines.append("-" * 25)
        message = Message(lines, MESSAGE_TYPES.summary)
        return message


class AlertNotifier(BaseNotifier):
    """Responsible for determining when website hits cross
    a specified threshold and forwarding information to a display"""
    def __init__(self, display, interval, hits_threshold):
        BaseNotifier.__init__(self, display)
        self._interval = datetime.timedelta(seconds=interval)
        self.hits_threshold = hits_threshold
        self._time_2_hits = {}
        self.hits = 0
        self.is_alert_displayed = False

    def purge_old_data(self, event_time):
        # purge old data (determined by interval)
        for time, hits in self._time_2_hits.items():
            if time + self._interval < event_time:
                self.hits -= hits
                del self._time_2_hits[time]

    def insert_data(self, linedata):
        # insert current event
        event_time = linedata[LINE_DATA_FIELDS.datetime]
        self._time_2_hits[event_time] = self._time_2_hits.get(event_time, 0) + 1
        self.hits += 1
        self.notify()

    @property
    def message(self):    
        """Display a messages when hits threshold is crossed
        and when hits subsequently drops below threshold (recovers)."""
        # purge old data
        now = datetime.datetime.now().replace(microsecond=0)
        self.purge_old_data(now)
        # create message if necessary
        lines = []
        if self.hits > self.hits_threshold:
            if not self.is_alert_displayed:
                self.is_alert_displayed = True
                lines.extend(self.high_traffic_message(self.hits, now))
        elif self.is_alert_displayed:
            self.is_alert_displayed = False
            lines.extend(self.recovered_message(now))
        message = Message(lines, MESSAGE_TYPES.alert)
        return message

    def high_traffic_message(self, hits, time):
        message_str = "High traffic generated an alert - hits = %i, triggered at %s" % (hits, time)
        return [message_str]

    def recovered_message(self, time):
        message_str = "alert recovered at %s" % (time)
        return [message_str]
