from __future__ import annotations

import json
from pathlib import Path

from ..paths import Paths
from .prospect_calibration_model import ProspectCalibrationModel


class ProspectCalibrationStore():
   FILE_NAME = 'prospect_calibration.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / Paths.PROSPECTS / cls.FILE_NAME


   @classmethod
   def write( cls, model: ProspectCalibrationModel ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text(
         json.dumps( model.to_dict(), indent=2 ) )


   @classmethod
   def read( cls ) -> ProspectCalibrationModel:
      payload = json.loads( cls.path().read_text() )
      return ProspectCalibrationModel.from_row( payload )
