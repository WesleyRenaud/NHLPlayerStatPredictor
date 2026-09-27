from __future__ import annotations

from dataclasses import dataclass

from .prior_source import PriorSource
from .prior_year import PriorYear
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason


@dataclass( frozen=True )
class PaceSample():
   current: NhlSkaterSeason
   priors: list[ PriorYear ]


   def source( self ) -> PriorSource:
      return self.priors[ Position.FIRST ].source()


   def target_age( self ) -> int:
      return self.priors[ Position.FIRST ].target_age()


   def gap( self ) -> int:
      return self.priors[ Position.FIRST ].gap_before(
         Season.start_year( self.current.season_id ) )


   def truncated( self, width: int ) -> PaceSample:
      return PaceSample( self.current, self.priors[ :width ] )
