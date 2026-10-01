from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.aging.league_factor import LeagueFactor
from api.projections.baseline_pace_resolver import BaselinePaceResolver
from api.projections.power_play_pace import PowerPlayPace
from api.recency.age_band import AgeBand
from api.recency.pace_regression import PaceRegression
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pim_regression import PimRegression
from api.recency.pim_regression_model import PimRegressionModel
from api.recency.prior_source import PriorSource
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater import Skater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


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
   return PaceRegressionModel(
      [
         PaceRegression(
            source=PriorSource.NHL,
            band=AgeBand( 27, 28 ),
            goal_constant=1.0,
            goal_weights=[ 0.5 ],
            assist_constant=2.0,
            assist_weights=[ 0.5 ],
            power_play_goal_constant=0.0,
            power_play_goal_weights=[ 0.0 ],
            power_play_assist_constant=0.0,
            power_play_assist_weights=[ 0.0 ],
            short_handed_goal_constant=0.0,
            short_handed_goal_weights=[ 0.0 ],
            short_handed_assist_constant=0.0,
            short_handed_assist_weights=[ 0.0 ] ),
         PaceRegression(
            source=PriorSource.TRANSLATED,
            band=AgeBand( 17, 19 ),
            goal_constant=3.0,
            goal_weights=[ 0.8 ],
            assist_constant=4.0,
            assist_weights=[ 0.8 ],
            power_play_goal_constant=0.0,
            power_play_goal_weights=[ 0.0 ],
            power_play_assist_constant=0.0,
            power_play_assist_weights=[ 0.0 ],
            short_handed_goal_constant=0.0,
            short_handed_goal_weights=[ 0.0 ],
            short_handed_assist_constant=0.0,
            short_handed_assist_weights=[ 0.0 ] ),
      ],
      0.8,
      0.9,
      1.5,
      0.5,
      1.0,
      1.0,
      1.0,
      1.0 )


def _pim_model() -> PimRegressionModel:
   return PimRegressionModel(
      regressions=[ PimRegression( constant=4.0, weights=[ 0.5 ] ) ],
      nhl_gap_scale=0.8 )


def Test_Resolve_TestNhlSeason_ExpectRegressedPace() -> None:
   season = _nhl( 20242025, 20.0, 30.0, 27.4 )
   model = _model()
   pim_model = _pim_model()
   regression = model.regressions[ Position.FIRST ]
   pim_regression = pim_model.regressions[ Position.FIRST ]

   resolved = BaselinePaceResolver.resolve( Skater( [ season ] ), 20252026, [], model, pim_model )

   assert resolved is not None
   assert resolved.goals == pytest.approx(
      regression.goal_constant + regression.goal_weights[ Position.FIRST ] * season.g_pace )
   assert resolved.assists == pytest.approx(
      regression.assist_constant + regression.assist_weights[ Position.FIRST ] * season.a_pace )
   assert resolved.penalty_minutes == pytest.approx(
      pim_regression.constant + pim_regression.weights[ Position.FIRST ] * season.penalty_minutes_pace() )


def Test_Resolve_TestPlayoffSurplus_ExpectWeightedSurplusAdded() -> None:
   regular = _nhl( 20242025, 20.0, 30.0, 27.4 )
   season = replace( regular, playoff_games=10, playoff_goals=5, playoff_assists=3 )
   model = _model()
   surplus = season.playoff_surplus()

   without = BaselinePaceResolver.resolve( Skater( [ regular ] ), 20252026, [], model, _pim_model() )
   resolved = BaselinePaceResolver.resolve( Skater( [ season ] ), 20252026, [], model, _pim_model() )

   assert without is not None
   assert resolved is not None
   assert resolved.goals == pytest.approx(
      without.goals + model.playoff_goal_weight * surplus.goals )
   assert resolved.assists == pytest.approx(
      without.assists + model.playoff_assist_weight * surplus.assists )


def Test_Resolve_TestOtherLeagueOnly_ExpectTranslatedRegression() -> None:
   factor = LeagueFactor( 'AAA', 0.4 )
   season = _other( 20242025, 30.0, 50.0, factor.league )
   model = _model()
   regression = model.regressions[ Position.LAST ]

   resolved = BaselinePaceResolver.resolve(
      Skater( [ season ] ),
      20252026,
      [ factor ],
      model,
      _pim_model() )

   assert resolved is not None
   assert resolved.goals == pytest.approx(
      regression.goal_constant + regression.goal_weights[ Position.FIRST ] * season.g_pace * factor.rate )
   assert resolved.assists == pytest.approx(
      regression.assist_constant + regression.assist_weights[ Position.FIRST ] * season.a_pace * factor.rate )
   assert resolved.power_play_goals == 0.0
   assert resolved.power_play_assists == 0.0
   assert resolved.penalty_minutes is None


def Test_Resolve_TestLatestOtherLeague_ExpectIndependentNhlPim() -> None:
   factor = LeagueFactor( 'AAA', 0.4 )
   nhl = replace( _nhl( 20222023, 20.0, 30.0, 27.4 ), penalty_minutes=20 )
   other = _other( 20242025, 30.0, 50.0, factor.league )
   model = _model()
   pim_model = _pim_model()
   scoring_regression = model.regressions[ Position.LAST ]
   pim_regression = pim_model.regressions[ Position.FIRST ]

   resolved = BaselinePaceResolver.resolve(
      Skater( [ nhl, other ] ),
      20252026,
      [ factor ],
      model,
      pim_model )

   assert resolved is not None
   assert resolved.goals == pytest.approx(
      scoring_regression.goal_constant
      + scoring_regression.goal_weights[ Position.FIRST ] * other.g_pace * factor.rate )
   assert resolved.penalty_minutes == pytest.approx(
      ( pim_regression.constant
        + pim_regression.weights[ Position.FIRST ] * nhl.penalty_minutes_pace() )
      * pim_model.nhl_gap_scale )


def Test_Resolve_TestMissedSeason_ExpectGapDiscount() -> None:
   season = _nhl( 20232024, 20.0, 30.0, 27.4 )
   model = _model()
   pim_model = _pim_model()
   regression = model.regressions[ Position.FIRST ]
   pim_regression = pim_model.regressions[ Position.FIRST ]

   resolved = BaselinePaceResolver.resolve( Skater( [ season ] ), 20252026, [], model, pim_model )

   assert resolved is not None
   assert resolved.goals == pytest.approx(
      ( regression.goal_constant + regression.goal_weights[ Position.FIRST ] * season.g_pace )
      * model.nhl_gap_goals )
   assert resolved.assists == pytest.approx(
      ( regression.assist_constant + regression.assist_weights[ Position.FIRST ] * season.a_pace )
      * model.nhl_gap_assists )
   assert resolved.power_play_goals == 0.0
   assert resolved.power_play_assists == 0.0
   assert resolved.penalty_minutes == pytest.approx(
      ( pim_regression.constant
        + pim_regression.weights[ Position.FIRST ] * season.penalty_minutes_pace() )
      * pim_model.nhl_gap_scale )


def Test_Resolve_TestNoSeasons_ExpectNone() -> None:
   resolved = BaselinePaceResolver.resolve( Skater( [] ), 20252026, [], _model(), _pim_model() )

   assert resolved is None
