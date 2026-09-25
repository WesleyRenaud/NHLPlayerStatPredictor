from __future__ import annotations

from api.shared.enums.position import Position
from api.skaters.club_league import ClubLeague


def Test_Members_TestValues_ExpectUniqueStrings() -> None:
   values = [ member.value for member in ClubLeague ]
   assert values
   assert len( values ) == len( set( values ) )

   for member in ClubLeague:
      assert isinstance( member.value, str )
      assert ClubLeague( member.value ) is member


def Test_Contains_TestListed_ExpectTrue() -> None:
   league = list( ClubLeague )[ Position.FIRST ].value
   assert ClubLeague.contains( league )


def Test_Contains_TestUnknown_ExpectFalse() -> None:
   assert ClubLeague.contains( '' ) is False
