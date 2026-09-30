from __future__ import annotations

import pytest

from api.projections.power_play_pace import PowerPlayPace
from api.projections.season_pace import SeasonPace
from api.recency.age_band import AgeBand
from api.recency.pace_regression import PaceRegression
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pace_regression_predictor import PaceRegressionPredictor
from api.recency.prior_source import PriorSource
from api.recency.prior_year import PriorYear
from api.shared.enums.position import Position


def _prior(
      year: int,
      goals: float,
      nhl_games: int = 82,
      age: float = 25.4,
      surplus: SeasonPace = SeasonPace.zero(),
      power_play_goals: float = 0.0,
      power_play_assists: float = 0.0 ) -> PriorYear:
   return PriorYear(
      year,
      SeasonPace( goals, goals ),
      PowerPlayPace( power_play_goals, power_play_assists ),
      82,
      nhl_games,
      age,
      surplus )


def _model() -> PaceRegressionModel:
   return PaceRegressionModel(
      [
         PaceRegression(
            source=PriorSource.NHL,
            band=AgeBand( 25, 26 ),
            goal_constant=1.0,
            goal_weights=[ 0.5 ],
            assist_constant=1.0,
            assist_weights=[ 0.5 ],
            power_play_goal_constant=2.0,
            power_play_goal_weights=[ 0.5 ],
            power_play_assist_constant=1.0,
            power_play_assist_weights=[ 0.25 ] ),
         PaceRegression(
            source=PriorSource.NHL,
            band=AgeBand( 25, 26 ),
            goal_constant=9.0,
            goal_weights=[ 0.1, 0.1 ],
            assist_constant=9.0,
            assist_weights=[ 0.1, 0.1 ],
            power_play_goal_constant=8.0,
            power_play_goal_weights=[ 0.1, 0.1 ],
            power_play_assist_constant=7.0,
            power_play_assist_weights=[ 0.1, 0.1 ] ),
         PaceRegression(
            source=PriorSource.TRANSLATED,
            band=AgeBand( 24, 40 ),
            goal_constant=3.0,
            goal_weights=[ 0.8 ],
            assist_constant=3.0,
            assist_weights=[ 0.8 ],
            power_play_goal_constant=4.0,
            power_play_goal_weights=[ 0.4 ],
            power_play_assist_constant=2.0,
            power_play_assist_weights=[ 0.3 ] ),
      ],
      0.8,
      0.9,
      1.2,
      0.7,
      0.8,
      0.6 )


def Test_Regressed_TestNoPriors_ExpectNone() -> None:
   regressed = PaceRegressionPredictor.regressed_paces( _model().regressions, [] )

   assert regressed is None


def Test_Regressed_TestWidestMatch_ExpectWiderRegression() -> None:
   model = _model()
   priors = [
      _prior( 2024, 20.0, power_play_goals=20.0 ),
      _prior( 2023, 10.0, power_play_goals=10.0 ),
   ]
   wide_regression = next(
      regression
      for regression in model.regressions
      if regression.source == PriorSource.NHL and len( regression.goal_weights ) == 2 )
   expected_power_play_goals = wide_regression.power_play_goal_constant + sum(
      weight * prior.power_play_pace.goals
      for weight, prior in zip( wide_regression.power_play_goal_weights, priors ) )

   regressed = PaceRegressionPredictor.regressed_paces( model.regressions, priors )

   assert regressed is not None
   assert regressed.goals == pytest.approx( 9.0 + 0.1 * 20.0 + 0.1 * 10.0 )
   assert regressed.power_play_goals == pytest.approx( expected_power_play_goals )


def Test_Regressed_TestAgeOutsideBands_ExpectNone() -> None:
   priors = [ _prior( 2024, 20.0, age=30.2 ) ]

   regressed = PaceRegressionPredictor.regressed_paces( _model().regressions, priors )

   assert regressed is None


def Test_Regressed_TestTranslatedLatest_ExpectTranslatedRegression() -> None:
   model = _model()
   priors = [ _prior( 2024, 20.0, nhl_games=0, power_play_goals=20.0 ) ]
   translated_regression = next(
      regression
      for regression in model.regressions
      if regression.source == PriorSource.TRANSLATED )
   expected_power_play_goals = translated_regression.power_play_goal_constant + sum(
      weight * prior.power_play_pace.goals
      for weight, prior in zip( translated_regression.power_play_goal_weights, priors ) )

   regressed = PaceRegressionPredictor.regressed_paces( model.regressions, priors )

   assert regressed is not None
   assert regressed.goals == pytest.approx( 3.0 + 0.8 * 20.0 )
   assert regressed.power_play_goals == pytest.approx( expected_power_play_goals )


def Test_Pace_TestNhlGap_ExpectDiscount() -> None:
   model = _model()
   priors = [ _prior( 2023, 20.0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 2025 )

   assert paced is not None
   assert paced.goals == pytest.approx( ( 1.0 + 0.5 * 20.0 ) * model.nhl_gap_goals )
   assert paced.assists == pytest.approx( ( 1.0 + 0.5 * 20.0 ) * model.nhl_gap_assists )


def Test_Pace_TestTranslatedGap_ExpectNoDiscount() -> None:
   priors = [ _prior( 2023, 20.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( _model(), priors, 2025 )

   assert paced is not None
   assert paced.goals == pytest.approx( 3.0 + 0.8 * 20.0 )


def Test_Pace_TestNoGap_ExpectRegressed() -> None:
   model = _model()
   priors = [ _prior( 2024, 20.0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 2025 )

   assert paced == PaceRegressionPredictor.regressed_paces( model.regressions, priors )


def Test_Pace_TestNhlPlayoffSurplus_ExpectWeightedSurplusAdded() -> None:
   model = _model()
   surplus = SeasonPace( 4.0, 6.0 )
   priors = [ _prior( 2024, 20.0, surplus=surplus ) ]
   regressed = PaceRegressionPredictor.regressed_paces( model.regressions, priors )

   paced = PaceRegressionPredictor.paces( model, priors, 2025 )

   assert regressed is not None
   assert paced is not None
   assert paced.goals == pytest.approx(
      regressed.goals + model.playoff_goal_weight * surplus.goals )
   assert paced.assists == pytest.approx(
      regressed.assists + model.playoff_assist_weight * surplus.assists )


def Test_Pace_TestPlayoffSurplusAfterGap_ExpectSurplusDiscounted() -> None:
   model = _model()
   surplus = SeasonPace( 4.0, 6.0 )
   priors = [ _prior( 2023, 20.0, surplus=surplus ) ]
   regressed = PaceRegressionPredictor.regressed_paces( model.regressions, priors )

   paced = PaceRegressionPredictor.paces( model, priors, 2025 )

   assert regressed is not None
   assert paced is not None
   assert paced.goals == pytest.approx(
      ( regressed.goals + model.playoff_goal_weight * surplus.goals ) * model.nhl_gap_goals )


def Test_Pace_TestTranslatedPlayoffSurplus_ExpectIgnored() -> None:
   priors = [ _prior( 2024, 20.0, nhl_games=0, surplus=SeasonPace( 4.0, 6.0 ) ) ]
   model = _model()

   paced = PaceRegressionPredictor.paces( model, priors, 2025 )

   assert paced == PaceRegressionPredictor.regressed_paces( model.regressions, priors )


def Test_Paces_TestNhlGap_ExpectRegularAndPowerPlayScales() -> None:
   model = _model()
   prior = _prior( 2023, 20.0, power_play_goals=10.0, power_play_assists=8.0 )
   priors = [ prior ]
   regression = model.regressions[ Position.FIRST ]
   expected_power_play_goals = (
      regression.power_play_goal_constant
      + sum(
         weight * prior.power_play_pace.goals
         for weight, prior in zip( regression.power_play_goal_weights, priors ) )
   ) * model.nhl_gap_power_play_goals
   expected_power_play_assists = (
      regression.power_play_assist_constant
      + sum(
         weight * prior.power_play_pace.assists
         for weight, prior in zip( regression.power_play_assist_weights, priors ) )
   ) * model.nhl_gap_power_play_assists

   paced = PaceRegressionPredictor.paces( model, priors, 2025 )

   assert paced is not None
   assert paced.power_play_goals == pytest.approx( expected_power_play_goals )
   assert paced.power_play_assists == pytest.approx( expected_power_play_assists )
