from __future__ import annotations

from .depth_group import DepthGroup
from .dressed_lineup import DressedLineup
from .ice_skater import IceSkater
from .slot_average import SlotAverage
from .slot_filler import SlotFiller


class DressedLineupBuilder():
   @classmethod
   def build(
         cls,
         present: list[ IceSkater ],
         extras: list[ IceSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> DressedLineup:
      dressed = []
      for skater in present:
         if cls._complete( dressed, group ):
            break

         dressed.append( skater.implied )

      next_slot = group.spare_slot
      for extra in extras:
         if cls._complete( dressed, group ):
            break

         dressed.append( extra.implied )
         next_slot += 1

      while not cls._complete( dressed, group ):
         average = SlotFiller.average( slot_averages, next_slot )

         if average is None:
            break

         dressed.append( average.toi )
         next_slot += 1

      return DressedLineup( dressed )


   @staticmethod
   def _complete(
         dressed: list[ float ],
         group: DepthGroup ) -> bool:
      return len( dressed ) >= group.dressed_count
