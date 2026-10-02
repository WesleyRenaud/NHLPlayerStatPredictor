from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.aging.league_factor import LeagueFactor
from api.projections.baseline_pace_resolver import BaselinePaceResolver
from api.projections.scoring_component_shares import ScoringComponentShares
from api.projections.scoring_stat import ScoringStat
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
OTHER_LEAGUE_SHARES = ScoringComponentShares( 18, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 )


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
      even_strength_goals=round( g_pace ),
      even_strength_points=round( g_pace + a_pace ),
      goals=round( g_pace ),
      assists=round( a_pace ),
      points=round( g_pace + a_pace ),
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
      for stat in ScoringStat
   ], [ OTHER_LEAGUE_SHARES ] )


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
   translated_goals = season.g_pace * factor.rate
   assert resolved.power_play_goals == pytest.approx(
      translated_goals * OTHER_LEAGUE_SHARES.power_play_goals * SCORING_MULTIPLIER )
   assert resolved.short_handed_goals == pytest.approx(
      translated_goals * OTHER_LEAGUE_SHARES.short_handed_goals * SCORING_MULTIPLIER )
   assert resolved.penalty_minutes is None


def Test_Resolve_TestSmallNhlStint_ExpectObservedAndInferredComponents() -> None:
   factor = LeagueFactor( 'AAA', 0.4 )
   nhl = replace( _nhl( 20242025, 20.0, 30.0, 18.4 ), games_played=9, power_play_goals=2, power_play_points=4 )
   other = _other( 20242025, 30.0, 50.0, factor.league )

   resolved = BaselinePaceResolver.resolve( Skater( [ nhl, other ] ), 20252026, [ factor ], _model(), _pim_model() )

   assert resolved is not None
   assert resolved.goals > 0.0
   observed_pp_pace = nhl.power_play_goals * nhl.pace_games / nhl.games_played
   inferred_pp_pace = other.g_pace * factor.rate * OTHER_LEAGUE_SHARES.power_play_goals
   expected_pp = (
      observed_pp_pace * nhl.games_played + inferred_pp_pace * other.games_played
   ) / ( nhl.games_played + other.games_played ) * SCORING_MULTIPLIER
   assert resolved.power_play_goals == pytest.approx( expected_pp )
   assert resolved.penalty_minutes is None


def Test_Resolve_TestMissedSeason_ExpectElapsedAgeGrowth() -> None:
   season = _nhl( 20232024, 20.0, 30.0, 27.4 )

   resolved = BaselinePaceResolver.resolve( Skater( [ season ] ), 20252026, [], _model(), _pim_model() )

   assert resolved is not None
   elapsed_seasons = 2025 - 2023
   assert resolved.goals == pytest.approx( season.g_pace * SCORING_MULTIPLIER ** elapsed_seasons )


def Test_Resolve_TestLatestOtherLeague_ExpectMixedComponentsAndNhlOnlyPim() -> None:
   factor = LeagueFactor( 'AAA', 0.4 )
   nhl = replace( _nhl( 20222023, 20.0, 30.0, 16.4 ), penalty_minutes=20, power_play_goals=2, power_play_points=4 )
   other = _other( 20242025, 30.0, 50.0, factor.league )

   resolved = BaselinePaceResolver.resolve( Skater( [ nhl, other ] ), 20252026, [ factor ], _model(), _pim_model() )

   assert resolved is not None
   elapsed_nhl_seasons = 2025 - 2022
   pace_scale = nhl.pace_games / nhl.games_played
   inferred_pp_pace = other.g_pace * factor.rate * OTHER_LEAGUE_SHARES.power_play_goals
   # This fixture has no multi-year relationship weights, so scoring uses the latest season.
   expected_pp = inferred_pp_pace * SCORING_MULTIPLIER
   assert resolved.power_play_goals == pytest.approx( expected_pp )
   assert resolved.penalty_minutes == pytest.approx(
      nhl.penalty_minutes * pace_scale * PIM_MULTIPLIER ** elapsed_nhl_seasons )


def Test_Resolve_TestNoSeasons_ExpectNone() -> None:
   assert BaselinePaceResolver.resolve( Skater( [] ), 20252026, [], _model(), _pim_model() ) is None
