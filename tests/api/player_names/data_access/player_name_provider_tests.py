from __future__ import annotations

from datetime import date
from pathlib import Path

from api.player_names.data_access.player_name_provider import PlayerNameProvider
from api.position import Position
from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.skater_season_store import SkaterSeasonStore
from api.team import Team


def _season( player_id: int, season_id: int, player_name: str ) -> SkaterSeason:
   return SkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name=player_name,
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=82,
      goals=48,
      assists=90,
      points=138,
      schedule_games=82,
      pace_games=84,
      g_pace=48.0,
      a_pace=90.0,
      p_pace=138.0,
      gp_share=1.0 )


def Test_Names_TestMissingTable_ExpectEmptyList( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   assert PlayerNameProvider.names( db_path ) == []


def Test_Names_TestDuplicateSeasons_ExpectDistinctSortedNames( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   first_name = 'Alpha Skater'
   second_name = 'Beta Skater'
   SkaterSeasonStore.insert_rows(
      [
         _season( 1, 20242025, second_name ),
         _season( 1, 20252026, second_name ),
         _season( 2, 20252026, first_name ),
      ],
      db_path=db_path )
   assert PlayerNameProvider.names( db_path ) == [ first_name, second_name ]
