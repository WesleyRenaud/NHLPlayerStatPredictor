from __future__ import annotations

from .depth_group import DepthGroup
from .games_share import GamesShare
from .ice_skater import IceSkater
from .slot_average import SlotAverage
from .team import Team


class SlotFiller():
   @classmethod
   def average(
         cls,
         slots: list[ SlotAverage ],
         slot: int ) -> SlotAverage | None:
      for row in slots:
         if row.slot == slot:
            return row

      return None


   @classmethod
   def implied( cls, slots: list[ SlotAverage ], slot: int ) -> float:
      return cls.average( slots, slot ).toi


   @classmethod
   def contribution( cls, slots: list[ SlotAverage ], slot: int ) -> float:
      return cls.average( slots, slot ).contribution


   @classmethod
   def skater(
         cls,
         slots: list[ SlotAverage ],
         slot: int,
         group: DepthGroup,
         team: Team ) -> IceSkater:
      average = cls.average( slots, slot )
      return IceSkater(
         -slot,
         f'League { slot }{ group.label }',
         group.skater_group.position,
         team,
         average.toi,
         average.toi,
         None,
         False,
         GamesShare.FULL )


   @classmethod
   def pad_extras(
         cls,
         extras: list[ IceSkater ],
         slots: list[ SlotAverage ],
         group: DepthGroup,
         team: Team ) -> list[ IceSkater ]:
      filled = list( extras )

      while len( filled ) < group.extra_count:
         filled.append(
            cls.skater(
               slots,
               group.spare_slot + len( filled ),
               group,
               team ) )

      return filled
