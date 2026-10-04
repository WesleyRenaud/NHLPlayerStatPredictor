from __future__ import annotations

import math

import pytest

from api.projections.draft_pick import DraftPick
from api.projections.draft_pick_modifier import DraftPickModifier
from api.projections.draft_pick_modifier_fitter import DraftPickModifierFitter
from api.projections.prospect_calibration_sample import ProspectCalibrationSample


def _sample( player_id: int, pick: int | None, predicted: float, actual: float ) -> ProspectCalibrationSample:
   return ProspectCalibrationSample( player_id, 20242025, DraftPick( pick ), predicted, actual, 'SHL' )


def Test_Fit_TestKnownCurve_ExpectRecoveredCoefficients() -> None:
   expected_intercept = 1.8
   expected_log_pick_coefficient = -0.2
   earlier_pick = 10
   later_pick = 11
   samples = [
      _sample(
         pick, pick, 10.0 + pick,
         ( 10.0 + pick ) * ( expected_intercept + expected_log_pick_coefficient * math.log( pick ) ) )
      for pick in [ 1, 3, 10, 11, 32, 100 ]
   ]
   expected_factor_difference = expected_log_pick_coefficient * math.log( earlier_pick / later_pick )

   modifier = DraftPickModifierFitter.fit( samples, 20262027, excluded_player_id=200 )

   assert modifier.intercept == pytest.approx( expected_intercept )
   assert modifier.log_pick_coefficient == pytest.approx( expected_log_pick_coefficient )
   assert modifier.factor( earlier_pick ) - modifier.factor( later_pick ) == pytest.approx( expected_factor_difference )


def Test_Fit_TestNoisyPoints_ExpectLeastSquaresNormalEquations() -> None:
   samples = [
      _sample( 1, 1, 10.0, 20.0 ), _sample( 2, 5, 30.0, 25.0 ), _sample( 3, 100, 20.0, 30.0 ),
   ]
   modifier = DraftPickModifierFitter.fit( samples, 20262027, excluded_player_id=4 )

   residuals = [
      ( sample, sample.actual_points - sample.predicted_points * modifier.factor( sample.draft_pick.value ) )
      for sample in samples
   ]
   assert sum( sample.predicted_points * residual for sample, residual in residuals ) == pytest.approx( 0.0, abs=1e-10 )
   assert sum(
      sample.predicted_points * math.log( sample.draft_pick.value ) * residual
      for sample, residual in residuals if sample.draft_pick.value is not None ) == pytest.approx( 0.0, abs=1e-10 )


def Test_Fit_TestFutureSelfUndraftedAndZeroBaseline_ExpectExcluded() -> None:
   expected_factor = 2.0
   first_baseline = 10.0
   second_baseline = 20.0
   samples = [
      _sample( 1, 1, first_baseline, first_baseline * expected_factor ),
      _sample( 2, 10, second_baseline, second_baseline * expected_factor ),
   ]
   extra = [
      ProspectCalibrationSample( 3, 20262027, DraftPick( 1 ), 100.0, 0.0, 'OHL' ),
      _sample( 4, 1, 100.0, 0.0 ), _sample( 5, None, 100.0, 0.0 ), _sample( 6, 1, 0.0, 100.0 ),
   ]

   modifier = DraftPickModifierFitter.fit( samples + extra, 20262027, excluded_player_id=4 )

   assert modifier.intercept == pytest.approx( expected_factor )
   assert modifier.log_pick_coefficient == pytest.approx( 0.0 )
   assert modifier.factor( None ) == 1.0


def Test_Factor_TestExtrapolation_ExpectUnclampedCurve() -> None:
   intercept = 1.0
   coefficient = -1.0
   pick = 100
   modifier = DraftPickModifier( intercept, coefficient )
   expected_factor = intercept + coefficient * math.log( pick )

   assert modifier.factor( pick ) == pytest.approx( expected_factor )
