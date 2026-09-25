from __future__ import annotations

from api.shared.enums.position import Position
from api.skaters.club_league import ClubLeague


def Test_Members_TestValues_ExpectUniqueStrings() -> None:
   members = list( ClubLeague )

   values = [ member.value for member in members ]

   assert values
   assert len( values ) == len( set( values ) )
   assert all( isinstance( value, str ) for value in values )
   assert [ ClubLeague( value ) for value in values ] == members


def Test_Contains_TestListed_ExpectTrue() -> None:
   league = list( ClubLeague )[ Position.FIRST ].value

   listed = ClubLeague.contains( league )

   assert listed


def Test_Contains_TestUnknown_ExpectFalse() -> None:
   unknown = ''

   listed = ClubLeague.contains( unknown )

   assert listed is False
