from __future__ import annotations

from api.time import Time


def Test_Minutes_TestSeconds_ExpectMinutes() -> None:
   seconds = 1480.8

   minutes = Time.minutes( seconds )

   assert minutes == seconds / Time.SECONDS_PER_MINUTE


def Test_Clock_TestMinutesAndSeconds_ExpectMinutes() -> None:
   minutes = 14
   seconds = 19
   clock = '%d:%02d' % ( minutes, seconds )

   value = Time.clock( clock )

   assert value == minutes + seconds / Time.SECONDS_PER_MINUTE
