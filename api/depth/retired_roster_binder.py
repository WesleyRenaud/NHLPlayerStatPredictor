from __future__ import annotations

from .ice_usage import IceUsage
from ..skaters.player_status import PlayerStatus
from ..skaters.roster_skater import RosterSkater


class RetiredRosterBinder():
   @classmethod
   def bind(
         cls,
         roster: list[ RosterSkater ],
         usages: dict[ int, IceUsage ],
         statuses: list[ PlayerStatus ],
         names: dict[ int, str ] ) -> list[ RosterSkater ]:
      added = []

      for player_id in cls.missing( roster, usages, statuses ):
         if player_id not in names:
            continue

         usage = usages[ player_id ]
         added.append(
            RosterSkater(
               player_id,
               names[ player_id ],
               usage.position,
               usage.team ) )

      return [ *roster, *added ]


   @classmethod
   def missing(
         cls,
         roster: list[ RosterSkater ],
         usages: dict[ int, IceUsage ],
         statuses: list[ PlayerStatus ] ) -> list[ int ]:
      seen = { row.player_id for row in roster }
      inactive = PlayerStatus.inactive_ids( statuses )
      return [
         player_id
         for player_id in usages
         if player_id not in seen and player_id in inactive
      ]
