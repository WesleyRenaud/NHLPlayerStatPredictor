from __future__ import annotations

from dataclasses import dataclass

from .pim_regression import PimRegression
from ..types import Types


@dataclass( frozen=True )
class PimRegressionModel():
	regressions: list[ PimRegression ]
	nhl_gap_scale: float


	@classmethod
	def from_row( cls, row: Types.JsonObject ) -> PimRegressionModel:
		return cls(
			regressions=[ PimRegression.from_row( item ) for item in row[ 'regressions' ] ],
			nhl_gap_scale=float( row[ 'nhl_gap_scale' ] ) )


	def to_dict( self ) -> dict[ str, float | list[ dict[ str, float | list[ float ] ] ] ]:
		return {
			'regressions': [ regression.to_dict() for regression in self.regressions ],
			'nhl_gap_scale': self.nhl_gap_scale,
		}

