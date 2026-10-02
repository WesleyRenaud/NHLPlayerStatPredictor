from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.aging.league_factor import LeagueFactor
from api.projections.baseline_pace_resolver import BaselinePaceResolver
from api.recency.pace_regression import PaceRegression
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pim_regression_model import PimRegressionModel
from api.recency.prior_source import PriorSource
from api.recency.production_coefficient import ProductionCoefficient
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater import Skater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


SCORING_MULTIPLIER = 1.2
PIM_MULTIPLIER = 1.1


def _nhl( season_id: int, g_pace: float, a_pace: float, age: float ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=age,
      team=list( Team )[ Position.FIRST ],
      games_played=82,
      goals=0,
      assists=0,
      points=0,
      schedule_games=82,
      pace_games=82,
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      penalty_minutes=0 )


def _other( season_id: int, g_pace: float, a_pace: float, league: str ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1,
      season_id=season_id,
      league=league,
      position=SkaterPosition( 'C' ),
      age=18.4,
      games_played=52,
      goals=0,
      assists=0,
      points=0,
      g_pace=g_pace,
      a_pace=a_pace )


def _model() -> PaceRegressionModel:
   return PaceRegressionModel( [
      PaceRegression( source, stat, [
         ProductionCoefficient( age, age + 1, SCORING_MULTIPLIER, 0.8, 100 )
         for age in range( 17, 40 )
      ] )
      for source in PriorSource
      for stat in ( 'goals', 'assists', 'power_play_goals', 'power_play_assists', 'short_handed_goals', 'short_handed_assists' )
   ] )


def _pim_model() -> PimRegressionModel:
   return PimRegressionModel( [
      ProductionCoefficient( age, age + 1, PIM_MULTIPLIER, 0.8, 100 ) for age in range( 17, 40 )
   ] )


def Test_Resolve_TestNhlSeason_ExpectMultiplicativePace() -> None:
   season = replace( _nhl( 20242025, 20.0, 30.0, 27.4 ), penalty_minutes=20 )

   resolved = BaselinePaceResolver.resolve( Skater( [ season ] ), 20252026, [], _model(), _pim_model() )

   assert resolved is not None
   assert resolved.goals == pytest.approx( season.g_pace * SCORING_MULTIPLIER )
   assert resolved.assists == pytest.approx( season.a_pace * SCORING_MULTIPLIER )
   assert resolved.penalty_minutes == pytest.approx(
      season.penalty_minutes * season.pace_games / season.games_played * PIM_MULTIPLIER )


def Test_Resolve_TestPlayoffSurplus_ExpectRegularSeasonWorkflow() -> None:
   regular = _nhl( 20242025, 20.0, 30.0, 27.4 )
   playoffs = replace( regular, playoff_games=10, playoff_goals=5, playoff_assists=3 )

   without = BaselinePaceResolver.resolve( Skater( [ regular ] ), 20252026, [], _model(), _pim_model() )
   resolved = BaselinePaceResolver.resolve( Skater( [ playoffs ] ), 20252026, [], _model(), _pim_model() )

   assert resolved == without


def Test_Resolve_TestOtherLeagueOnly_ExpectTranslatedMultiplicativePace() -> None:
   factor = LeagueFactor( 'AAA', 0.4 )
   season = _other( 20242025, 30.0, 50.0, factor.league )

   resolved = BaselinePaceResolver.resolve( Skater( [ season ] ), 20252026, [ factor ], _model(), _pim_model() )

   assert resolved is not None
   assert resolved.goals == pytest.approx( season.g_pace * factor.rate * SCORING_MULTIPLIER )
   assert resolved.assists == pytest.approx( season.a_pace * factor.rate * SCORING_MULTIPLIER )
   assert resolved.power_play_goals == 0.0
   assert resolved.short_handed_goals == 0.0
   assert resolved.penalty_minutes is None


def Test_Resolve_TestSmallNhlStint_ExpectNoUnsupportedSpecialTeamsProjection() -> None:
   factor = LeagueFactor( 'AAA', 0.4 )
   nhl = replace( _nhl( 20242025, 20.0, 30.0, 18.4 ), games_played=9, power_play_goals=2, power_play_points=4 )
   other = _other( 20242025, 30.0, 50.0, factor.league )

   resolved = BaselinePaceResolver.resolve( Skater( [ nhl, other ] ), 20252026, [ factor ], _model(), _pim_model() )

   assert resolved is not None
   assert resolved.goals > 0.0
   assert resolved.power_play_goals == 0.0
   assert resolved.penalty_minutes is None


def Test_Resolve_TestMissedSeason_ExpectElapsedAgeGrowth() -> None:
   season = _nhl( 20232024, 20.0, 30.0, 27.4 )

   resolved = BaselinePaceResolver.resolve( Skater( [ season ] ), 20252026, [], _model(), _pim_model() )

   assert resolved is not None
   elapsed_seasons = 2025 - 2023
   assert resolved.goals == pytest.approx( season.g_pace * SCORING_MULTIPLIER ** elapsed_seasons )


def Test_Resolve_TestSpecialTeamsExceedTotal_ExpectUnalteredCalculation() -> None:
   season = replace(
      _nhl( 20242025, 2.0, 3.0, 27.4 ),
      power_play_goals=3, power_play_points=7, short_handed_goals=1, short_handed_points=2 )

   resolved = BaselinePaceResolver.resolve( Skater( [ season ] ), 20252026, [], _model(), _pim_model() )

   assert resolved is not None
   special_teams_scale = season.pace_games / season.games_played * SCORING_MULTIPLIER
   power_play_assists = season.power_play_points - season.power_play_goals
   short_handed_assists = season.short_handed_points - season.short_handed_goals
   assert resolved.goals == pytest.approx( season.g_pace * SCORING_MULTIPLIER )
   assert resolved.power_play_goals == pytest.approx( season.power_play_goals * special_teams_scale )
   assert resolved.short_handed_goals == pytest.approx( season.short_handed_goals * special_teams_scale )
   assert resolved.power_play_assists == pytest.approx( power_play_assists * special_teams_scale )
   assert resolved.short_handed_assists == pytest.approx( short_handed_assists * special_teams_scale )
   assert resolved.power_play_goals / resolved.short_handed_goals == pytest.approx(
      season.power_play_goals / season.short_handed_goals )


def Test_Resolve_TestLatestOtherLeague_ExpectIndependentNhlSpecialTeamsAndPim() -> None:
   factor = LeagueFactor( 'AAA', 0.4 )
   nhl = replace( _nhl( 20222023, 20.0, 30.0, 16.4 ), penalty_minutes=20, power_play_goals=2, power_play_points=4 )
   other = _other( 20242025, 30.0, 50.0, factor.league )

   resolved = BaselinePaceResolver.resolve( Skater( [ nhl, other ] ), 20252026, [ factor ], _model(), _pim_model() )

   assert resolved is not None
   elapsed_nhl_seasons = 2025 - 2022
   pace_scale = nhl.pace_games / nhl.games_played
   assert resolved.power_play_goals == pytest.approx(
      nhl.power_play_goals * pace_scale * SCORING_MULTIPLIER ** elapsed_nhl_seasons )
   assert resolved.penalty_minutes == pytest.approx(
      nhl.penalty_minutes * pace_scale * PIM_MULTIPLIER ** elapsed_nhl_seasons )


def Test_Resolve_TestNoSeasons_ExpectNone() -> None:
   assert BaselinePaceResolver.resolve( Skater( [] ), 20252026, [], _model(), _pim_model() ) is None
