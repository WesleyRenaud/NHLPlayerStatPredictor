from __future__ import annotations

from collections.abc import Callable
from functools import partial

from .prior_year import PriorYear
from .production_coefficient_fitter import ProductionCoefficientFitter
from .production_growth import ProductionGrowth
from .production_history_predictor import ProductionHistoryPredictor
from .production_trajectory_change import ProductionTrajectoryChange
from .production_trajectory_fit import ProductionTrajectoryFit
from .production_trajectory_share import ProductionTrajectoryShare
from ..projections.prospect_eligibility import ProspectEligibility


class ProductionTrajectoryFitter():
   @classmethod
   def fit( cls, changes: list[ ProductionTrajectoryChange ] ) -> ProductionTrajectoryFit:
      """Fraction of a pace change still present the next season, after age growth."""
      move = cls._move( changes )

      if move is None:
         return ProductionTrajectoryFit.empty()

      loud = [ change for change in changes if change.relative() >= move ]
      by_age: list[ ProductionTrajectoryShare ] = []

      for age in sorted( { change.age for change in loud } ):
         group = [ change for change in loud if change.age == age ]
         rise = cls._share( [ change for change in group if change.latest_pace > change.prior_pace ] )
         drop = cls._share( [ change for change in group if change.latest_pace < change.prior_pace ] )

         if rise is None and drop is None:
            continue

         by_age.append( ProductionTrajectoryShare(
            age,
            None if rise is None else cls._bounded( rise ),
            None if drop is None else cls._bounded( drop ) ) )

      return ProductionTrajectoryFit( move, by_age )


   @classmethod
   def observe(
         cls,
         history_by_player: dict[ int, list[ PriorYear ] ],
         growth: list[ ProductionGrowth ] ) -> list[ ProductionTrajectoryChange ]:
      return cls._changes( history_by_player, growth, None )


   @classmethod
   def observe_debuts(
         cls,
         history_by_player: dict[ int, list[ PriorYear ] ],
         growth: list[ ProductionGrowth ] ) -> list[ ProductionTrajectoryChange ]:
      """Rises into a first NHL season from years still played outside the league."""
      return cls._changes( history_by_player, growth, cls._first_nhl_season )


   @classmethod
   def observe_short_nhl(
         cls,
         history_by_player: dict[ int, list[ PriorYear ] ],
         growth: list[ ProductionGrowth ] ) -> list[ ProductionTrajectoryChange ]:
      """Rises into a first NHL season from a year that already included a short NHL stint."""
      return cls._changes( history_by_player, growth, cls._short_nhl_season )


   @classmethod
   def observe_rookie(
         cls,
         history_by_player: dict[ int, list[ PriorYear ] ],
         growth: list[ ProductionGrowth ] ) -> list[ ProductionTrajectoryChange ]:
      """Changes through a first full NHL season and the NHL season after it."""
      return cls._changes( history_by_player, growth, cls._rookie_season )


   @classmethod
   def _changes(
         cls,
         history_by_player: dict[ int, list[ PriorYear ] ],
         growth: list[ ProductionGrowth ],
         include: Callable[ [ list[ PriorYear ], PriorYear, PriorYear ], bool ] | None ) -> list[ ProductionTrajectoryChange ]:
      lookup = partial( ProductionHistoryPredictor.coefficient, growth )
      changes: list[ ProductionTrajectoryChange ] = []

      for history in history_by_player.values():
         qualified = sorted(
            ( prior for prior in history if prior.games >= PriorYear.MIN_GAMES ),
            key=lambda prior: prior.year )

         for index in range( len( qualified ) - 2 ):
            prior, latest, following = qualified[ index : index + 3 ]

            if latest.year != prior.year + 1 or following.year != latest.year + 1:
               continue

            if include is not None and not include( qualified, latest, following ):
               continue

            change = cls._change( prior, latest, following, lookup )

            if change is not None:
               changes.append( change )

      return changes


   @classmethod
   def _first_nhl_season(
         cls,
         qualified: list[ PriorYear ],
         latest: PriorYear,
         following: PriorYear ) -> bool:
      played = sum( prior.nhl_games for prior in qualified if prior.year < following.year )
      return (
         following.nhl_games >= PriorYear.MIN_GAMES
         and ProspectEligibility.pre_nhl( latest.age, latest.nhl_games, played ) )


   @classmethod
   def _short_nhl_season(
         cls,
         qualified: list[ PriorYear ],
         latest: PriorYear,
         following: PriorYear ) -> bool:
      played = sum( prior.nhl_games for prior in qualified if prior.year < following.year )
      return (
         following.nhl_games >= PriorYear.MIN_GAMES
         and ProspectEligibility.short_nhl(
            latest.age, latest.nhl_games, latest.games - latest.nhl_games, played ) )


   @classmethod
   def _rookie_season(
         cls,
         qualified: list[ PriorYear ],
         latest: PriorYear,
         following: PriorYear ) -> bool:
      played = sum( prior.nhl_games for prior in qualified if prior.year < latest.year )
      return (
         following.nhl_games >= PriorYear.MIN_GAMES
         and ProspectEligibility.rookie_nhl( latest.age, latest.nhl_games, played ) )


   @classmethod
   def _change(
         cls,
         prior: PriorYear,
         latest: PriorYear,
         following: PriorYear,
         lookup: Callable[ [ int, int ], ProductionGrowth ] ) -> ProductionTrajectoryChange | None:
      prior_pace = prior.scoring.goals + prior.scoring.assists
      latest_pace = latest.scoring.goals + latest.scoring.assists
      following_pace = following.scoring.goals + following.scoring.assists
      multiplier = ProductionHistoryPredictor.multiplier(
         lookup, int( latest.age ), int( following.age ) )

      if multiplier <= 0.0 or latest_pace == prior_pace:
         return None

      return ProductionTrajectoryChange(
         int( latest.age ),
         prior_pace,
         latest_pace,
         following_pace,
         multiplier,
         min( prior.games, latest.games, following.games ) )


   @classmethod
   def _move( cls, changes: list[ ProductionTrajectoryChange ] ) -> float | None:
      # Smaller than the typical swing, and the kept fraction is mostly noise.
      relatives = sorted( change.relative() for change in changes if change.relative() > 0.0 )

      if not relatives:
         return None

      middle = len( relatives ) // 2

      if len( relatives ) % 2 == 1:
         return relatives[ middle ]

      return ( relatives[ middle - 1 ] + relatives[ middle ] ) / 2.0


   @classmethod
   def _share( cls, changes: list[ ProductionTrajectoryChange ] ) -> float | None:
      if len( changes ) < ProductionCoefficientFitter.MIN_SUPPORT:
         return None

      numerator = sum(
         change.games * ( change.following_pace / change.multiplier - change.prior_pace )
         for change in changes )
      denominator = sum(
         change.games * ( change.latest_pace - change.prior_pace ) for change in changes )

      if denominator == 0.0:
         return None

      return numerator / denominator


   @classmethod
   def _bounded( cls, share: float ) -> float:
      return min( 1.0, max( 0.0, share ) )
