from __future__ import annotations

from .production_list_store import ProductionListStore
from .production_trajectory_fit import ProductionTrajectoryFit
from .production_trajectory_share import ProductionTrajectoryShare


class ProductionTrajectoryStore( ProductionListStore ):
   FILE_NAME = 'production_trajectory.json'


   @classmethod
   def read( cls ) -> ProductionTrajectoryFit:
      rows = cls.read_rows()

      if not rows:
         return ProductionTrajectoryFit.empty()

      return ProductionTrajectoryFit(
         float( rows[ 0 ][ 'move' ] ),
         [ ProductionTrajectoryShare.from_row( row ) for row in rows ] )


   @classmethod
   def write( cls, fit: ProductionTrajectoryFit ) -> None:
      cls.write_rows( [
         { **share.to_dict(), 'move': fit.move }
         for share in fit.by_age
      ] )
