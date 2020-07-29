import time
import unittest

from lunchbox.stopwatch import StopWatch
# ------------------------------------------------------------------------------


class StopwatchTests(unittest.TestCase):
    def test_stopwatch(self):
        stopwatch = StopWatch()
        stopwatch.start()
        time.sleep(0.01)
        stopwatch.stop()

        self.assertAlmostEqual(stopwatch.delta.microseconds, 10000, delta=10000)
        self.assertEqual(stopwatch.human_readable_delta, '0.01 seconds')

        stopwatch.start()
        time.sleep(0.02)
        stopwatch.stop()

        self.assertAlmostEqual(stopwatch.delta.microseconds, 20000, delta=10000)
        self.assertEqual(stopwatch.human_readable_delta, '0.02 seconds')
