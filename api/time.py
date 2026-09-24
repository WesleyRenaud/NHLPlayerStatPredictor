from __future__ import annotations


class Time():
   SECONDS_PER_MINUTE = 60.0


   @classmethod
   def minutes( cls, seconds: float ) -> float:
      return seconds / cls.SECONDS_PER_MINUTE
