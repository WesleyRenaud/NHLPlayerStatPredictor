from __future__ import annotations

from .current_season_weight import CurrentSeasonWeight
from ..paths import Paths
from .production_list_store import ProductionListStore


class CurrentSeasonWeightStore( ProductionListStore ):
   FILE_NAME = 'current_season_weights.json'
   FOLDER = Paths.RECENCY


   @classmethod
   def read( cls ) -> list[ CurrentSeasonWeight ]:
      return [ CurrentSeasonWeight.from_row( row ) for row in cls.read_rows() ]


   @classmethod
   def write( cls, weights: list[ CurrentSeasonWeight ] ) -> None:
      cls.write_rows( [ weight.to_dict() for weight in weights ] )
