import sys
import os
import argparse
from .display import StdDisplay
from .repeatfunction import RepeatFunction
from .notifier import SummaryNotifier, AlertNotifier
# TODO Add support for parsing Common Logs - Factory constructor
from .logparser import CommonLogParser, W3CLogParser 
from . import __version__

def get_parser():
    parser = argparse.ArgumentParser(
            description="""logmonitor monitors a w3c log file:
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
            default = 2, type = int)
            # TODO ASTERISK set defaults
            #default = 10, type = int)
    parser.add_argument('-i', '--hitsinterval',
            help='interval in seconds to retain total website hits',
            default = 10, type = int)
            #default = 120, type = int)
    parser.add_argument('-t', '--hitsthreshold',
            help='hits threshold',
            default = 15, type = int)
            #default = 20, type = int)
    parser.add_argument('-l', '--logtype',
            help='type of log file',
            default = 'common',
            choices=['w3c', 'common'])
    parser.add_argument('-v', '--version',
            help='displays the current version of logmonitor',
            action='store_true')
    return parser


def logmonitor(args):
    # display
    display = StdDisplay()
    
    # summary notifier
    summary_notifier = SummaryNotifier(display)
    # repeatedly call notify method of summary_notifier 
    # every summary_interval seconds
    summary_notifier_repeater = RepeatFunction(args['summaryinterval'], 
                                               summary_notifier.notify)
    summary_notifier_repeater.setDaemon(True)
    summary_notifier_repeater.start()

    # alert notifier
    alert_notifier = AlertNotifier(display, 
                                   args['hitsinterval'], 
                                   args['hitsthreshold'])
    
    logfilepath = args['logfilepath']
    logparser = W3CLogParser(logfilepath)
    if args['logtype'] == 'common':
        logparser = CommonLogParser(logfilepath)

    for linedata in logparser.parsedlines():
        summary_notifier.insert_data(linedata)
        alert_notifier.insert_data(linedata)
        alert_notifier.notify()

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
    
    try:
        logmonitor(args)
    except(KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main() 
