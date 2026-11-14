"""Run the suite with a per-test deadlock trace instead of an endless CI job."""
import faulthandler
import sys
import unittest


class TimedResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        faulthandler.dump_traceback_later(90, exit=True)

    def stopTest(self, test):
        faulthandler.cancel_dump_traceback_later()
        super().stopTest(test)


class TimedRunner(unittest.TextTestRunner):
    resultclass = TimedResult


if __name__ == '__main__':
    arguments = sys.argv if len(sys.argv) > 1 else [sys.argv[0], 'discover', '-s', 'tests', '-v']
    try:
        unittest.main(module=None, argv=arguments, testRunner=TimedRunner)
    finally:
        faulthandler.cancel_dump_traceback_later()
