from __future__ import annotations

from datetime import date

from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season import SkaterSeason
from api.skaters.skater_season_key import SkaterSeasonKey
from api.skaters.team import Team


def Test_FromRow_TestStoredFields_ExpectValues() -> None:
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
      g_pace=48.0,
      a_pace=90.0,
      p_pace=138.0,
      gp_share=1.0 )

   loaded = NhlSkaterSeason.from_row( {
      'PLAYER_ID': season.player_id,
      'SEASON_ID': season.season_id,
      'PLAYER_NAME': season.player_name,
      'POSITION': season.position.value,
      'BIRTH_DATE': season.birth_date.isoformat(),
      'AGE': season.age,
      'TEAM': season.team.value,
      'GAMES_PLAYED': season.games_played,
      'GOALS': season.goals,
      'ASSISTS': season.assists,
      'POINTS': season.points,
      'SCHEDULE_GAMES': season.schedule_games,
      'PACE_GAMES': season.pace_games,
      'G_PACE': season.g_pace,
      'A_PACE': season.a_pace,
      'P_PACE': season.p_pace,
      'GP_SHARE': season.gp_share,
   } )

   assert loaded == season
   assert isinstance( loaded, SkaterSeason )


def Test_Key_TestPlayerAndSeason_ExpectKey() -> None:
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

   key = season.key()

   assert key == SkaterSeasonKey( season.player_id, season.season_id )
