from __future__ import annotations

from ..availability.availability_enumerator import AvailabilityEnumerator
from ..depth.depth_group import DepthGroup
from ..depth.dressed_points_builder import DressedPointsBuilder
from ..depth.slot_average import SlotAverage
from .teammate_skater import TeammateSkater


class TeammateMixer():
   @classmethod
   def expected(
         cls,
         regulars: list[ TeammateSkater ],
         extras: list[ TeammateSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> float:
      total = 0.0
      weight = 0.0

      for state in AvailabilityEnumerator.resolve( regulars ):
         total += state.share * DressedPointsBuilder.build(
            list( state.playing ),
            extras,
            slot_averages,
            group ).total
         weight += state.share

      return total / weight
