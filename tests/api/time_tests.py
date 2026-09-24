from __future__ import annotations

from api.time import Time


def Test_Minutes_TestSeconds_ExpectMinutes() -> None:
   assert Time.minutes( 1480.8 ) == 24.68
