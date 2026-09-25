from __future__ import annotations

from datetime import date
from pathlib import Path

from api.season import Season
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season_finder import SkaterSeasonFinder
from api.skaters.skater_season_provider import SkaterSeasonProvider
from api.skaters.skater_season_store import SkaterSeasonStore
from api.skaters.team import Team


def Test_FormatTable_TestOneSeason_ExpectPaceColumns( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   season = NhlSkaterSeason(
      player_id=8478402,
      season_id=20252026,
      player_name='Connor McDavid',
      position=position,
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=team,
      games_played=82,
      goals=48,
      assists=90,
      points=138,
      schedule_games=82,
      pace_games=84,
      g_pace=49.170731707317074,
      a_pace=92.1951219512195,
      p_pace=141.3658536585366,
      gp_share=1.0 )
   SkaterSeasonStore.insert_rows( [ season ], db_path=db_path )
   rows = SkaterSeasonProvider.seasons_for_name( season.player_name, db_path=db_path )

   table = SkaterSeasonFinder.format_table( rows )

   assert f'{ season.player_name } ({ season.position.value }, #{ season.player_id })' in table
   assert Season.label( season.season_id ) in table
   assert season.team.value in table
   assert f'G/{ season.pace_games }' in table
   assert SkaterSeasonFinder._fmt_pace( season.p_pace ) in table
