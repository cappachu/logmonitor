#!/usr/bin/env python

import unittest
import datetime
import random
from logmonitor.notifier import AlertNotifier
from logmonitor.display import StdDisplay
from logmonitor.logparser import CommonLogParser, LINE_DATA_FIELDS


class AlertingLogicTestCase(unittest.TestCase):
    def setUp(self):
        self.HITS_INTERVAL = 10
        self.HITS_THRESHOLD = 5
        self.common_log_parser = CommonLogParser('')
        self.display = StdDisplay()
        self.alert_notifier = AlertNotifier(self.display, self.HITS_INTERVAL, self.HITS_THRESHOLD)
    
    def tearDown(self):
        pass

    def create_log_line_with_time(self, datetime):
        logline_template = 'www.somedomain.com - - %s "GET /section/page.html HTTP/1.0" 200 969'
        datetime_str = datetime.strftime("[%d/%b/%Y:%H:%M:%S -0600]")
        logline = logline_template % datetime_str
        return logline

    def simulate_line_with_time(self, datetime):
        """feeds alert notifier with a parsed line with specified time"""
        line = self.create_log_line_with_time(datetime)
        linedata = self.common_log_parser.parse_line(line)
        self.alert_notifier.insert_data(linedata)

    def simulate_lines(self, start_time, end_time, num_lines):
        """feeds num_lines lines to alert notifier with times ranging from start_time to end_time"""
        time_delta = end_time - start_time
        delta_seconds = time_delta.total_seconds()
        # monotonically increasing
        intervals = sorted([random.randint(0,delta_seconds) for i in range(num_lines)])
        for i in intervals:
            self.simulate_line_with_time(start_time + datetime.timedelta(seconds=i))

    def test_alert(self):
        start_time = datetime.datetime(year=2015, month=4, day=1, hour=8, minute=30, second=0)
        end_time   = datetime.datetime(year=2015, month=4, day=1, hour=8, minute=30, second=10)
        self.simulate_lines(start_time, end_time, self.HITS_THRESHOLD + 1)
        assert self.alert_notifier.is_alert_displayed == True

    def test_do_not_alert(self):
        start_time = datetime.datetime(year=2015, month=4, day=1, hour=8, minute=30, second=0)
        end_time   = datetime.datetime(year=2015, month=4, day=1, hour=8, minute=30, second=10)
        self.simulate_lines(start_time, end_time, self.HITS_THRESHOLD - 2)
        assert self.alert_notifier.is_alert_displayed == False

    def test_recover(self):
        start_time = datetime.datetime(year=2015, month=4, day=1, hour=8, minute=30, second=0)
        end_time   = datetime.datetime(year=2015, month=4, day=1, hour=8, minute=30, second=10)
        self.simulate_lines(start_time, end_time, self.HITS_THRESHOLD + 1)
        assert self.alert_notifier.is_alert_displayed == True
        end_time   = datetime.datetime(year=2015, month=4, day=1, hour=8, minute=30, second=20)
        self.simulate_line_with_time(end_time)
        assert self.alert_notifier.is_alert_displayed == False
        

if __name__ == '__main__':
    unittest.main()

