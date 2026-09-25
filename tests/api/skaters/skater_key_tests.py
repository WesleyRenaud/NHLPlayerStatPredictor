from __future__ import annotations

from datetime import date

from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_key import SkaterKey
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_FromRow_TestPlayerAndName_ExpectFields() -> None:
   season = NhlSkaterSeason(
      player_id=8478402,
      season_id=20252026,
      player_name='Connor McDavid',
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

   key = SkaterKey.from_row( season )

   assert key == SkaterKey( season.player_id, season.player_name )


def Test_Equality_TestSamePlayerAndName_ExpectEqual() -> None:
   player_id = 8478402
   player_name = 'Connor McDavid'
   key = SkaterKey( player_id, player_name )
   duplicate = SkaterKey( player_id, player_name )

   equal = key == duplicate

   assert equal
   assert key in { duplicate }
