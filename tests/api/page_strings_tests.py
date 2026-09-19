from __future__ import annotations

from api.page_strings import PageStrings


def Test_Values_TestMap_ExpectStringKeysAndValues() -> None:
   assert isinstance( PageStrings.VALUES, dict )

   for key, value in PageStrings.VALUES.items():
      assert isinstance( key, str )
      assert isinstance( value, str )
