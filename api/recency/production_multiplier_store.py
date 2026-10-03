from .production_growth import ProductionGrowth
from .production_list_store import ProductionListStore


class ProductionMultiplierStore( ProductionListStore ):


   @classmethod
   def read( cls ) -> list[ ProductionGrowth ]:
      return [ ProductionGrowth.from_row( row ) for row in cls.read_rows() ]


   @classmethod
   def write( cls, growth: list[ ProductionGrowth ] ) -> None:
      cls.write_rows( [ item.to_dict() for item in growth ] )
