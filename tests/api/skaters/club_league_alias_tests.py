from __future__ import annotations

import pytest

from api.skaters.club_league import ClubLeague
from api.skaters.club_league_alias import ClubLeagueAlias


@pytest.fixture
def aliases( monkeypatch: pytest.MonkeyPatch ) -> dict[ ClubLeague, list[ str ] ]:
   labels = {
      ClubLeague.OHL: [ 'Test league alpha', 'Test league beta' ],
      ClubLeague.WHL: [ 'Test league gamma' ],
   }
   monkeypatch.setattr( ClubLeagueAlias, 'LABELS', labels )
   return labels


def Test_League_TestCanonical_ExpectSameLeague( aliases: dict[ ClubLeague, list[ str ] ] ) -> None:
   league = next( iter( aliases ) )

   resolved = ClubLeagueAlias.league( league.value )

   assert resolved == league


def Test_League_TestAlias_ExpectCanonicalLeague( aliases: dict[ ClubLeague, list[ str ] ] ) -> None:
   for league, labels in aliases.items():
      resolved = [ ClubLeagueAlias.league( label ) for label in labels ]

      assert resolved == [ league ] * len( labels )


def Test_League_TestUnknown_ExpectNone( aliases: dict[ ClubLeague, list[ str ] ] ) -> None:
   resolved = ClubLeagueAlias.league( 'Unlisted test league' )

   assert resolved is None


def Test_League_TestEmptyAliases_ExpectCanonicalStillResolves( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( ClubLeagueAlias, 'LABELS', {} )
   league = ClubLeague.OHL

   resolved = ClubLeagueAlias.league( league.value )

   assert resolved is league


def Test_Rank_TestCanonical_ExpectZero( aliases: dict[ ClubLeague, list[ str ] ] ) -> None:
   league = next( iter( aliases ) )

   rank = ClubLeagueAlias.rank( league.value )

   assert rank == 0


def Test_Rank_TestAliases_ExpectListedOrderAfterCanonical( aliases: dict[ ClubLeague, list[ str ] ] ) -> None:
   for labels in aliases.values():
      ranks = [ ClubLeagueAlias.rank( label ) for label in labels ]

      assert ranks == list( range( 1, len( labels ) + 1 ) )


def Test_Rank_TestUnknown_ExpectZero( aliases: dict[ ClubLeague, list[ str ] ] ) -> None:
   rank = ClubLeagueAlias.rank( 'Unlisted test league' )

   assert rank == 0
