from __future__ import annotations

from dataclasses import replace

from .depth_group import DepthGroup
from .ice_skater import IceSkater
from .last_toi import LastToi
from .shared.enums.position import Position
from .slot_chosen_share import SlotChosenShare


class ChosenShareBinder():
   @classmethod
   def bind(
         cls,
         skaters: list[ IceSkater ],
         shares: list[ SlotChosenShare ],
         group: DepthGroup ) -> list[ IceSkater ]:
      by_slot = {
         share.slot: share.chosen
         for share in shares
         if share.skater_group is group.skater_group
      }
      ranked = sorted(
         skaters,
         key=lambda skater: LastToi.key( skater.player_id, skater.implied ) )
      bound = {}

      for index, skater in enumerate( ranked ):
         bound[ skater.player_id ] = replace(
            skater,
            availability=skater.availability * by_slot[ index - Position.LAST ] )

      return [ bound[ skater.player_id ] for skater in skaters ]
