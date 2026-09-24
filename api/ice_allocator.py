from __future__ import annotations

from .availability_enumerator import AvailabilityEnumerator
from .depth_group import DepthGroup
from .dressed_lineup_builder import DressedLineupBuilder
from .ice_skater import IceSkater
from .slot_average import SlotAverage


class IceAllocator():
   @classmethod
   def project(
         cls,
         regulars: list[ IceSkater ],
         extras: list[ IceSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> list[ tuple[ IceSkater, float ] ]:
      return [
         (
            skater,
            cls._mix( skater, regulars, extras, slot_averages, group ) )
         for skater in regulars
      ]


   @classmethod
   def _mix(
         cls,
         skater: IceSkater,
         regulars: list[ IceSkater ],
         extras: list[ IceSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> float:
      others = [
         other
         for other in regulars
         if other.player_id != skater.player_id
      ]
      total = 0.0
      weight = 0.0

      for state in AvailabilityEnumerator.resolve( others ):
         denom = DressedLineupBuilder.build(
            [ skater, *state.playing ],
            extras,
            slot_averages,
            group ).implied
         total += state.share * group.ice_minutes * skater.implied / denom
         weight += state.share

      return total / weight
