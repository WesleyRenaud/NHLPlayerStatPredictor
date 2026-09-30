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


def Test_ClockString_TestDecimalMinutes_ExpectMinutesAndSeconds() -> None:
   assert Time.clock_string( 18.5 ) == '18:30'


def Test_ClockString_TestRoundingSeconds_ExpectMinuteCarry() -> None:
   assert Time.clock_string( 18.999 ) == '19:00'
