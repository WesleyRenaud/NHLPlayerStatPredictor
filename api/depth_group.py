from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .last_core import LastCore
from .projections.nhl_lineup_selector import NhlLineupSelector
from .roster_skater import RosterSkater
from .skater_group import SkaterGroup
from .skater_position import SkaterPosition
from .team import Team


@dataclass( frozen=True )
class DepthGroup():
   FORWARD_ICE_MINUTES: ClassVar[ float ] = 180.0
   DEFENSE_ICE_MINUTES: ClassVar[ float ] = 117.0


   dressed_count: int
   spare_slot: int
   extra_count: int
   ice_minutes: float
   skater_group: SkaterGroup


   @property
   def roster_count( self ) -> int:
      return self.dressed_count + self.extra_count


   @property
   def label( self ) -> str:
      return self.skater_group.value


   @property
   def positions( self ) -> set[ SkaterPosition ]:
      return self.skater_group.positions


   def contains( self, position: SkaterPosition ) -> bool:
      return SkaterGroup.of( position ) is self.skater_group


   def skaters(
         self,
         roster: list[ RosterSkater ],
         team: Team ) -> list[ RosterSkater ]:
      return [
         row
         for row in roster
         if row.team == team and self.contains( row.position )
      ]


   @classmethod
   def forwards( cls ) -> DepthGroup:
      return cls(
         dressed_count=NhlLineupSelector.DRESSED_FORWARDS,
         spare_slot=NhlLineupSelector.DRESSED_FORWARDS + 1,
         extra_count=LastCore.EXTRA,
         ice_minutes=cls.FORWARD_ICE_MINUTES,
         skater_group=SkaterGroup.FORWARD )


   @classmethod
   def defense( cls ) -> DepthGroup:
      return cls(
         dressed_count=NhlLineupSelector.DRESSED_DEFENSE,
         spare_slot=NhlLineupSelector.DRESSED_DEFENSE + 1,
         extra_count=LastCore.EXTRA,
         ice_minutes=cls.DEFENSE_ICE_MINUTES,
         skater_group=SkaterGroup.DEFENSE )
