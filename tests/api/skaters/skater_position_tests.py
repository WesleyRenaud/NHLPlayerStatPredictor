from __future__ import annotations

from api.skaters.skater_position import SkaterPosition


def Test_Members_TestValues_ExpectUniqueStrings() -> None:
   values = [ member.value for member in SkaterPosition ]
   assert values
   assert len( values ) == len( set( values ) )

   for member in SkaterPosition:
      assert isinstance( member.value, str )
      assert SkaterPosition( member.value ) is member
