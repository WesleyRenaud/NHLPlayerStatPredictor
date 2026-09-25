from __future__ import annotations

from .depth_group import DepthGroup
from .dressed_filler import DressedFiller
from .dressed_points import DressedPoints
from .slot_average import SlotAverage
from .slot_filler import SlotFiller
from ..team_factor.teammate_skater import TeammateSkater


class DressedPointsBuilder():
   @classmethod
   def build(
         cls,
         present: list[ TeammateSkater ],
         extras: list[ TeammateSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> DressedPoints:
      claims = [ skater.contribution for skater in present ]
      extra_claims = [ skater.contribution for skater in extras ]
      return DressedPoints(
         DressedFiller.fill(
            claims,
            extra_claims,
            [ average.contribution for average in SlotFiller.spare_averages(
               slot_averages,
               DressedFiller.spare_slot(
                  len( claims ),
                  len( extra_claims ),
                  group ) ) ],
            group.dressed_count ) )
