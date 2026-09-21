from __future__ import annotations

from pathlib import Path

from api.other_league_season_provider import OtherLeagueSeasonProvider
from api.other_league_season_store import OtherLeagueSeasonStore
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.shared.enums.position import Position


def _season( player_id: int, season_id: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      league='AAA',
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )


def Test_SeasonsForPlayerId_TestInsertedSeason_ExpectLookupById( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   row = _season( 7, 20252026 )
   OtherLeagueSeasonStore.insert_rows( [ row ], db_path=db_path )
   rows = OtherLeagueSeasonProvider.seasons_for_player_id( row.player_id, db_path )
   assert rows == [ row ]


def Test_SeasonsForSeasonId_TestMixedSeasons_ExpectMatchingYear( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   wanted = 20252026
   matching = _season( 1, wanted )
   other = _season( 2, 20242025 )
   OtherLeagueSeasonStore.insert_rows( [ matching, other ], db_path=db_path )
   rows = OtherLeagueSeasonProvider.seasons_for_season_id( wanted, db_path )
   assert rows == [ matching ]
   assert rows[ Position.FIRST ].season_id == wanted
