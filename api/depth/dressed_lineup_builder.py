from __future__ import annotations

from .depth_group import DepthGroup
from .dressed_filler import DressedFiller
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
      claims = [ skater.implied for skater in present ]
      extra_claims = [ skater.implied for skater in extras ]
      return DressedLineup(
         DressedFiller.fill(
            claims,
            extra_claims,
            [ average.toi for average in SlotFiller.spare_averages(
               slot_averages,
               DressedFiller.spare_slot(
                  len( claims ),
                  len( extra_claims ),
                  group ) ) ],
            group.dressed_count ) )
