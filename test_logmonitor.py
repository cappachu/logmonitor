#!/usr/bin/env python

import unittest
import time
import datetime
import random
from logmonitor.notifier import AlertNotifier
from logmonitor.logparser import CommonLogParser, LINE_DATA_FIELDS

class AlertingLogicTestCase(unittest.TestCase):
    def setUp(self):
        self.HITS_INTERVAL = 5
        self.OVER_HITS_INTERVAL = self.HITS_INTERVAL + 1
        self.HITS_THRESHOLD = 5
        self.OVER_THRESHOLD = self.HITS_THRESHOLD + 1
        self.UNDER_THRESHOLD = self.HITS_THRESHOLD - 1
        self.common_log_parser = CommonLogParser('')
        self.display = None
        self.last_event_time = None
        self.alert_notifier = AlertNotifier(self.display, 1, self.HITS_INTERVAL, self.HITS_THRESHOLD)
        self.alert_notifier.start()
        
    def tearDown(self):
        self.alert_notifier.stop() 

    def create_log_line(self):
        logline_template = 'www.somedomain.com - - %s "GET /section/page.html HTTP/1.0" 200 969'
        self.last_event_time = time.time()
        datetime_str = time.strftime("[%d/%b/%Y:%H:%M:%S -0600]",time.localtime(self.last_event_time))
        logline = logline_template % datetime_str
        return logline

    def simulate_line(self):
        """feeds alert notifier with a parsed line with specified time"""
        line = self.create_log_line()
        linedata = self.common_log_parser.parse_line(line)
        self.alert_notifier.insert_data(linedata)

    def simulate_lines(self, time_period, num_lines):
        """feeds num_lines lines to alert notifier with times ranging from start_time to end_time"""
        if num_lines > 0:
            time_period_seconds = time_period.total_seconds()
            next_call = time.time()
            ## monotonically increasing interval boundaries
            interval_boundaries = sorted([random.randint(0,time_period_seconds) for i in range(num_lines+1)])
            for i in range(len(interval_boundaries) - 1):
                interval = interval_boundaries[i+1] - interval_boundaries[i]  
                next_call = next_call + interval
                sleep_time = next_call - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.simulate_line()

    def test_alert(self):
        time_period = datetime.timedelta(seconds=self.HITS_INTERVAL)
        self.simulate_lines(time_period, self.OVER_THRESHOLD)
        assert self.alert_notifier.is_alert_displayed == True

    def test_do_not_alert(self):
        time_period = datetime.timedelta(seconds=self.HITS_INTERVAL)
        self.simulate_lines(time_period, self.UNDER_THRESHOLD)
        assert self.alert_notifier.is_alert_displayed == False

    def test_recover(self):
        time_period = datetime.timedelta(seconds=self.HITS_INTERVAL)
        self.simulate_lines(time_period, self.OVER_THRESHOLD)
        assert self.alert_notifier.is_alert_displayed == True
        # wait till last event time + interval
        sleep_time = self.last_event_time + self.OVER_HITS_INTERVAL
        time.sleep(self.last_event_time + self.OVER_HITS_INTERVAL - time.time())
        assert self.alert_notifier.is_alert_displayed == False

    def test_do_not_recover(self):
        time_period = datetime.timedelta(seconds=self.HITS_INTERVAL)
        self.simulate_lines(time_period, self.OVER_THRESHOLD)
        assert self.alert_notifier.is_alert_displayed == True
        time_period = datetime.timedelta(seconds=self.HITS_INTERVAL)
        self.simulate_lines(time_period, self.OVER_THRESHOLD)
        assert self.alert_notifier.is_alert_displayed == True
        

if __name__ == '__main__':
    unittest.main()

