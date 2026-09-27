from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.aging.league_factor import LeagueFactor
from api.recency.age_band import AgeBand
from api.recency.pace_regression_fitter import PaceRegressionFitter
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pace_regression_predictor import PaceRegressionPredictor
from api.recency.prior_source import PriorSource
from api.recency.prior_year_builder import PriorYearBuilder
from api.season import Season
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
      age: float ) -> NhlSkaterSeason:
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
      playoff_assists=0 )


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


_PLAYERS = 60


def _goals( player_id: int ) -> float:
   return float( player_id % 30 )


def _assists( player_id: int ) -> float:
   return float( ( player_id * 7 ) % 40 )


def _pairs( count: int, gap: int = 0, scale: float = 1.0, first_id: int = 0 ) -> list[ NhlSkaterSeason ]:
   seasons: list[ NhlSkaterSeason ] = []

   for player_id in range( first_id, first_id + count ):
      goals = _goals( player_id )
      assists = _assists( player_id )
      seasons.append( _nhl( player_id, 2020, goals, assists, 25.4 ) )
      seasons.append(
         _nhl(
            player_id,
            2021 + gap,
            scale * ( 2.0 + 0.5 * goals ),
            scale * ( 1.0 + 0.25 * assists ),
            26.4 + gap ) )

   return seasons


def _playoff_pairs() -> list[ NhlSkaterSeason ]:
   seasons: list[ NhlSkaterSeason ] = []

   for player_id in range( _PLAYERS ):
      goals = _goals( player_id )
      assists = _assists( player_id )
      prior = replace(
         _nhl( player_id, 2020, goals, assists, 25.4 ),
         playoff_games=20,
         playoff_goals=player_id % 5,
         playoff_assists=player_id % 4 )
      surplus = prior.playoff_surplus()
      seasons.append( prior )
      seasons.append(
         _nhl(
            player_id,
            2021,
            2.0 + 0.5 * goals + 1.5 * surplus.goals,
            1.0 + 0.25 * assists + 0.8 * surplus.assists,
            26.4 ) )

   return seasons


def _goal_error( model: PaceRegressionModel, seasons: list[ NhlSkaterSeason ] ) -> float:
   error = 0.0

   for target in seasons:
      if Season.start_year( target.season_id ) != 2021:
         continue

      priors = PriorYearBuilder.build(
         [ season for season in seasons if season.player_id == target.player_id ],
         [],
         2021 )
      pace = PaceRegressionPredictor.pace( model, priors, 2021 )
      assert pace is not None
      error += ( pace.goals - target.g_pace ) ** 2

   return error


def Test_Fit_TestLinearPairs_ExpectRecoveredBandRegression() -> None:
   seasons = _pairs( _PLAYERS )

   model = PaceRegressionFitter.fit( seasons, [], [] )

   assert len( model.regressions ) == 1
   regression = model.regressions[ Position.FIRST ]
   assert regression.source == PriorSource.NHL
   assert regression.band == AgeBand( 25, 26 )
   assert regression.goal_constant == pytest.approx( 2.0 )
   assert regression.goal_weights == pytest.approx( [ 0.5 ] )
   assert regression.assist_constant == pytest.approx( 1.0 )
   assert regression.assist_weights == pytest.approx( [ 0.25 ] )
   assert model.playoff_goal_weight == PaceRegressionFitter.NO_PLAYOFF_WEIGHT
   assert model.playoff_assist_weight == PaceRegressionFitter.NO_PLAYOFF_WEIGHT


def Test_Fit_TestPlayoffSurplus_ExpectErrorMinimizingPositiveWeights() -> None:
   seasons = _playoff_pairs()
   step = 0.1

   model = PaceRegressionFitter.fit( seasons, [], [] )

   fitted = _goal_error( model, seasons )
   assert model.playoff_goal_weight > PaceRegressionFitter.NO_PLAYOFF_WEIGHT
   assert model.playoff_assist_weight > PaceRegressionFitter.NO_PLAYOFF_WEIGHT
   assert fitted < _goal_error(
      replace( model, playoff_goal_weight=model.playoff_goal_weight + step ), seasons )
   assert fitted < _goal_error(
      replace( model, playoff_goal_weight=model.playoff_goal_weight - step ), seasons )


def Test_Fit_TestReturningPlayers_ExpectGapScaleWithoutChangingFit() -> None:
   count = _PLAYERS
   seasons = _pairs( count ) + _pairs( count, gap=1, scale=0.8, first_id=count )

   model = PaceRegressionFitter.fit( seasons, [], [] )

   assert model.regressions[ Position.FIRST ].goal_constant == pytest.approx( 2.0 )
   assert model.nhl_gap_goals == pytest.approx( 0.8 )
   assert model.nhl_gap_assists == pytest.approx( 0.8 )


def Test_Fit_TestOtherLeaguePriors_ExpectTranslatedRegressions() -> None:
   factor = LeagueFactor( 'AAA', 0.5 )
   other_seasons = [
      _other( player_id, 2020, 2.0 * _goals( player_id ), 2.0 * _assists( player_id ) )
      for player_id in range( _PLAYERS )
   ]
   nhl_seasons = [
      _nhl( player_id, 2021, 3.0 + 0.5 * _goals( player_id ), 4.0 + 0.5 * _assists( player_id ), 19.4 )
      for player_id in range( _PLAYERS )
   ]

   model = PaceRegressionFitter.fit( nhl_seasons, other_seasons, [ factor ] )

   assert { regression.source for regression in model.regressions } == { PriorSource.TRANSLATED }
   assert model.regressions[ Position.FIRST ].goal_constant == pytest.approx( 3.0 )
   assert model.regressions[ Position.FIRST ].goal_weights == pytest.approx( [ 0.5 ] )


def Test_Fit_TestNoSamples_ExpectEmptyModel() -> None:
   seasons = _pairs( 0 )

   model = PaceRegressionFitter.fit( seasons, [], [] )

   assert model.regressions == []
   assert model.nhl_gap_goals == PaceRegressionFitter.NO_DISCOUNT
   assert model.nhl_gap_assists == PaceRegressionFitter.NO_DISCOUNT
