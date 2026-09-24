from __future__ import annotations

from .depth_group import DepthGroup
from .games_share import GamesShare
from .ice_skater import IceSkater
from .league_filler import LeagueFiller
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
   def spare_averages(
         cls,
         slots: list[ SlotAverage ],
         first_spare: int ) -> list[ SlotAverage ]:
      averages = []
      slot = first_spare
      average = cls.average( slots, slot )

      while average is not None:
         averages.append( average )
         slot += 1
         average = cls.average( slots, slot )

      return averages


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
         LeagueFiller.player_id( slot ),
         f'League { slot }{ group.label }',
         group.skater_group.position,
         team,
         average.toi,
         average.toi,
         GamesShare.FULL )


   @classmethod
   def pad_extras(
         cls,
         extras: list[ IceSkater ],
         slots: list[ SlotAverage ],
         group: DepthGroup,
         team: Team ) -> list[ IceSkater ]:
      filled = list( extras )
      needed = group.extra_count - len( filled )

      for average in cls.spare_averages(
            slots,
            group.spare_slot + len( filled ) )[ :needed ]:
         filled.append( cls.skater( slots, average.slot, group, team ) )

      return filled
