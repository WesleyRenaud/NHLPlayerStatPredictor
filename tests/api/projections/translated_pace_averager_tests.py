from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.aging.league_factor import LeagueFactor
from api.projections.power_play_pace import PowerPlayPace
from api.projections.season_pace import SeasonPace
from api.projections.translated_pace_averager import TranslatedPaceAverager
from api.season import Season
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _nhl(
      g_pace: float,
      a_pace: float,
      season_id: int,
   games_played: int = 82,
   power_play_goals: int = 0,
   power_play_points: int = 0,
   short_handed_goals: int = 0,
   short_handed_points: int = 0 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=games_played,
      goals=int( g_pace ),
      assists=int( a_pace ),
      points=int( g_pace + a_pace ),
      schedule_games=82,
      pace_games=82,
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=power_play_goals,
      power_play_points=power_play_points,
      short_handed_goals=short_handed_goals,
      short_handed_points=short_handed_points,
      penalty_minutes=0 )


def _other(
      g_pace: float,
      a_pace: float,
      season_id: int,
      league: str,
      games_played: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1,
      season_id=season_id,
      league=league,
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=games_played,
      goals=1,
      assists=1,
      points=2,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Year_TestMixedNhlAndOther_ExpectGamesWeightedBlend() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   nhl_games = 1
   other_games = 46
   nhl = replace( _nhl( 84.0, 84.0, 20252026, nhl_games ), penalty_minutes=2 )
   other = _other( 10.96, 23.74, 20252026, league, other_games )
   total_games = nhl_games + other_games

   year = TranslatedPaceAverager.year( [ nhl, other ], [ factor ] )

   assert year.games == total_games
   assert year.goals == pytest.approx(
      ( nhl_games * nhl.g_pace + other_games * other.g_pace * factor.rate )
      / total_games )
   assert year.assists == pytest.approx(
      ( nhl_games * nhl.a_pace + other_games * other.a_pace * factor.rate )
      / total_games )
   assert year.power_play_goals == 0.0
   assert year.power_play_assists == 0.0
   assert year.penalty_minutes == pytest.approx( nhl.penalty_minutes_pace() )


def Test_Year_TestOtherLeagueOnly_ExpectMissingPim() -> None:
   factor = LeagueFactor( 'AAA', 0.40 )
   other = _other( 10.96, 23.74, 20252026, factor.league, 46 )

   year = TranslatedPaceAverager.year( [ other ], [ factor ] )

   assert year is not None
   assert year.penalty_minutes is None


def Test_Year_TestNhlPowerPlayTotals_ExpectSeparatePowerPlayPace() -> None:
   games_played = 10
   power_play_goals = 4
   power_play_points = 10
   nhl = _nhl(
      20.0,
      30.0,
      20252026,
      games_played,
      power_play_goals=power_play_goals,
      power_play_points=power_play_points )
   expected_power_play_goals = Season.pace(
      float( power_play_goals ),
      float( games_played ),
      nhl.pace_games )
   expected_power_play_assists = Season.pace(
      float( power_play_points - power_play_goals ),
      float( games_played ),
      nhl.pace_games )

   year = TranslatedPaceAverager.year( [ nhl ], [] )

   assert year.power_play_goals == pytest.approx( expected_power_play_goals )
   assert year.power_play_assists == pytest.approx( expected_power_play_assists )


def Test_Year_TestNhlShortHandedTotals_ExpectSeparateShortHandedPace() -> None:
   games_played = 10
   short_handed_goals = 2
   short_handed_points = 3
   nhl = _nhl(
      20.0,
      30.0,
      20252026,
      games_played,
      short_handed_goals=short_handed_goals,
      short_handed_points=short_handed_points )
   expected_goals = Season.pace(
      float( short_handed_goals ), float( games_played ), nhl.pace_games )
   expected_assists = Season.pace(
      float( short_handed_points - short_handed_goals ),
      float( games_played ),
      nhl.pace_games )

   year = TranslatedPaceAverager.year( [ nhl ], [] )

   assert year.short_handed_goals == pytest.approx( expected_goals )
   assert year.short_handed_assists == pytest.approx( expected_assists )


def Test_Year_TestNoGames_ExpectNone() -> None:
   year = TranslatedPaceAverager.year( [], [] )

   assert year is None


def Test_Year_TestMissingLeague_ExpectNhlOnly() -> None:
   nhl = _nhl( 20.0, 30.0, 20252026, 10 )
   other = _other( 100.0, 100.0, 20252026, 'AAA', 50 )

   year = TranslatedPaceAverager.year( [ nhl, other ], [] )

   assert year.games == nhl.games_played
   assert year.goals == nhl.g_pace
   assert year.assists == nhl.a_pace
