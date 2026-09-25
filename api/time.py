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
