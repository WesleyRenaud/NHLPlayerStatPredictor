from __future__ import annotations

from api.recency.pace_regression_model import PaceRegressionModel


def Test_FromRow_TestModel_ExpectRoundTrip() -> None:
   model = PaceRegressionModel( [] )

   assert PaceRegressionModel.from_row( model.to_dict() ) == model


def Test_ToDict_TestModel_ExpectOnlyRegressions() -> None:
   assert PaceRegressionModel( [] ).to_dict() == { 'regressions': [] }
