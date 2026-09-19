from __future__ import annotations

from datetime import date

from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.skater_season_key import SkaterSeasonKey
from api.team import Team


def Test_FromRow_TestStoredFields_ExpectValues() -> None:
   row = SkaterSeason.from_row( {
      'PLAYER_ID': 8478402,
      'SEASON_ID': 20252026,
      'PLAYER_NAME': 'Connor McDavid',
      'POSITION': 'C',
      'BIRTH_DATE': '1997-01-13',
      'AGE': 28.7,
      'TEAM': 'EDM',
      'GAMES_PLAYED': 82,
      'GOALS': 48,
      'ASSISTS': 90,
      'POINTS': 138,
      'SCHEDULE_GAMES': 82,
      'PACE_GAMES': 84,
      'G_PACE': 48.0,
      'A_PACE': 90.0,
      'P_PACE': 138.0,
      'GP_SHARE': 1.0,
   } )
   assert row.player_id == 8478402
   assert row.player_name == 'Connor McDavid'
   assert row.p_pace == 138.0


def Test_Key_TestPlayerAndSeason_ExpectKey() -> None:
   row = SkaterSeason(
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
      gp_share=1.0 )
   assert row.key() == SkaterSeasonKey( 8478402, 20252026 )
