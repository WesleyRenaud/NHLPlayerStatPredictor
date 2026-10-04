from __future__ import annotations

from api.skaters.club_league import ClubLeague


def Test_Contains_TestListed_ExpectTrue() -> None:
   league = ClubLeague.OHL.value

   listed = ClubLeague.contains( league )

   assert listed


def Test_Contains_TestUnknown_ExpectFalse() -> None:
   unknown = ''

   listed = ClubLeague.contains( unknown )

   assert listed is False
