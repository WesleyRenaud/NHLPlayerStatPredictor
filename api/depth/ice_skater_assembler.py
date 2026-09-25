from __future__ import annotations

from .club_ice import ClubIce
from .ice_claim import IceClaim
from .ice_skater import IceSkater
from .ice_usage import IceUsage
from ..skaters.roster_skater import RosterSkater
from ..skaters.team import Team


class IceSkaterAssembler():
   @classmethod
   def build(
         cls,
         roster: list[ RosterSkater ],
         ice_usages: dict[ int, IceUsage ],
         availabilities: dict[ int, float ],
         team_rates: dict[ Team, float ],
         ices_by_player: dict[ int, list[ ClubIce ] ] ) -> list[ IceSkater ]:
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
                  availability ) )
            continue

         skaters.append(
            IceSkater(
               row.player_id,
               row.player_name,
               row.position,
               row.team,
               IceClaim.resolve(
                  ices_by_player.get( row.player_id ) or [
                     ClubIce( usage.team, usage.games, usage.toi ) ],
                  team_rates ),
               usage.toi,
               availability ) )

      return skaters
