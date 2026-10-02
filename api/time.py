from __future__ import annotations


class Time():
   SECONDS_PER_MINUTE = 60.0


   @classmethod
   def minutes( cls, seconds: float ) -> float:
      return seconds / cls.SECONDS_PER_MINUTE


   @classmethod
   def clock( cls, value: str ) -> float:
      minutes, seconds = value.split( ':' )
      return int( minutes ) + int( seconds ) / cls.SECONDS_PER_MINUTE


   @classmethod
   def clock_string( cls, minutes: float ) -> str:
      total_seconds = round( minutes * cls.SECONDS_PER_MINUTE )
      whole_minutes, seconds = divmod( total_seconds, int( cls.SECONDS_PER_MINUTE ) )
      return '%d:%02d' % ( whole_minutes, seconds )


   @classmethod
   def clock_string_from_seconds( cls, seconds: float ) -> str:
      return cls.clock_string( cls.minutes( seconds ) )
