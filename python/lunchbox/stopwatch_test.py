import time
import unittest

from lunchbox.stopwatch import StopWatch
# ------------------------------------------------------------------------------


class StopwatchTests(unittest.TestCase):
    def test_stopwatch(self):
        stopwatch = StopWatch()
        stopwatch.start()
        time.sleep(0.1)
        stopwatch.stop()

        delta = 1 * 1000000
        self.assertAlmostEqual(stopwatch.delta.microseconds, 1, delta=delta)
        self.assertRegex(stopwatch.human_readable_delta, '0.1.* second')

        stopwatch.start()
        time.sleep(0.2)
        stopwatch.stop()

        self.assertAlmostEqual(stopwatch.delta.microseconds, 2, delta=delta)
        self.assertRegex(stopwatch.human_readable_delta, '0.2.* seconds')
