from __future__ import annotations

import math

from .draft_pick_modifier import DraftPickModifier
from .draft_pick_regression import DraftPickRegression
from .prospect_calibration_sample import ProspectCalibrationSample


class DraftPickModifierFitter():
   @classmethod
   def fit(
         cls,
         samples: list[ ProspectCalibrationSample ],
         target_season_id: int,
         excluded_player_id: int ) -> DraftPickModifier:
      log_picks: list[ float ] = []
      predicted_points: list[ float ] = []
      actual_points: list[ float ] = []
      for sample in samples:
         pick = sample.draft_pick.value
         if (
               sample.season_id >= target_season_id or sample.player_id == excluded_player_id
               or pick is None or sample.predicted_points <= 0 ):
            continue
         log_picks.append( math.log( pick ) )
         predicted_points.append( sample.predicted_points )
         actual_points.append( sample.actual_points )
      return DraftPickRegression.fit( log_picks, predicted_points, actual_points )
