from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.aging.league_factor import LeagueFactor
from api.recency.pace_regression_fitter import PaceRegressionFitter
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.prior_source import PriorSource
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _nhl(
      player_id: int,
      start_year: int,
      g_pace: float,
      a_pace: float,
   age: float,
   power_play_goals: int = 0,
   power_play_points: int = 0,
   short_handed_goals: int = 0,
   short_handed_points: int = 0 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=start_year * 10000 + start_year + 1,
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
      power_play_goals=power_play_goals,
      power_play_points=power_play_points,
      short_handed_goals=short_handed_goals,
      short_handed_points=short_handed_points,
      penalty_minutes=0 )


def _other( player_id: int, start_year: int, g_pace: float, a_pace: float ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id,
      season_id=start_year * 10000 + start_year + 1,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=18.4,
      games_played=60,
      goals=0,
      assists=0,
      points=0,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Fit_TestMultiplicativePairs_ExpectAgeSpecificCoefficients() -> None:
   goal_multiplier = 2
   assist_multiplier = 3
   seasons: list[ NhlSkaterSeason ] = []

   for player_id in range( 1, 31 ):
      seasons.append( _nhl( player_id, 2020, float( player_id ), float( player_id ), 18.4, player_id, 2 * player_id, player_id, 2 * player_id ) )
      special_goals = goal_multiplier * player_id
      special_points = ( goal_multiplier + assist_multiplier ) * player_id
      seasons.append( _nhl(
         player_id, 2021, goal_multiplier * player_id, assist_multiplier * player_id, 19.4,
         special_goals, special_points, special_goals, special_points ) )

   model = PaceRegressionFitter.fit( seasons, [], [] )
   multipliers = {
      regression.stat: regression.coefficients[ Position.FIRST ].multiplier
      for regression in model.regressions
   }

   assert multipliers == pytest.approx( {
      'goals': goal_multiplier, 'assists': assist_multiplier,
      'power_play_goals': goal_multiplier, 'power_play_assists': assist_multiplier,
      'short_handed_goals': goal_multiplier, 'short_handed_assists': assist_multiplier
   } )
   assert all( regression.coefficients[ Position.FIRST ].weight == pytest.approx( 1.0 ) for regression in model.regressions )


def Test_Fit_TestAgePairAcrossYears_ExpectLongerLagRelationships() -> None:
   annual_multiplier = 2
   seasons = [
      _nhl( player_id, year, float( player_id * annual_multiplier ** ( year - 2020 ) ), float( player_id ), 18.4 + year - 2020 )
      for player_id in range( 1, 31 )
      for year in range( 2020, 2024 )
   ]

   model = PaceRegressionFitter.fit( seasons, [], [] )
   goals = next( regression for regression in model.regressions if regression.stat == 'goals' )
   pair = next( coefficient for coefficient in goals.coefficients if coefficient.from_age == 19 and coefficient.to_age == 21 )

   assert pair.multiplier == pytest.approx( annual_multiplier ** ( pair.to_age - pair.from_age ) )
   assert pair.weight == pytest.approx( 1.0 )


def Test_Fit_TestTranslatedPriors_ExpectTranslationAndNoMissingSpecialTeams() -> None:
   other_league_multiplier = 2.0
   league_factor = LeagueFactor( 'AAA', 0.5 )
   nhl = [ _nhl( player_id, 2021, float( player_id ), float( player_id ), 19.4 ) for player_id in range( 1, 31 ) ]
   other = [
      _other( player_id, 2020, other_league_multiplier * player_id, other_league_multiplier * player_id )
      for player_id in range( 1, 31 ) ]

   model = PaceRegressionFitter.fit( nhl, other, [ league_factor ] )

   assert { regression.stat for regression in model.regressions } == { 'goals', 'assists' }
   assert all( regression.source == PriorSource.TRANSLATED for regression in model.regressions )
   expected_multiplier = 1 / ( other_league_multiplier * league_factor.rate )
   assert all( regression.coefficients[ Position.FIRST ].multiplier == pytest.approx( expected_multiplier ) for regression in model.regressions )


def Test_Fit_TestSmallNhlStints_ExpectExcludedSpecialTeamsTraining() -> None:
   seasons: list[ NhlSkaterSeason ] = []
   others: list[ OtherLeagueSkaterSeason ] = []

   for player_id in range( 1, 31 ):
      seasons.append( replace( _nhl( player_id, 2020, 10.0, 10.0, 18.4, 2, 4 ), games_played=9 ) )
      seasons.append( _nhl( player_id, 2021, 20.0, 20.0, 19.4, 10, 20 ) )
      others.append( _other( player_id, 2020, 20.0, 20.0 ) )

   model = PaceRegressionFitter.fit( seasons, others, [ LeagueFactor( 'AAA', 0.5 ) ] )

   assert { regression.stat for regression in model.regressions } == { 'goals', 'assists' }


def Test_Fit_TestNoSamples_ExpectEmptyModel() -> None:
   assert PaceRegressionFitter.fit( [], [], [] ) == PaceRegressionModel( [] )
