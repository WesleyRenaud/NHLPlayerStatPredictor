from __future__ import annotations

from pathlib import Path

from api.other_league_season import OtherLeagueSeason
from api.other_league_season_provider import OtherLeagueSeasonProvider
from api.other_league_season_store import OtherLeagueSeasonStore
from api.shared.enums.position import Position


def Test_InsertRows_TestInsertedSeason_ExpectReadableByPlayer( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   row = OtherLeagueSeason(
      player_id=7,
      season_id=20252026,
      league='AAA',
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )
   OtherLeagueSeasonStore.insert_rows( [ row ], db_path=db_path )
   rows = OtherLeagueSeasonProvider.seasons_for_player_id( row.player_id, db_path )
   assert len( rows ) == 1
   assert rows[ Position.FIRST ] == row
