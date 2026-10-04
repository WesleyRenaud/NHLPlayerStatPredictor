from __future__ import annotations

import math

from .draft_pick_modifier import DraftPickModifier


class DraftPickRegression():
   @classmethod
   def fit(
         cls,
         log_picks: list[ float ],
         predicted_points: list[ float ],
         actual_points: list[ float ] ) -> DraftPickModifier:
      weight = math.fsum( predicted ** 2 for predicted in predicted_points )
      mean_log_pick = math.fsum(
         pick * predicted ** 2 for pick, predicted in zip( log_picks, predicted_points ) ) / weight
      mean_ratio = math.fsum(
         predicted * actual for predicted, actual in zip( predicted_points, actual_points ) ) / weight
      variance = math.fsum(
         predicted ** 2 * ( pick - mean_log_pick ) ** 2
         for pick, predicted in zip( log_picks, predicted_points ) )
      # Weighting by baseline squared minimizes point errors, not noisy individual ratios.
      covariance = math.fsum(
         predicted * ( pick - mean_log_pick ) * ( actual - predicted * mean_ratio )
         for pick, predicted, actual in zip( log_picks, predicted_points, actual_points ) )
      coefficient = covariance / variance
      return DraftPickModifier( mean_ratio - coefficient * mean_log_pick, coefficient )
