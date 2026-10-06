from functools import partial
from pathlib import Path

from .pace_regression_model import PaceRegressionModel
from .pim_multiplier_store import PimMultiplierStore
from .pim_weight_store import PimWeightStore
from .production_coefficient import ProductionCoefficient
from .production_debut_trajectory_store import ProductionDebutTrajectoryStore
from .production_growth import ProductionGrowth
from .production_history_predictor import ProductionHistoryPredictor
from .production_short_nhl_trajectory_store import ProductionShortNhlTrajectoryStore
from .production_trajectory_store import ProductionTrajectoryStore
from .production_weight import ProductionWeight
from .scoring_component_share_store import ScoringComponentShareStore
from .scoring_multiplier_store import ScoringMultiplierStore
from .scoring_weight_store import ScoringWeightStore
from .shots_multiplier_store import ShotsMultiplierStore
from .shots_weight_store import ShotsWeightStore


class ProductionModelProvider():
   """Assemble the projection model from independently stored production data."""

   @classmethod
   def paths( cls ) -> list[ Path ]:
      return [
         ScoringWeightStore.path(), ScoringMultiplierStore.path(),
         ProductionTrajectoryStore.path(), ProductionDebutTrajectoryStore.path(),
         ProductionShortNhlTrajectoryStore.path(),
         PimWeightStore.path(), PimMultiplierStore.path(),
         ShotsWeightStore.path(), ShotsMultiplierStore.path(),
         ScoringComponentShareStore.path(),
      ]


   @classmethod
   def read( cls ) -> PaceRegressionModel:
      return PaceRegressionModel(
         ScoringMultiplierStore.read(),
         ScoringComponentShareStore.read(),
         cls._coefficients( PimMultiplierStore.read(), PimWeightStore.read() ),
         cls._coefficients( ShotsMultiplierStore.read(), ShotsWeightStore.read() ),
         ScoringWeightStore.read(),
         ProductionTrajectoryStore.read(),
         ProductionDebutTrajectoryStore.read(),
         ProductionShortNhlTrajectoryStore.read() )


   @classmethod
   def _coefficients(
         cls,
         growth: list[ ProductionGrowth ],
         weights: list[ ProductionWeight ] ) -> list[ ProductionCoefficient ]:
      lookup = partial( ProductionHistoryPredictor.coefficient, growth )
      return [
         ProductionCoefficient(
            weight.from_age, weight.to_age,
            ProductionHistoryPredictor.multiplier( lookup, weight.from_age, weight.to_age ),
            weight.weight, weight.samples )
         for weight in weights
      ]
