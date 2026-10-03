from __future__ import annotations

from dataclasses import replace
from datetime import date
from functools import partial
from unittest.mock import Mock

import pytest

from api.aging.league_factor import LeagueFactor
from api.projections.scoring_stat import ScoringStat
from api.recency.pace_regression_fitter import PaceRegressionFitter
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.prior_year_builder import PriorYearBuilder
from api.recency.production_coefficient_fitter import ProductionCoefficientFitter
from api.recency.production_history_predictor import ProductionHistoryPredictor
from api.recency.production_pair import ProductionPair
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


def Test_Fit_TestDifferentGoalAndAssistGrowth_ExpectOneTotalPointsMultiplier() -> None:
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
   expected_multiplier = ( goal_multiplier + assist_multiplier ) / 2
   assert len( model.scoring_growth ) == 1
   assert model.scoring_growth[ Position.FIRST ].multiplier == pytest.approx( expected_multiplier )
   assert model.history_weights[ Position.FIRST ].weight == 1.0


def Test_Fit_TestAgePairAcrossYears_ExpectAnnualGrowthAndLongerLagWeights() -> None:
   annual_multiplier = 2
   seasons = [
      _nhl( player_id, year, float( player_id * annual_multiplier ** ( year - 2020 ) ), float( player_id ), 18.4 + year - 2020 )
      for player_id in range( 1, 31 )
      for year in range( 2020, 2024 )
   ]

   model = PaceRegressionFitter.fit( seasons, [], [] )
   expected_multiplier = ( annual_multiplier ** 3 + 1 ) / ( annual_multiplier + 1 )
   assert all( coefficient.to_age == coefficient.from_age + 1 for coefficient in model.scoring_growth )
   multiplier = ProductionHistoryPredictor.multiplier(
      partial( ProductionHistoryPredictor.coefficient, model.scoring_growth ), 19, 21 )
   assert multiplier == pytest.approx( expected_multiplier )
   weight = next( weight for weight in model.history_weights
      if weight.from_age == 19 and weight.to_age == 21 )
   assert sum( item.weight for item in model.history_weights if item.to_age == 21 ) == pytest.approx( 1.0 )
   assert weight.weight > 0.0


def Test_Fit_TestTranslatedPriors_ExpectNormalizedPointsGrowthAndReliability() -> None:
   other_league_multiplier = 2.0
   league_factor = LeagueFactor( 'AAA', 0.5 )
   nhl = [ _nhl( player_id, 2021, float( player_id ), float( player_id ), 19.4 ) for player_id in range( 1, 31 ) ]
   other = [
      _other( player_id, 2020, other_league_multiplier * player_id, other_league_multiplier * player_id )
      for player_id in range( 1, 31 ) ]

   model = PaceRegressionFitter.fit( nhl, other, [ league_factor ] )

   expected_multiplier = 1 / ( other_league_multiplier * league_factor.rate )
   assert model.scoring_growth[ Position.FIRST ].multiplier == pytest.approx( expected_multiplier )
   assert model.history_weights[ Position.FIRST ].weight == pytest.approx( 1.0 )


def Test_Fit_TestSmallNhlStints_ExpectExcludedSpecialTeamsTraining() -> None:
   seasons: list[ NhlSkaterSeason ] = []
   others: list[ OtherLeagueSkaterSeason ] = []

   for player_id in range( 1, 31 ):
      seasons.append( replace( _nhl( player_id, 2020, 10.0, 10.0, 18.4, 2, 4 ), games_played=9 ) )
      seasons.append( _nhl( player_id, 2021, 20.0, 20.0, 19.4, 10, 20 ) )
      others.append( _other( player_id, 2020, 20.0, 20.0 ) )

   model = PaceRegressionFitter.fit( seasons, others, [ LeagueFactor( 'AAA', 0.5 ) ] )

   assert model.scoring_growth
   assert model.history_weights


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
      for player_id in range( 1, 31 )
      for year in range( 2020, 2024 )
   ]
   history = Mock( wraps=PriorYearBuilder.history )
   monkeypatch.setattr( PriorYearBuilder, 'history', history )

   model = PaceRegressionFitter.fit( seasons, [], [] )

   assert history.call_count == len( { season.player_id for season in seasons } )
   assert model.scoring_growth
   assert all(
      0 < coefficient.to_age - coefficient.from_age <= PriorYearBuilder.WIDTH
      for coefficient in model.scoring_growth )


def Test_Fit_TestTotalOnlyPriors_ExpectNormalizedPointsGrowthAndReliability() -> None:
   league_factor = LeagueFactor( 'AAA', 0.5 )
   nhl = [
      _nhl( player_id, 2021, 10.0 * player_id, 10.0 * player_id, 19.4, 2 * player_id, 4 * player_id )
      for player_id in range( 1, 31 ) ]
   other = [ _other( player_id, 2020, 20.0 * player_id, 20.0 * player_id ) for player_id in range( 1, 31 ) ]

   model = PaceRegressionFitter.fit( nhl, other, [ league_factor ] )
   assert model.scoring_growth[ Position.FIRST ].multiplier == pytest.approx( 1.0 )
   assert model.history_weights[ Position.FIRST ].weight == pytest.approx( 1.0 )
   assert model.history_weights[ Position.FIRST ].samples == len( other )


@pytest.mark.parametrize( 'translated', [ False, True ] )
def Test_Fit_TestDifferentComponentRelationships_ExpectPointsGrowthAndWeights(
      translated: bool ) -> None:
   player_ids = range( 1, 31 )
   previous = [
      _nhl( player_id, 2020, 3.0 * player_id, 2.0 * player_id, 18.4, player_id, 2 * player_id )
      for player_id in player_ids ]
   current = [
      _nhl( player_id, 2021, float( player_id + 30 ), float( 2 * player_id + 10 * ( player_id % 3 ) ),
         19.4, 31 - player_id, 31 - player_id )
      for player_id in player_ids ]
   factors = [ LeagueFactor( 'AAA', 0.5 ) ]
   other = [ _other( season.player_id, 2020, 2 * season.g_pace, 2 * season.a_pace ) for season in previous ]
   historical_seasons = other if translated else previous
   model = PaceRegressionFitter.fit( current if translated else previous + current,
      other if translated else [], factors )
   histories = [
      PriorYearBuilder.history( [ season ], factors, model.component_shares )[ Position.FIRST ]
      for season in historical_seasons ]
   points_pairs = [
      ProductionPair( int( prior.age ), int( prior.age ) + 1,
         prior.scoring.goals + prior.scoring.assists,
         following.scoring_paces().goals + following.scoring_paces().assists,
         min( prior.games, following.games_played ) )
      for prior, following in zip( histories, current ) ]
   points_coefficient = ProductionCoefficientFitter.fit( points_pairs )[ Position.FIRST ]
   points_weight = ProductionCoefficientFitter.fit_weights( points_pairs )[ Position.FIRST ].weight
   independent_weights = []

   assert model.history_weights[ Position.FIRST ].weight == points_weight
   assert model.scoring_growth[ Position.FIRST ].multiplier == pytest.approx( points_coefficient.multiplier )
   assert model.scoring_growth[ Position.FIRST ].samples == points_coefficient.samples

   for stat in ScoringStat:
      component_pairs = [
         replace( pair, prior_pace=getattr( prior.scoring, stat.value ),
            following_pace=getattr( following.scoring_paces(), stat.value ) )
         for pair, prior, following in zip( points_pairs, histories, current ) ]
      independent = ProductionCoefficientFitter.fit( component_pairs )
      independent_weights.append( [ coefficient.weight for coefficient in independent ] )

   assert points_weight == 1.0
   assert independent_weights == [
      [ 1.0 ], [ 1.0 ], [ 1.0 ], [] if translated else [ 0.0 ], [], [] ]


def Test_Fit_TestScoringComponents_ExpectOneGrowthFitPerProductionType(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   seasons = [
      _nhl( player_id, year, float( player_id ), float( 2 * player_id ), 18.4 + year - 2020 )
      for player_id in range( 1, 31 )
      for year in ( 2020, 2021 ) ]
   weight_fit = Mock( wraps=ProductionCoefficientFitter.fit_weights )
   growth_fit = Mock( wraps=ProductionCoefficientFitter.fit_growth )
   monkeypatch.setattr( ProductionCoefficientFitter, 'fit_weights', weight_fit )
   monkeypatch.setattr( ProductionCoefficientFitter, 'fit_growth', growth_fit )

   model = PaceRegressionFitter.fit( seasons, [], [] )

   assert weight_fit.call_count == 1
   assert growth_fit.call_count == 3
   assert all( 'weight' not in coefficient.to_dict()
      for coefficient in model.scoring_growth )


def Test_Fit_TestNhlAndTranslatedPairs_ExpectOnePooledScoringFit() -> None:
   nhl_multiplier = 2.0
   translated_multiplier = 3.0
   factor = LeagueFactor( 'AAA', 0.5 )
   previous = [ _nhl( player_id, 2020, float( player_id ), float( player_id ), 18.4 )
      for player_id in range( 1, 31 ) ]
   other = [ _other( season.player_id + len( previous ), 2020,
      season.g_pace / factor.rate, season.a_pace / factor.rate ) for season in previous ]
   current = [ _nhl( season.player_id, 2021,
      season.g_pace * nhl_multiplier, season.a_pace * nhl_multiplier, 19.4 ) for season in previous ]
   translated_current = [ _nhl( season.player_id, 2021,
      season.g_pace * factor.rate * translated_multiplier,
      season.a_pace * factor.rate * translated_multiplier, 19.4 ) for season in other ]

   model = PaceRegressionFitter.fit( previous + current + translated_current, other, [ factor ] )

   nhl_games = previous[ Position.FIRST ].games_played
   other_games = other[ Position.FIRST ].games_played
   expected_multiplier = (
      nhl_games * nhl_multiplier + other_games * translated_multiplier
   ) / ( nhl_games + other_games )
   assert len( model.scoring_growth ) == 1
   assert len( model.history_weights ) == 1
   assert model.scoring_growth[ Position.FIRST ].multiplier == pytest.approx( expected_multiplier )
   assert model.scoring_growth[ Position.FIRST ].samples == len( current ) + len( translated_current )
   assert model.history_weights[ Position.FIRST ].samples == len( current ) + len( translated_current )
