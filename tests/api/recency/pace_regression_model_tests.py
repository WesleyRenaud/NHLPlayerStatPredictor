from __future__ import annotations

from api.recency.age_band import AgeBand
from api.recency.pace_regression import PaceRegression
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.prior_source import PriorSource


def Test_FromRow_TestDict_ExpectRoundTrip() -> None:
   model = PaceRegressionModel(
      [
         PaceRegression( PriorSource.NHL, AgeBand( 25, 26 ), 1.0, [ 0.5 ], 1.0, [ 0.5 ] ),
         PaceRegression( PriorSource.TRANSLATED, AgeBand( 24, 40 ), 3.0, [ 0.8, 0.1 ], 3.0, [ 0.8, 0.1 ] ),
      ],
      0.8,
      0.9 )

   loaded = PaceRegressionModel.from_row( model.to_dict() )

   assert loaded == model
