from __future__ import annotations

from api.projections.scoring_component_shares import ScoringComponentShares
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.production_coefficient import ProductionCoefficient
from api.recency.production_growth import ProductionGrowth
from api.recency.production_weight import ProductionWeight


def Test_FromRow_TestModel_ExpectRoundTrip() -> None:
   model = PaceRegressionModel(
      [ ProductionGrowth( 18, 19, 1.2, 100 ) ], [ ScoringComponentShares( 18, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 ) ],
      pim_coefficients=[ ProductionCoefficient( 18, 19, 1.1, 0.8, 100 ) ],
      shots_coefficients=[ ProductionCoefficient( 18, 19, 1.2, 0.9, 100 ) ],
      history_weights=[ ProductionWeight( 18, 19, 0.8, 100 ) ] )

   assert PaceRegressionModel.from_row( model.to_dict() ) == model


def Test_ToDict_TestModel_ExpectOnlyRegressions() -> None:
   assert PaceRegressionModel( [] ).to_dict() == {
      'scoring': { 'growth': [], 'history_weights': [] }, 'component_shares': [],
      'pim': { 'coefficients': [] }, 'shots': { 'coefficients': [] },
   }
