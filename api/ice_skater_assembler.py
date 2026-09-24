from __future__ import annotations

from .ice_skater import IceSkater
from .ice_usage import IceUsage
from .roster_skater import RosterSkater


class IceSkaterAssembler():
   @classmethod
   def build(
         cls,
         roster: list[ RosterSkater ],
         ice_usages: dict[ int, IceUsage ],
         availabilities: dict[ int, float ] ) -> list[ IceSkater ]:
      skaters = []

      for row in roster:
         usage = ice_usages.get( row.player_id )
         availability = availabilities[ row.player_id ]

         if usage is None:
            skaters.append(
               IceSkater(
                  row.player_id,
                  row.player_name,
                  row.position,
                  row.team,
                  0.0,
                  None,
                  None,
                  False,
                  availability ) )
            continue

         skaters.append(
            IceSkater(
               row.player_id,
               row.player_name,
               row.position,
               row.team,
               usage.toi,
               usage.toi,
               usage.games,
               usage.team != row.team,
               availability ) )

      return skaters
