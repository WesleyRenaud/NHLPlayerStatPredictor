from __future__ import annotations

from api.team import Team


def Test_Members_TestValues_ExpectUniqueStrings() -> None:
   values = [ member.value for member in Team ]
   assert values
   assert len( values ) == len( set( values ) )

   for member in Team:
      assert isinstance( member.value, str )
      assert Team( member.value ) is member
