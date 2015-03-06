import sys
import os
import argparse
from .display import StdDisplay
from .repeatfunction import RepeatFunction
from .notifier import SectionNotifier, AlertNotifier
from .logparser import CommonLogParser
from . import __version__


def get_parser():
    parser = argparse.ArgumentParser(
            description="""logmonitor monitors a w3c log file:
                           a summary of website traffic is displayed
                           every sectioninterval seconds
                           and alerts are displayed if total website hits
                           are greater than hitsthreshold in the last
                           hitsinterval seconds""")
    parser.add_argument('logfilepath', 
            help='log file path',
            nargs='?')
    parser.add_argument('-s', '--sectioninterval', 
            help='interval in seconds to display section summary',
            default = 2, type = int)
            #default = 10, type = int)
    parser.add_argument('-i', '--hitsinterval',
            help='interval in seconds to retain total website hits',
            default = 10, type = int)
            #default = 120, type = int)
    parser.add_argument('-t', '--hitsthreshold',
            help='hits threshold',
            default = 15, type = int)
            #default = 20, type = int)
    parser.add_argument('-v', '--version',
            help='displays the current version of logmonitor',
            action='store_true')
    return parser


def logmonitor(args):
    # display
    display = StdDisplay()
    
    # section notifier
    section_notifier = SectionNotifier(display)
    # repeatedly call notify method of section_notifier 
    # every section_interval seconds
    section_notifier_repeater = RepeatFunction(args['sectioninterval'], 
                                               section_notifier.notify)
    section_notifier_repeater.setDaemon(True)
    section_notifier_repeater.start()

    # alert notifier
    alert_notifier = AlertNotifier(display, 
                                   args['hitsinterval'], 
                                   args['hitsthreshold'])

    logparser = CommonLogParser(args['logfilepath'])
    for linedata in logparser.parsedlines():
        section_notifier.insert_data(linedata)
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
    
    logmonitor(args)


if __name__ == '__main__':
    main() 
