from __future__ import annotations

from datetime import date

from api.skater_key import SkaterKey
from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.team import Team


def Test_FromRow_TestPlayerAndName_ExpectFields() -> None:
   key = SkaterKey.from_row( SkaterSeason(
      player_id=8478402,
      season_id=20252026,
      player_name='Connor McDavid',
      position=SkaterPosition.CENTER,
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=Team.EDMONTON_OILERS,
      games_played=82,
      goals=48,
      assists=90,
      points=138,
      schedule_games=82,
      pace_games=84,
      g_pace=48.0,
      a_pace=90.0,
      p_pace=138.0,
      gp_share=1.0 ) )
   assert key.player_id == 8478402
   assert key.player_name == 'Connor McDavid'


def Test_Equality_TestSamePlayerAndName_ExpectEqual() -> None:
   key = SkaterKey( 8478402, 'Connor McDavid' )
   assert key == SkaterKey( 8478402, 'Connor McDavid' )
   assert key in { SkaterKey( 8478402, 'Connor McDavid' ) }
