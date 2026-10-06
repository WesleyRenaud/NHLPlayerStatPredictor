from .pace_regression_model import PaceRegressionModel
from .pim_multiplier_store import PimMultiplierStore
from .pim_weight_store import PimWeightStore
from .production_debut_trajectory_store import ProductionDebutTrajectoryStore
from .production_growth import ProductionGrowth
from .production_short_nhl_trajectory_store import ProductionShortNhlTrajectoryStore
from .production_trajectory_store import ProductionTrajectoryStore
from .production_weight import ProductionWeight
from .scoring_component_share_store import ScoringComponentShareStore
from .scoring_multiplier_store import ScoringMultiplierStore
from .scoring_weight_store import ScoringWeightStore
from .shots_multiplier_store import ShotsMultiplierStore
from .shots_weight_store import ShotsWeightStore


class ProductionModelRecorder():
   """Distribute fitted model data to its individual file stores."""

   @classmethod
   def write( cls, model: PaceRegressionModel ) -> None:
      ScoringMultiplierStore.write( model.scoring_growth )
      ScoringWeightStore.write( model.history_weights )
      ProductionTrajectoryStore.write( model.trajectory )
      ProductionDebutTrajectoryStore.write( model.debut_trajectory )
      ProductionShortNhlTrajectoryStore.write( model.short_nhl_trajectory )
      ScoringComponentShareStore.write( model.component_shares )

      for coefficients, multiplier_store, weight_store in (
            ( model.pim_coefficients, PimMultiplierStore, PimWeightStore ),
            ( model.shots_coefficients, ShotsMultiplierStore, ShotsWeightStore ) ):
         multiplier_store.write( [
            ProductionGrowth( item.from_age, item.to_age, item.multiplier, item.samples )
            for item in coefficients if item.to_age == item.from_age + 1
         ] )
         weight_store.write( [
            ProductionWeight( item.from_age, item.to_age, item.weight, item.samples )
            for item in coefficients
         ] )
