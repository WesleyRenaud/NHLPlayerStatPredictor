from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.draft_class import DraftClass
from api.season import Season
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season import SkaterSeason
from api.skaters.skater_season_key import SkaterSeasonKey
from api.skaters.team import Team


def _season( games_played: int, goals: int, assists: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=7,
      season_id=20252026,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=games_played,
      even_strength_goals=goals,
      even_strength_points=( goals + assists ),
      goals=goals,
      assists=assists,
      points=goals + assists,
      schedule_games=82,
      pace_games=82,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      shots=200,
      penalty_minutes=0,
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0 )


def Test_FromRow_TestStoredFields_ExpectValues() -> None:
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   season_id = 20252026
   birth_date = date( 1997, 1, 13 )
   season = NhlSkaterSeason(
      player_id=8478402,
      season_id=season_id,
      player_name='Connor McDavid',
      position=position,
      birth_date=birth_date,
      age=DraftClass.age( birth_date, season_id ),
      team=team,
      games_played=82,
      even_strength_goals=48 - 20 - 3,
      even_strength_points=138 - 35 - 5,
      goals=48,
      assists=90,
      points=138,
      schedule_games=82,
      pace_games=84,
      g_pace=48.0,
      a_pace=90.0,
      p_pace=138.0,
      shots=0,
      penalty_minutes=54,
      gp_share=1.0,
      playoff_games=18,
      playoff_goals=7,
      playoff_assists=26,
      power_play_goals=20,
      power_play_points=35,
      short_handed_goals=3,
      short_handed_points=5 )

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
      'SHOTS': season.shots,
      'PIM': season.penalty_minutes,
      'SCHEDULE_GAMES': season.schedule_games,
      'PACE_GAMES': season.pace_games,
      'G_PACE': season.g_pace,
      'A_PACE': season.a_pace,
      'P_PACE': season.p_pace,
      'GP_SHARE': season.gp_share,
      'PLAYOFF_GAMES': season.playoff_games,
      'PLAYOFF_GOALS': season.playoff_goals,
      'PLAYOFF_ASSISTS': season.playoff_assists,
      'PP_GOALS': season.power_play_goals,
      'PP_POINTS': season.power_play_points,
      'SHORT_HANDED_GOALS': season.short_handed_goals,
      'SHORT_HANDED_POINTS': season.short_handed_points,
      'EV_GOALS': season.even_strength_goals,
      'EV_POINTS': season.even_strength_points,
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
      even_strength_goals=48,
      even_strength_points=138,
      goals=48,
      assists=90,
      points=138,
      schedule_games=82,
      pace_games=84,
      g_pace=48.0,
      a_pace=90.0,
      p_pace=138.0,
      shots=0,
      penalty_minutes=54,
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0 )

   key = season.key()

   assert key == SkaterSeasonKey( season.player_id, season.season_id )


def Test_EvenStrengthPace_TestExplicitCounts_ExpectPacedSourceValues() -> None:
   season = replace( _season( 60, 12, 18 ), even_strength_goals=8, even_strength_points=20 )

   pace = season.even_strength_pace()

   assert pace.goals == pytest.approx(
      Season.pace( season.even_strength_goals, season.games_played, season.pace_games ) )
   assert pace.assists == pytest.approx(
      Season.pace( season.even_strength_points - season.even_strength_goals, season.games_played, season.pace_games ) )


def Test_PlayoffSurplus_TestAboveRegularRate_ExpectExtraScoring() -> None:
   season = replace( _season( 60, 12, 18 ), playoff_games=20, playoff_goals=10, playoff_assists=9 )
   share = season.playoff_games / season.games_played

   surplus = season.playoff_surplus()

   assert surplus.goals == pytest.approx( season.playoff_goals - share * season.goals )
   assert surplus.assists == pytest.approx( season.playoff_assists - share * season.assists )


def Test_PlayoffSurplus_TestBelowRegularRate_ExpectNoSurplus() -> None:
   season = replace( _season( 80, 40, 40 ), playoff_games=10, playoff_goals=1, playoff_assists=2 )

   surplus = season.playoff_surplus()

   assert surplus.goals == 0.0
   assert surplus.assists == 0.0


def Test_PlayoffSurplus_TestNoPlayoffs_ExpectNoSurplus() -> None:
   surplus = _season( 80, 40, 40 ).playoff_surplus()

   assert surplus.goals == 0.0
   assert surplus.assists == 0.0
