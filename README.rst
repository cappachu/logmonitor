
logmonitor: a w3c log monitor
====================================================

.. image:: https://raw.github.com/mtamrf/logmonitor/master/misc/logmonitor.jpeg


logmonitor monitors a w3c log file repeatedly displaying summaries of website traffic and alerts when traffic crosses beyond a specified threshold. 

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
    usage: logmonitor.py [-h] [-s SECTIONINTERVAL] [-i HITSINTERVAL]
                         [-t HITSTHRESHOLD] [-v]
                         [logfilepath]
    
    logmonitor monitors a w3c log file: a summary of website traffic is displayed
    every sectioninterval seconds and alerts are displayed if total website hits
    are greater than hitsthreshold in the last hitsinterval seconds
    
    positional arguments:
      logfilepath           log file path
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SECTIONINTERVAL, --sectioninterval SECTIONINTERVAL
                            interval in seconds to display section summary
      -i HITSINTERVAL, --hitsinterval HITSINTERVAL
                            interval in seconds to retain total website hits
      -t HITSTHRESHOLD, --hitsthreshold HITSTHRESHOLD
                            hits threshold
      -v, --version         displays the current version of logmonitor



Improvements
------------
- 
- 


