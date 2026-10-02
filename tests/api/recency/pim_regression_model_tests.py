from __future__ import annotations

from api.recency.pim_regression_model import PimRegressionModel
from api.recency.production_coefficient import ProductionCoefficient


def Test_FromRow_TestModel_ExpectRoundTrip() -> None:
   model = PimRegressionModel( [ ProductionCoefficient( 18, 19, 1.2, 0.8, 100 ) ] )

   assert PimRegressionModel.from_row( model.to_dict() ) == model


def Test_ToDict_TestModel_ExpectOnlyCoefficients() -> None:
   assert PimRegressionModel( [] ).to_dict() == { 'coefficients': [] }
