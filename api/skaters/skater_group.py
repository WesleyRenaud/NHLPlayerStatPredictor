from __future__ import annotations

from enum import Enum

from .skater_position import SkaterPosition


class SkaterGroup( str, Enum ):
   FORWARD = 'F'
   DEFENSE = 'D'


   @property
   def positions( self ) -> set[ SkaterPosition ]:
      if self is SkaterGroup.DEFENSE:
         return { SkaterPosition.DEFENSE }

      return {
         SkaterPosition.CENTER,
         SkaterPosition.FORWARD,
         SkaterPosition.LEFT_WING,
         SkaterPosition.RIGHT_WING,
      }


   @property
   def position( self ) -> SkaterPosition:
      if self is SkaterGroup.DEFENSE:
         return SkaterPosition.DEFENSE

      return SkaterPosition.FORWARD


   @classmethod
   def of( cls, position: SkaterPosition ) -> SkaterGroup:
      if position is SkaterPosition.DEFENSE:
         return cls.DEFENSE

      return cls.FORWARD
