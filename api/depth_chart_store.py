from __future__ import annotations

import json
from pathlib import Path

from .depth_chart import DepthChart
from .paths import Paths


class DepthChartStore():
   FILE_NAME = 'depth_charts.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, charts: list[ DepthChart ] ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text(
         json.dumps( [ chart.to_dict() for chart in charts ], indent=2 ) )


   @classmethod
   def read( cls ) -> list[ dict[ str, object ] ]:
      return json.loads( cls.path().read_text() )
