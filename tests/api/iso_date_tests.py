from __future__ import annotations

from datetime import date

from api.iso_date import IsoDate


def Test_Parse_TestDate_ExpectThatDate() -> None:
   assert IsoDate.parse( '2008-03-12' ) == date( 2008, 3, 12 )


def Test_Parse_TestTimestamp_ExpectDatePortion() -> None:
   assert IsoDate.parse( '2008-03-12T00:00:00' ) == date( 2008, 3, 12 )


def Test_Parse_TestUtcTimestamp_ExpectDatePortion() -> None:
   assert IsoDate.parse( '2008-03-12T00:00:00Z' ) == date( 2008, 3, 12 )
