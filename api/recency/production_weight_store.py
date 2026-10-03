from .production_list_store import ProductionListStore
from .production_weight import ProductionWeight


class ProductionWeightStore( ProductionListStore ):


   @classmethod
   def read( cls ) -> list[ ProductionWeight ]:
      return [ ProductionWeight.from_row( row ) for row in cls.read_rows() ]


   @classmethod
   def write( cls, weights: list[ ProductionWeight ] ) -> None:
      cls.write_rows( [ weight.to_dict() for weight in weights ] )
