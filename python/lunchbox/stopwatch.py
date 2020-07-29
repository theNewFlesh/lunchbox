from typing import Optional

import datetime
import humanfriendly
# ------------------------------------------------------------------------------


class StopWatch():
    '''
    StopWatch is used for timing blocks of code.
    '''
    def __init__(self):
        # type: () -> None
        self._delta = None  # type: Optional[datetime.timedelta]
        self._start_time = None  # type: Optional[datetime.datetime]
        self._stop_time = None  # type: Optional[datetime.datetime]

    def start(self):
        # type: () -> None
        '''
        Call this method directly before the code you wish to time.
        '''
        self._stop_time = None
        self._start_time = datetime.datetime.now()

    def stop(self):
        # type: () -> None
        '''
        Call this method directly after the code you wish to time.
        '''
        if self._start_time is not None:
            self._stop_time = datetime.datetime.now()

    @property
    def delta(self):
        # type: () -> datetime.timedelta
        '''
        Time delta of stop - start.
        '''
        return self._stop_time - self._start_time  # type: ignore

    @property
    def human_readable_delta(self):
        # type: () -> str
        '''
        Time delta in human readable format.
        '''
        return humanfriendly.format_timespan(self.delta.total_seconds())
