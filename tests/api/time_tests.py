from __future__ import annotations

from api.time import Time


def Test_Minutes_TestSeconds_ExpectMinutes() -> None:
   assert Time.minutes( 1480.8 ) == 24.68


def Test_Clock_TestMinutesAndSeconds_ExpectMinutes() -> None:
   minutes = 14
   seconds = 19
   assert Time.clock( '%d:%02d' % ( minutes, seconds ) ) == (
      minutes + seconds / Time.SECONDS_PER_MINUTE )
