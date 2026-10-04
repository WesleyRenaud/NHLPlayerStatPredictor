from __future__ import annotations

import pytest

from api.projections.draft_pick_regression import DraftPickRegression


def Test_Fit_TestNumericInputs_ExpectLinearCoefficients() -> None:
   expected_intercept = 2.0
   expected_log_pick_coefficient = -0.25
   log_picks = [ 0.0, 1.0, 3.0 ]
   predicted_points = [ 10.0, 30.0, 20.0 ]
   actual_points = [
      baseline * ( expected_intercept + expected_log_pick_coefficient * log_pick )
      for log_pick, baseline in zip( log_picks, predicted_points )
   ]

   modifier = DraftPickRegression.fit( log_picks, predicted_points, actual_points )

   assert modifier.intercept == pytest.approx( expected_intercept )
   assert modifier.log_pick_coefficient == pytest.approx( expected_log_pick_coefficient )
