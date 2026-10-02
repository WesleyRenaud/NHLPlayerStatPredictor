from __future__ import annotations

import json
from pathlib import Path

from ..paths import Paths
from .pim_regression_model import PimRegressionModel


class PimRegressionStore():
	FILE_NAME = 'pim_regressions.json'


	@classmethod
	def path( cls ) -> Path:
		return Paths.PROCESSED_DIR / cls.FILE_NAME


	@classmethod
	def write( cls, model: PimRegressionModel ) -> None:
		path = cls.path()
		path.parent.mkdir( parents=True, exist_ok=True )
		path.write_text( json.dumps( model.to_dict(), indent=2 ) )


	@classmethod
	def read( cls ) -> PimRegressionModel:
		row = json.loads( cls.path().read_text() )

		return PimRegressionModel.from_row( row )
