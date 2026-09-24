from __future__ import annotations

from .depth_core import DepthCore
from .depth_group import DepthGroup
from .ice_skater import IceSkater
from .last_toi import LastToi
from .shared.enums.position import Position
from .slot_average import SlotAverage
from .slot_filler import SlotFiller


class DepthCoreBuilder():
   @classmethod
   def build(
         cls,
         skaters: list[ IceSkater ],
         group: DepthGroup,
         slot_averages: list[ SlotAverage ] ) -> DepthCore:
      ranked = sorted(
         skaters,
         key=lambda skater: LastToi.key( skater.player_id, skater.implied ) )
      count = group.dressed_count
      return DepthCore(
         regulars=ranked[ : count ],
         extras=SlotFiller.pad_extras(
            ranked[ count: count + group.extra_count ],
            slot_averages,
            group,
            skaters[ Position.FIRST ].team ) )
