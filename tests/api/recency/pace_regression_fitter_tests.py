from __future__ import annotations

from dataclasses import replace
from datetime import date
from unittest.mock import Mock

import pytest

from api.aging.league_factor import LeagueFactor
from api.projections.scoring_stat import ScoringStat
from api.recency.pace_regression_fitter import PaceRegressionFitter
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.prior_source import PriorSource
from api.recency.prior_year_builder import PriorYearBuilder
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
      even_strength_goals=round( g_pace ) - power_play_goals - short_handed_goals,
      even_strength_points=round( g_pace + a_pace ) - power_play_points - short_handed_points,
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
      power_play_goals=power_play_goals,
      power_play_points=power_play_points,
      short_handed_goals=short_handed_goals,
      short_handed_points=short_handed_points,
      shots=0,
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
      seasons.append( _nhl( player_id, 2020, 3.0 * player_id, 3.0 * player_id, 18.4, player_id, 2 * player_id, player_id, 2 * player_id ) )
      special_goals = goal_multiplier * player_id
      special_points = ( goal_multiplier + assist_multiplier ) * player_id
      seasons.append( _nhl(
         player_id, 2021, 3 * goal_multiplier * player_id, 3 * assist_multiplier * player_id, 19.4,
         special_goals, special_points, special_goals, special_points ) )

   model = PaceRegressionFitter.fit( seasons, [], [] )
   multipliers = {
      regression.stat: regression.coefficients[ Position.FIRST ].multiplier
      for regression in model.regressions
   }

   assert multipliers == pytest.approx( {
      'even_strength_goals': goal_multiplier, 'even_strength_assists': assist_multiplier,
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
   goals = next( regression for regression in model.regressions if regression.stat == ScoringStat.EVEN_STRENGTH_GOALS )
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

   assert { regression.stat for regression in model.regressions } == set( ScoringStat )
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

   assert { regression.stat for regression in model.regressions } == set( ScoringStat )


def Test_Fit_TestNoSamples_ExpectEmptyModel() -> None:
   assert PaceRegressionFitter.fit( [], [], [] ) == PaceRegressionModel( [] )


def Test_Fit_TestNhlProduction_ExpectSeparatePimAndShotsCoefficients() -> None:
   pim_multiplier = 2
   shots_multiplier = 3
   seasons = [
      replace(
         _nhl( player_id, year, 10.0, 20.0, 18.4 + year - 2020 ),
         penalty_minutes=player_id * pim_multiplier ** ( year - 2020 ),
         shots=player_id * shots_multiplier ** ( year - 2020 ) )
      for player_id in range( 1, 31 )
      for year in range( 2020, 2023 )
   ]

   model = PaceRegressionFitter.fit( seasons, [], [] )

   for coefficient in model.pim_coefficients:
      assert coefficient.multiplier == pytest.approx(
         pim_multiplier ** ( coefficient.to_age - coefficient.from_age ) )
   for coefficient in model.shots_coefficients:
      assert coefficient.multiplier == pytest.approx(
         shots_multiplier ** ( coefficient.to_age - coefficient.from_age ) )
   assert model.pim_coefficients
   assert model.shots_coefficients


def Test_Fit_TestMultipleYears_ExpectOneHistoryPreparationPerPlayer(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   seasons = [
      _nhl( player_id, year, 10.0, 20.0, 18.4 + year - 2020 )
      for player_id in range( 1, 3 )
      for year in range( 2020, 2024 )
   ]
   history = Mock( wraps=PriorYearBuilder.history )
   monkeypatch.setattr( PriorYearBuilder, 'history', history )

   model = PaceRegressionFitter.fit( seasons, [], [] )

   assert history.call_count == len( { season.player_id for season in seasons } )
   assert model.regressions
   assert all(
      0 < coefficient.to_age - coefficient.from_age <= PriorYearBuilder.WIDTH
      for regression in model.regressions
      for coefficient in regression.coefficients )


def Test_Fit_TestTotalOnlyPriors_ExpectInferredPowerPlayTraining() -> None:
   league_factor = LeagueFactor( 'AAA', 0.5 )
   nhl = [
      _nhl( player_id, 2021, 10.0 * player_id, 10.0 * player_id, 19.4, 2 * player_id, 4 * player_id )
      for player_id in range( 1, 31 ) ]
   other = [ _other( player_id, 2020, 20.0 * player_id, 20.0 * player_id ) for player_id in range( 1, 31 ) ]

   model = PaceRegressionFitter.fit( nhl, other, [ league_factor ] )
   power_play = next( regression for regression in model.regressions if regression.stat == ScoringStat.POWER_PLAY_GOALS )
   coefficient = power_play.coefficients[ Position.FIRST ]

   assert power_play.source == PriorSource.TRANSLATED
   assert coefficient.multiplier == pytest.approx( 1.0 )
   assert coefficient.weight == pytest.approx( 1.0 )
   assert coefficient.samples == len( other )
