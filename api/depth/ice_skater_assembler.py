from __future__ import annotations

from .ice_claim import IceClaim
from .ice_skater import IceSkater
from ..skaters.roster_skater import RosterSkater
from ..skaters.team import Team
from .usable_nhl_ice import UsableNhlIce


class IceSkaterAssembler():
   @classmethod
   def build(
         cls,
         roster: list[ RosterSkater ],
         ices_by_player: dict[ int, UsableNhlIce | None ],
         availabilities: dict[ int, float ],
         team_rates: dict[ Team, float ] ) -> list[ IceSkater ]:
      skaters = []

      for row in roster:
         ice = ices_by_player.get( row.player_id )
         availability = availabilities[ row.player_id ]

         if ice is None:
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
               IceClaim.resolve( ice.clubs, team_rates ),
               ice.toi,
               availability ) )

      return skaters
