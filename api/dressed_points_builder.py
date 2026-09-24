from __future__ import annotations

from .depth_group import DepthGroup
from .dressed_points import DressedPoints
from .slot_average import SlotAverage
from .slot_filler import SlotFiller
from .teammate_skater import TeammateSkater


class DressedPointsBuilder():
   @classmethod
   def build(
         cls,
         present: list[ TeammateSkater ],
         extras: list[ TeammateSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> DressedPoints:
      dressed = []
      for skater in present:
         if cls._complete( dressed, group ):
            break

         dressed.append( skater.contribution )

      next_slot = group.spare_slot
      for extra in extras:
         if cls._complete( dressed, group ):
            break

         dressed.append( extra.contribution )
         next_slot += 1

      while not cls._complete( dressed, group ):
         average = SlotFiller.average( slot_averages, next_slot )

         if average is None:
            break

         dressed.append( average.contribution )
         next_slot += 1

      return DressedPoints( dressed )


   @staticmethod
   def _complete(
         dressed: list[ float ],
         group: DepthGroup ) -> bool:
      return len( dressed ) >= group.dressed_count
