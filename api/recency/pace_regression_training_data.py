from __future__ import annotations

from dataclasses import dataclass, field

from .prior_source import PriorSource
from .production_pair import ProductionPair
from ..projections.scoring_stat import ScoringStat


@dataclass
class PaceRegressionTrainingData():
   source: PriorSource
   stat: ScoringStat
   samples: list[ ProductionPair ] = field( default_factory=list )
