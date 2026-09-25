from __future__ import annotations

from api.skaters.skater_position import SkaterPosition


def Test_Members_TestValues_ExpectUniqueStrings() -> None:
   members = list( SkaterPosition )

   values = [ member.value for member in members ]

   assert values
   assert len( values ) == len( set( values ) )
   assert all( isinstance( value, str ) for value in values )
   assert [ SkaterPosition( value ) for value in values ] == members
