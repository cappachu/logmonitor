
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
        if statuscode >= 400:
            self.error_code_count += 1

    def purge_data(self):
        self.section_2_hits = {}
        self.error_code_count = 0
        self.bytes = 0

    @property
    def message(self):
        # copy and purge 
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
    def __init__(self, display, interval, hits_threshold):
        BaseNotifier.__init__(self, display)
        self._interval = datetime.timedelta(seconds=interval)
        self.hits_threshold = hits_threshold
        # time of last event inserted
        self._last_event_time = datetime.datetime.now()
        self._time_2_hits = {}
        self.hits = 0
        self.is_alert_displayed = False
    
    def insert_data(self, linedata):
        event_time = linedata[LINE_DATA_FIELDS.datetime]
        # purge old data (determined by interval)
        if event_time > self._last_event_time:
            self._last_event_time = event_time
            for time, hits in self._time_2_hits.items():
                if time + self._interval < event_time:
                    self.hits -= hits
                    del self._time_2_hits[time]
        self._time_2_hits[event_time] = self._time_2_hits.get(event_time, 0) + 1
        self.hits += 1

    @property
    def message(self):    
        lines = []
        #print 'HITS:', self.hits
        if self.hits > self.hits_threshold:
            if not self.is_alert_displayed:
                self.is_alert_displayed = True
                lines.extend(self.high_traffic_message(self.hits, self._last_event_time))
        elif self.is_alert_displayed:
            self.is_alert_displayed = False
            lines.extend(self.recovered_message(self._last_event_time))
        message = Message(lines, MESSAGE_TYPES.alert)
        return message

    def high_traffic_message(self, hits, time):
        message_str = "High traffic generated an alert - hits = %i, triggered at %s" % (hits, time)
        return [message_str]

    def recovered_message(self, time):
        message_str = "alert recovered at %s" % (time)
        return [message_str]
