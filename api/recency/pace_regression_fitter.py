from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from .age_band import AgeBand
from ..aging.league_factor import LeagueFactor
from .pace_regression import PaceRegression
from .pace_regression_model import PaceRegressionModel
from .pace_regression_predictor import PaceRegressionPredictor
from .pace_sample import PaceSample
from .prior_source import PriorSource
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from ..projections.scoring_paces import ScoringPaces
from ..projections.season_pace import SeasonPace
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_season import SkaterSeason
from .weighted_pace_solver import WeightedPaceSolver


class PaceRegressionFitter():
   NHL_AGE_BANDS = [
      AgeBand( 18, 22 ),
      AgeBand( 23, 24 ),
      AgeBand( 25, 26 ),
      AgeBand( 27, 28 ),
      AgeBand( 29, 30 ),
      AgeBand( 31, 32 ),
      AgeBand( 33, 34 ),
      AgeBand( 35, 45 ),
   ]
   TRANSLATED_AGE_BANDS = [
      AgeBand( 17, 19 ),
      AgeBand( 20, 21 ),
      AgeBand( 22, 23 ),
      AgeBand( 24, 40 ),
   ]
   NO_DISCOUNT = 1.0
   NO_PLAYOFF_WEIGHT = 0.0


   @classmethod
   def fit(
         cls,
         nhl_seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> PaceRegressionModel:
      samples = cls._samples( nhl_seasons, other_seasons, factors )
      regressions = cls._regressions( [ sample for sample in samples if not sample.gap() ] )
      nhl = [ sample for sample in samples if sample.source() == PriorSource.NHL ]
      returning = [ sample for sample in nhl if sample.gap() ]
      consecutive = [ sample for sample in nhl if not sample.gap() ]
      return PaceRegressionModel(
         regressions=regressions,
         nhl_gap_goals=cls._gap_scale(
            regressions,
            returning,
            lambda pace: pace.goals,
            lambda season: season.g_pace ),
         nhl_gap_assists=cls._gap_scale(
            regressions,
            returning,
            lambda pace: pace.assists,
            lambda season: season.a_pace ),
         nhl_gap_power_play_goals=cls._gap_scale(
            regressions,
            returning,
            lambda pace: pace.power_play_goals,
            lambda season: season.power_play_pace().goals ),
         nhl_gap_power_play_assists=cls._gap_scale(
            regressions,
            returning,
            lambda pace: pace.power_play_assists,
            lambda season: season.power_play_pace().assists ),
         playoff_goal_weight=cls._playoff_weight(
            regressions,
            consecutive,
            lambda pace: pace.goals,
            lambda season: season.g_pace ),
         playoff_assist_weight=cls._playoff_weight(
            regressions,
            consecutive,
            lambda pace: pace.assists,
            lambda season: season.a_pace ),
         )


   @classmethod
   def _samples(
         cls,
         nhl_seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> list[ PaceSample ]:
      by_player: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )

      for season in [ *nhl_seasons, *other_seasons ]:
         by_player[ season.player_id ].append( season )

      samples: list[ PaceSample ] = []

      for current in nhl_seasons:
         if current.games_played < PriorYear.MIN_GAMES:
            continue

         priors = PriorYearBuilder.build(
            by_player[ current.player_id ],
            factors,
            Season.start_year( current.season_id ) )

         if priors:
            samples.append( PaceSample( current, priors ) )

      return samples


   @classmethod
   def _regressions( cls, samples: list[ PaceSample ] ) -> list[ PaceRegression ]:
      regressions: list[ PaceRegression ] = []

      for source in PriorSource:
         sourced = [ sample for sample in samples if sample.source() == source ]

         for band in cls._age_bands( source ):
            banded = [ sample for sample in sourced if band.contains( sample.target_age() ) ]

            for width in range( 1, PriorYearBuilder.WIDTH + 1 ):
               regression = cls._fit_width( banded, source, band, width )

               if regression is not None:
                  regressions.append( regression )

      return regressions


   @classmethod
   def _age_bands( cls, source: PriorSource ) -> list[ AgeBand ]:
      if source == PriorSource.NHL:
         return PaceRegressionFitter.NHL_AGE_BANDS

      return PaceRegressionFitter.TRANSLATED_AGE_BANDS


   @classmethod
   def _fit_width(
         cls,
         banded: list[ PaceSample ],
         source: PriorSource,
         band: AgeBand,
         width: int ) -> PaceRegression | None:
      complete = [
         sample.truncated( width )
         for sample in banded
         if len( sample.priors ) >= width
      ]

      if not complete:
         return None

      goal_constant, goal_weights = WeightedPaceSolver.solve(
         complete,
         lambda prior: prior.pace.goals,
         lambda season: season.g_pace )
      assist_constant, assist_weights = WeightedPaceSolver.solve(
         complete,
         lambda prior: prior.pace.assists,
         lambda season: season.a_pace )
      power_play_goal_constant, power_play_goal_weights = WeightedPaceSolver.solve(
         complete,
         lambda prior: prior.power_play_pace.goals,
         lambda season: season.power_play_pace().goals )
      power_play_assist_constant, power_play_assist_weights = WeightedPaceSolver.solve(
         complete,
         lambda prior: prior.power_play_pace.assists,
         lambda season: season.power_play_pace().assists )
      return PaceRegression(
         source=source,
         band=band,
         goal_constant=goal_constant,
         goal_weights=goal_weights,
         assist_constant=assist_constant,
         assist_weights=assist_weights,
         power_play_goal_constant=power_play_goal_constant,
         power_play_goal_weights=power_play_goal_weights,
         power_play_assist_constant=power_play_assist_constant,
         power_play_assist_weights=power_play_assist_weights )


   @classmethod
   def _playoff_weight(
         cls,
         regressions: list[ PaceRegression ],
         samples: list[ PaceSample ],
         predicted: Callable[ [ SeasonPace ], float ],
         actual: Callable[ [ NhlSkaterSeason ], float ] ) -> float:
      surplus_products = 0.0
      residual_products = 0.0

      for sample in samples:
         regressed_paces = PaceRegressionPredictor.regressed_paces(
            regressions,
            sample.priors )

         if regressed_paces is None:
            continue

         games = sample.current.games_played
         surplus = predicted( sample.priors[ Position.FIRST ].playoff_surplus )
         surplus_products += games * surplus * surplus
         residual_products += games * surplus * (
            actual( sample.current )
            - predicted( regressed_paces.season_pace() ) )

      if not surplus_products:
         return PaceRegressionFitter.NO_PLAYOFF_WEIGHT

      return residual_products / surplus_products


   @classmethod
   def _gap_scale(
         cls,
         regressions: list[ PaceRegression ],
         samples: list[ PaceSample ],
         predicted: Callable[ [ ScoringPaces ], float ],
         actual: Callable[ [ NhlSkaterSeason ], float ] ) -> float:
      actual_total = 0.0
      predicted_total = 0.0

      for sample in samples:
         regressed_paces = PaceRegressionPredictor.regressed_paces(
            regressions,
            sample.priors )

         if regressed_paces is None:
            continue

         actual_total += sample.current.games_played * actual( sample.current )
         predicted_total += sample.current.games_played * predicted( regressed_paces )

      if not predicted_total:
         return PaceRegressionFitter.NO_DISCOUNT

      return actual_total / predicted_total
