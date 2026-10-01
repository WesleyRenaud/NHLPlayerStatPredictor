from __future__ import annotations

from .pim_regression import PimRegression
from .pim_regression_model import PimRegressionModel
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason


class PimRegressionPredictor():
	@classmethod
	def pace(
			cls,
			model: PimRegressionModel,
			seasons: list[ NhlSkaterSeason ],
			target_season_id: int ) -> float | None:
		year = Season.start_year( target_season_id )
		priors = PriorYearBuilder.build( seasons, [], year )
		regression = cls._regression( model.regressions, priors )

		if regression is None:
			return None

		pace = regression.pace( priors[ :len( regression.weights ) ] )
		latest = priors[ Position.FIRST ]

		if latest.gap_before( year ):
			return pace * model.nhl_gap_scale

		return pace


	@classmethod
	def _regression(
			cls,
			regressions: list[ PimRegression ],
			priors: list[ PriorYear ] ) -> PimRegression | None:
		for width in range( len( priors ), 0, -1 ):
			for regression in regressions:
				if regression.covers( width ):
					return regression

		return None

