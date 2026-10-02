from __future__ import annotations

from api.projections.scoring_component_shares import ScoringComponentShares
from api.recency.pace_regression_model import PaceRegressionModel


def Test_FromRow_TestModel_ExpectRoundTrip() -> None:
   model = PaceRegressionModel( [], [ ScoringComponentShares( 18, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 ) ] )

   assert PaceRegressionModel.from_row( model.to_dict() ) == model


def Test_ToDict_TestModel_ExpectOnlyRegressions() -> None:
   assert PaceRegressionModel( [] ).to_dict() == { 'regressions': [], 'component_shares': [] }
