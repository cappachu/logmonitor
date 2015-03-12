#!/usr/bin/env python

import sys
import os
import argparse
import curses
from .display import StdDisplay, WindowDisplay
from .repeatfunctionthread import RepeatFunctionThreadError
from .notifier import SummaryNotifier, AlertNotifier
from .logparser import CommonLogParser, W3CLogParser 
from . import __version__

def get_parser():
    parser = argparse.ArgumentParser(
            description="""logmonitor monitors a http log file:
                           a summary of website traffic is displayed
                           every summaryinterval seconds
                           and alerts are displayed if total website hits
                           are greater than hitsthreshold in the last
                           hitsinterval seconds""",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('logfilepath', 
            help='log file path',
            nargs='?')
    parser.add_argument('-s', '--summaryinterval', 
            help='interval in seconds to display summary',
            default = 10, type = int)
    parser.add_argument('-i', '--hitsinterval',
            help='interval in seconds to retain total website hits',
            default = 120, type = int)
    parser.add_argument('-t', '--hitsthreshold',
            help='hits threshold',
            default = 20, type = int)
    parser.add_argument('-l', '--logtype',
            help='type of log file',
            default = 'common',
            choices=['w3c', 'common'])
    parser.add_argument('-d', '--displaytype',
            help='type of display',
            default = 'window',
            choices = ['window', 'standard'])
    parser.add_argument('-v', '--version',
            help='displays the current version of logmonitor',
            action='store_true')
    return parser


def logmonitor(args, display):
    # setup summary notifier
    # repeatedly call notify method of summary_notifier every summary_interval seconds
    summary_notifier = SummaryNotifier(display, args['summaryinterval'])
    summary_notifier.start()

    # setup alert notifier
    # repeatedly call notify method of alert_notifier every second
    alert_notifier = AlertNotifier(display, 1, args['hitsinterval'], args['hitsthreshold'])
    alert_notifier.start()

    
    logfilepath = args['logfilepath']
    logparser = None
    if args['logtype'] == 'common':
        logparser = CommonLogParser(logfilepath)
    else: # 'w3c'
        logparser = W3CLogParser(logfilepath)

    for linedata in logparser.parsedlines():
        summary_notifier.insert_data(linedata)
        alert_notifier.insert_data(linedata)


def run_with_windowdisplay(win, args):
    display = WindowDisplay(win)
    logmonitor(args, display)


def run_with_stddisplay(args):
    display = StdDisplay()
    logmonitor(args, display)
    

def main():
    parser = get_parser()
    args = vars(parser.parse_args())
    
    if args['version']:
        print(__version__)
        return

    if not args['logfilepath']:
        parser.print_help()
        return

    if not os.path.exists(args['logfilepath']):
        print "Invalid File Path:", args['logfilepath']
        return

    display_type = args['displaytype']
    if display_type == 'window':
        try:
            curses.wrapper(run_with_windowdisplay, args)
        except RepeatFunctionThreadError as e:
            # print any exceptions raised by thread after
            # curses wrapper has reset terminal
            print e
        except(KeyboardInterrupt, SystemExit):
            sys.exit(0)
    else: # 'standard' display
        try:
            run_with_stddisplay(args)
        except RepeatFunctionThreadError as e:
            print e
        except(KeyboardInterrupt, SystemExit):
            sys.exit(0)


if __name__ == '__main__':
    main() 
