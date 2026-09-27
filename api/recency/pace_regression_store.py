from __future__ import annotations

import json
from pathlib import Path

from .pace_regression_model import PaceRegressionModel
from ..paths import Paths


class PaceRegressionStore():
   FILE_NAME = 'pace_regressions.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, model: PaceRegressionModel ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text( json.dumps( model.to_dict(), indent=2 ) )


   @classmethod
   def read( cls ) -> PaceRegressionModel:
      return PaceRegressionModel.from_row( json.loads( cls.path().read_text() ) )
