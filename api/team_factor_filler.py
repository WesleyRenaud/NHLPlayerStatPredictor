from __future__ import annotations

from .games_share import GamesShare
from .league_filler import LeagueFiller
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

      for average in SlotFiller.spare_averages(
            slots,
            first_spare + len( filled ) ):
         filled.append(
            TeammateSkater(
               LeagueFiller.player_id( average.slot ),
               average.contribution,
               GamesShare.FULL,
               None ) )

      return filled


   @classmethod
   def extra_pace(
         cls,
         player_id: int,
         paces: dict[ int, float ],
         slots: list[ SlotAverage ] ) -> float:
      if player_id in paces:
         return paces[ player_id ]

      if LeagueFiller.is_filler( player_id ):
         average = SlotFiller.average(
            slots,
            LeagueFiller.slot( player_id ) )
         return average.contribution

      return 0.0
