
logmonitor: a http log monitor
====================================================

logmonitor monitors a http log file repeatedly displaying summaries of website traffic and alerts when traffic crosses beyond a specified threshold. It currently supports both the common log format as well as the w3c extended log format. 

::

    $ logmonitor access-log 


Installation
------------

::

    pip install git+https://github.com/mtamrf/logmonitor.git

or

::

    python setup.py install


Usage
-----

::
    usage: logmonitor.py [-h] [-s SUMMARYINTERVAL] [-i HITSINTERVAL]
                         [-t HITSTHRESHOLD] [-l {w3c,common}]
                         [-d {window,standard}] [-v]
                         [logfilepath]

    logmonitor monitors a http log file: a summary of website traffic is displayed
    every summaryinterval seconds and alerts are displayed if total website hits
    are greater than hitsthreshold in the last hitsinterval seconds

    positional arguments:
      logfilepath           log file path (default: None)

    optional arguments:
      -h, --help            show this help message and exit
      -s SUMMARYINTERVAL, --summaryinterval SUMMARYINTERVAL
                            interval in seconds to display summary (default: 10)
      -i HITSINTERVAL, --hitsinterval HITSINTERVAL
                            interval in seconds to retain total website hits
                            (default: 120)
      -t HITSTHRESHOLD, --hitsthreshold HITSTHRESHOLD
                            hits threshold (default: 20)
      -l {w3c,common}, --logtype {w3c,common}
                            type of log file (default: common)
      -d {window,standard}, --displaytype {window,standard}
                            type of display (default: window)
      -v, --version         displays the current version of logmonitor (default:
                            False)


Application Design Thoughts
---------------------------
- consider handling concurrency using alternative paradigm (event loops, message passing, async, coroutines, etc.)
- design could be centered around a data model built from the ground up for handling time series data

Improvements
------------
- display a countdown timer or progress bar to indicate to the user when to expect the next update
- support scrolling and saving windows, currently the alert history is limited to what can be displayed in a window  
- support for rotated log files
- application logging
- unit tests
- curses window display is not supported on all platforms
- testing alerting logic can be time consuming
- beautify display (add window titles, format text to fit window)




