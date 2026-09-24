from __future__ import annotations

from .games_share import GamesShare
from .slot_average import SlotAverage
from .slot_filler import SlotFiller
from .teammate_skater import TeammateSkater


class TeamFactorFiller():
   @classmethod
   def pad(
         cls,
         extras: list[ TeammateSkater ],
         slots: list[ SlotAverage ],
         first_spare: int ) -> list[ TeammateSkater ]:
      filled = list( extras )
      average = SlotFiller.average( slots, first_spare + len( filled ) )

      while average is not None:
         filled.append(
            TeammateSkater(
               -average.slot,
               average.contribution,
               GamesShare.FULL,
               None ) )
         average = SlotFiller.average( slots, first_spare + len( filled ) )

      return filled


   @classmethod
   def extra_pace(
         cls,
         player_id: int,
         paces: dict[ int, float ],
         slots: list[ SlotAverage ] ) -> float:
      if player_id in paces:
         return paces[ player_id ]

      average = SlotFiller.average( slots, -player_id )

      if average is None:
         return 0.0

      return average.contribution
