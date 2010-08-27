#!/usr/bin/env python
""" monitcall.py - Call and monitor executables for cpu blocks

    usage:
    usage: monitcall.py [-h] [-a ARGS] [-t CYCLES] [-l LIMIT] [-s SIGNAL]
                     [-d DEBUGLOG] [-v] cmd

    The script will call the given command (CMD) together with the
    given arguments (ARGS). If the CPU usage of the command is higher
    than the given limit (LIMIT) for more than CYCLES cycles
    the command is killed with the signal SIGNAL.

    Example:
    ./monitcall.py wvWare -a '-c utf-8 --nographics mydocument.doc'

    Extracts the contents of the MS-Word document `mydocument.doc` to
    an utf-8 text printed on stdout.

    Known issues:
    - The option string must not start with `-a`. Like this:

    ... -a '-a 4 -c utf-8 ...'

"""

# python imports
import datetime
import logging
import logging.handlers
import sys
import threading
import time
from subprocess import Popen, PIPE

# third party imports
import psutil
import argparse


logger = logging.getLogger('Monitcall')
logger.setLevel(logging.INFO)


class Monit(threading.Thread):

    killed = False

    def __init__(self, pid, cyles, limit, signal, verbose):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event()
        self._sleepperiod = 1.1
        self.pid = pid
        self.cyles = cyles
        self.limit = limit
        self.signal = signal
        self.verbose = verbose

    def run(self):
        count = 0
        try:
            proc = psutil.Process(self.pid)
        except (IOError, psutil.NoSuchProcess):
            return
        while not self._stopevent.isSet():
            self._stopevent.wait(self._sleepperiod)
            try:
                cpu = proc.get_cpu_percent()
            except psutil.NoSuchProcess:
                self._stopevent.set()
                cpu = 0.0
            if cpu > self.limit:
                count += 1
                if self.verbose:
                    sys.stderr.write('cpu at level %s pass %s\n' % (cpu, count))
            if count >= self.cyles:
                proc.kill(self.signal)
                self.killed = True
                self._stopevent.set()

    def join(self, timeout=None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)


class Call(threading.Thread):

    pid = 0
    result = ''

    def __init__(self, cmd, args):
        threading.Thread.__init__(self)
        self.cmd = ' '.join([cmd, args])

    def run(self):
        self.p = Popen(self.cmd, stdout=PIPE, shell=True)
        self.pid = self.p.pid

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)
        self.result = self.p.communicate()[0]


def parse_args():
    # Handle arguments
    parser = argparse.ArgumentParser(
        description="Call an executable in noblocking mode")
    parser.add_argument('cmd', help='Command to execute')
    parser.add_argument('-a', '--args', type=str, default='',
            help='Command arguments')
    parser.add_argument('-t', '--cycles', type=int, default=5,
            help='Timeout cycles of 1.1 seconds. Default: 5')
    parser.add_argument('-l', '--limit', type=float, default=90.0,
            help='CPU usage limit. Default: 90.0')
    parser.add_argument('-s', '--signal', type=int, default=9,
            help='Signal to kill process. Default: 9 (SIGKILL)')
    parser.add_argument('-d', '--debuglog', default='',
            help='Path to debuglog. Outputs 100 chars of processes stdout.')
    parser.add_argument('-v', '--verbose', default=False,
                        action='store_true',
                        help='Be more verbose')
    return parser.parse_args()


def execute(args):
    # Start command thread
    c = Call(args.cmd, args.args)
    c.start()

    # Wait until a PID is available
    while c.pid == 0:
        time.sleep(0.1)

    # Start monitoring thread
    m  = Monit(c.pid, args.cycles, args.limit, args.signal, args.verbose)
    m.start()
    c.join()

    # Log 100 chars of commands output, if it was killed for debugging
    # purposes
    if m.killed and args.verbose:
        stripped_result = ' '.join([i.strip() for i in c.result.split() if
                                    i.strip()])
        now = datetime.datetime.utcnow()
        logger.info('[%s] "%s" failed. Debug output: %s' % (
            now.strftime('%Y-%m-%d %H:%M:%S'), args.cmd, stripped_result[:100]))
    return c.result


def main():
    # Parse commandline arguments
    args = parse_args()

    # Setup logging, if in verbose mode:
    if args.debuglog:
        try:
            handler = logging.handlers.RotatingFileHandler(args.debuglog)
            logger.addHandler(handler)
        except (IOError, OSError):
            e = sys.exc_info()[1]
            sys.stderr.write("Couldn't open logfile: %s (%s). No log available\n" %
                             (args.debuglog, e))

    # Do the payload
    result = execute(args)

    # Print stdout of command
    sys.stdout.write(result)

if __name__ == '__main__':
     main()
