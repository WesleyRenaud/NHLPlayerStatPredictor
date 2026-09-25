from __future__ import annotations

from api.server.page_strings import PageStrings


def Test_Values_TestMap_ExpectStringKeysAndValues() -> None:
   values = PageStrings.VALUES

   assert isinstance( values, dict )
   assert all(
      isinstance( key, str ) and isinstance( value, str )
      for key, value in values.items() )
