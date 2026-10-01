from __future__ import annotations

from dataclasses import dataclass

from .prior_year import PriorYear


@dataclass( frozen=True )
class PimRegression():
	constant: float
	weights: list[ float ]


	def covers( self, width: int ) -> bool:
		return len( self.weights ) == width


	def pace( self, priors: list[ PriorYear ] ) -> float:
		return self.constant + sum(
			weight * self.prior_rate( prior )
			for weight, prior in zip( self.weights, priors ) )


	@staticmethod
	def prior_rate( prior: PriorYear ) -> float:
		if prior.pim_pace is None:
			raise ValueError( 'Penalty-minute pace is unavailable' )

		return prior.pim_pace


	@classmethod
	def from_row( cls, row: dict[ str, object ] ) -> PimRegression:
		return cls(
			constant=float( row[ 'constant' ] ),
			weights=[ float( weight ) for weight in row[ 'weights' ] ] )


	def to_dict( self ) -> dict[ str, float | list[ float ] ]:
		return {
			'constant': self.constant,
			'weights': self.weights,
		}

