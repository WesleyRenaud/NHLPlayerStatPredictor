from __future__ import annotations

from .depth_group import DepthGroup


class DressedFiller():
   @classmethod
   def fill(
         cls,
         present: list[ float ],
         extras: list[ float ],
         fills: list[ float ],
         count: int ) -> list[ float ]:
      dressed = []

      for claim in ( *present, *extras, *fills ):
         if len( dressed ) >= count:
            return dressed

         dressed.append( claim )

      return dressed


   @classmethod
   def spare_slot(
         cls,
         present: int,
         extras: int,
         group: DepthGroup ) -> int:
      used = min( extras, max( 0, group.dressed_count - present ) )
      return group.spare_slot + used
