import unittest
import StringIO
import sys
import re

from monitcall import execute


CPUPAT = re.compile("cpu at level ([0-9.]*) pass ([0-9]*)")

class DummyArgs(object):

    cmd = 'echo'
    args = '"foo bar"'
    cycles = 2
    limit = 80
    signal = 9
    verbose = False


class MonitcallTests(unittest.TestCase):
    """ Test monitcall implementation """

    def test_simplecall(self):
        args = DummyArgs()
        self.assertEqual(execute(args), 'foo bar\n')

    def test_exit(self):
        args = DummyArgs()
        args.cmd = 'python'
        args.args = 'endless.py'
        args.verbose = True
        out = StringIO.StringIO()
        sys.stderr = out
        execute(args)
        sys.stderr = sys.__stderr__
        f = CPUPAT.findall(out.getvalue())
        self.failUnlessEqual(len(f), args.cycles)
        for i in range(args.cycles):
            self.failIf(float(f[i][0]) <= args.limit)


def test_suite():
    """returns the test suite"""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

