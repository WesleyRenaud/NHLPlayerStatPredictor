from .production_weight_store import ProductionWeightStore


class ScoringWeightStore( ProductionWeightStore ):
   FILE_NAME = 'scoring_weights.json'
