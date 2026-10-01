from __future__ import annotations

from collections import defaultdict

from .pace_sample import PaceSample
from .pim_regression import PimRegression
from .pim_regression_model import PimRegressionModel
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason
from .weighted_pace_solver import WeightedPaceSolver


class PimRegressionFitter():
	NO_GAP_SCALE = 1.0


	@classmethod
	def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> PimRegressionModel:
		samples = cls._samples( seasons )
		consecutive = [ sample for sample in samples if not sample.gap() ]
		returning = [ sample for sample in samples if sample.gap() ]
		regressions = [
			cls._fit_width( consecutive, width )
			for width in range( 1, PriorYearBuilder.WIDTH + 1 )
		]
		regressions = [ regression for regression in regressions if regression is not None ]
		return PimRegressionModel(
			regressions=regressions,
			nhl_gap_scale=cls._gap_scale( regressions, returning ) )


	@classmethod
	def _samples( cls, seasons: list[ NhlSkaterSeason ] ) -> list[ PaceSample ]:
		by_player: dict[ int, list[ NhlSkaterSeason ] ] = defaultdict( list )

		for season in seasons:
			by_player[ season.player_id ].append( season )

		samples: list[ PaceSample ] = []

		for current in seasons:
			if current.games_played < PriorYear.MIN_GAMES:
				continue

			priors = PriorYearBuilder.build(
				by_player[ current.player_id ],
				[],
				Season.start_year( current.season_id ) )

			if priors:
				samples.append( PaceSample( current, priors ) )

		return samples


	@classmethod
	def _fit_width(
			cls,
			samples: list[ PaceSample ],
			width: int ) -> PimRegression | None:
		complete = [
			sample.truncated( width )
			for sample in samples
			if len( sample.priors ) >= width
		]

		if not complete:
			return None

		constant, weights = WeightedPaceSolver.solve(
			complete,
			PimRegression.prior_rate,
			lambda season: season.penalty_minutes_pace() )
		return PimRegression( constant, weights )


	@classmethod
	def _gap_scale(
			cls,
			regressions: list[ PimRegression ],
			samples: list[ PaceSample ] ) -> float:
		actual_total = 0.0
		predicted_total = 0.0

		for sample in samples:
			predicted = cls._regressed( regressions, sample.priors )

			if predicted is None:
				continue

			actual_total += sample.current.games_played * sample.current.penalty_minutes_pace()
			predicted_total += sample.current.games_played * predicted

		if not predicted_total:
			return PimRegressionFitter.NO_GAP_SCALE

		return actual_total / predicted_total


	@classmethod
	def _regressed(
			cls,
			regressions: list[ PimRegression ],
			priors: list[ PriorYear ] ) -> float | None:
		for width in range( len( priors ), 0, -1 ):
			for regression in regressions:
				if regression.covers( width ):
					return regression.pace( priors[ :width ] )

		return None

