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
   minutes = 18
   seconds = 30
   decimal_minutes = minutes + seconds / Time.SECONDS_PER_MINUTE

   assert Time.clock_string( decimal_minutes ) == '%d:%02d' % ( minutes, seconds )


def Test_ClockString_TestRoundingSeconds_ExpectMinuteCarry() -> None:
   minutes = 18
   seconds = 59.94
   decimal_minutes = minutes + seconds / Time.SECONDS_PER_MINUTE

   assert Time.clock_string( decimal_minutes ) == f'{ minutes + 1 }:00'


def Test_ClockStringFromSeconds_TestMinutesAndSeconds_ExpectFormattedClock() -> None:
   minutes = 18
   seconds = 30
   total_seconds = minutes * Time.SECONDS_PER_MINUTE + seconds

   assert Time.clock_string_from_seconds( total_seconds ) == '%d:%02d' % ( minutes, seconds )


def Test_ClockStringFromSeconds_TestFractionalSeconds_ExpectMinuteCarry() -> None:
   minutes = 18
   seconds = 59.9
   total_seconds = minutes * Time.SECONDS_PER_MINUTE + seconds

   assert Time.clock_string_from_seconds( total_seconds ) == f'{ minutes + 1 }:00'


def Test_ClockStringFromSeconds_TestZero_ExpectZeroClock() -> None:
   assert Time.clock_string_from_seconds( 0.0 ) == '0:00'
