from __future__ import annotations

from ..paths import Paths
from .production_keep_fit import ProductionKeepFit
from .production_list_store import ProductionListStore


class ProductionKeepStore( ProductionListStore ):
   FILE_NAME = 'production_keep.json'
   FOLDER = Paths.RECENCY


   @classmethod
   def read( cls ) -> ProductionKeepFit:
      return ProductionKeepFit.from_row( cls.read_rows()[ 0 ] )


   @classmethod
   def write( cls, fit: ProductionKeepFit ) -> None:
      cls.write_rows( [ fit.to_dict() ] )
