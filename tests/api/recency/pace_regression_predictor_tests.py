from __future__ import annotations

import pytest

from api.projections.season_pace import SeasonPace
from api.recency.age_band import AgeBand
from api.recency.pace_regression import PaceRegression
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pace_regression_predictor import PaceRegressionPredictor
from api.recency.prior_source import PriorSource
from api.recency.prior_year import PriorYear


def _prior( year: int, goals: float, nhl_games: int = 82, age: float = 25.4 ) -> PriorYear:
   return PriorYear( year, SeasonPace( goals, goals ), 82, nhl_games, age )


def _model() -> PaceRegressionModel:
   return PaceRegressionModel(
      [
         PaceRegression( PriorSource.NHL, AgeBand( 25, 26 ), 1.0, [ 0.5 ], 1.0, [ 0.5 ] ),
         PaceRegression( PriorSource.NHL, AgeBand( 25, 26 ), 9.0, [ 0.1, 0.1 ], 9.0, [ 0.1, 0.1 ] ),
         PaceRegression( PriorSource.TRANSLATED, AgeBand( 24, 40 ), 3.0, [ 0.8 ], 3.0, [ 0.8 ] ),
      ],
      0.8,
      0.9 )


def Test_Regressed_TestNoPriors_ExpectNone() -> None:
   regressed = PaceRegressionPredictor.regressed( _model().regressions, [] )

   assert regressed is None


def Test_Regressed_TestWidestMatch_ExpectWiderRegression() -> None:
   priors = [ _prior( 2024, 20.0 ), _prior( 2023, 10.0 ) ]

   regressed = PaceRegressionPredictor.regressed( _model().regressions, priors )

   assert regressed is not None
   assert regressed.goals == pytest.approx( 9.0 + 0.1 * 20.0 + 0.1 * 10.0 )


def Test_Regressed_TestAgeOutsideBands_ExpectNone() -> None:
   priors = [ _prior( 2024, 20.0, age=30.2 ) ]

   regressed = PaceRegressionPredictor.regressed( _model().regressions, priors )

   assert regressed is None


def Test_Regressed_TestTranslatedLatest_ExpectTranslatedRegression() -> None:
   priors = [ _prior( 2024, 20.0, nhl_games=0 ) ]

   regressed = PaceRegressionPredictor.regressed( _model().regressions, priors )

   assert regressed is not None
   assert regressed.goals == pytest.approx( 3.0 + 0.8 * 20.0 )


def Test_Pace_TestNhlGap_ExpectDiscount() -> None:
   model = _model()
   priors = [ _prior( 2023, 20.0 ) ]

   paced = PaceRegressionPredictor.pace( model, priors, 2025 )

   assert paced is not None
   assert paced.goals == pytest.approx( ( 1.0 + 0.5 * 20.0 ) * model.nhl_gap_goals )
   assert paced.assists == pytest.approx( ( 1.0 + 0.5 * 20.0 ) * model.nhl_gap_assists )


def Test_Pace_TestTranslatedGap_ExpectNoDiscount() -> None:
   priors = [ _prior( 2023, 20.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.pace( _model(), priors, 2025 )

   assert paced is not None
   assert paced.goals == pytest.approx( 3.0 + 0.8 * 20.0 )


def Test_Pace_TestNoGap_ExpectRegressed() -> None:
   model = _model()
   priors = [ _prior( 2024, 20.0 ) ]

   paced = PaceRegressionPredictor.pace( model, priors, 2025 )

   assert paced == PaceRegressionPredictor.regressed( model.regressions, priors )
