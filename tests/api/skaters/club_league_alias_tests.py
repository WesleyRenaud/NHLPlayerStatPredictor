from __future__ import annotations

from api.shared.enums.position import Position
from api.skaters.club_league import ClubLeague
from api.skaters.club_league_alias import ClubLeagueAlias


def _aliased() -> tuple[ ClubLeague, list[ str ] ]:
   return list( ClubLeagueAlias.LABELS.items() )[ Position.FIRST ]


def Test_Labels_TestAllAliases_ExpectNotCanonicalAndUnique() -> None:
   labels = [ label for aliases in ClubLeagueAlias.LABELS.values() for label in aliases ]

   assert len( labels ) == len( set( labels ) )
   assert not any( ClubLeague.contains( label ) for label in labels )


def Test_League_TestCanonical_ExpectSameLeague() -> None:
   league = list( ClubLeague )[ Position.FIRST ]

   resolved = ClubLeagueAlias.league( league.value )

   assert resolved == league


def Test_League_TestAlias_ExpectCanonicalLeague() -> None:
   league, labels = _aliased()

   resolved = [ ClubLeagueAlias.league( label ) for label in labels ]

   assert resolved == [ league ] * len( labels )


def Test_League_TestUnknown_ExpectNone() -> None:
   resolved = ClubLeagueAlias.league( '' )

   assert resolved is None


def Test_Rank_TestCanonical_ExpectZero() -> None:
   league, _ = _aliased()

   rank = ClubLeagueAlias.rank( league.value )

   assert rank == 0


def Test_Rank_TestAliases_ExpectListedOrderAfterCanonical() -> None:
   _, labels = _aliased()

   ranks = [ ClubLeagueAlias.rank( label ) for label in labels ]

   assert ranks == list( range( 1, len( labels ) + 1 ) )
