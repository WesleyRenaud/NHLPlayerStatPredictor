from __future__ import annotations

from .ice_usage import IceUsage
from .last_toi import LastToi
from ..projections.season_pace import SeasonPace
from ..shared.enums.position import Position
from ..skaters.team import Team
from .slot_average import SlotAverage


class SlotAverageFitter():
   @classmethod
   def fit(
         cls,
         usages: dict[ int, IceUsage ],
         paces: dict[ int, SeasonPace ],
         first_slot: int ) -> list[ SlotAverage ]:
      start = first_slot
      ranked = cls._ranked( usages )
      depth = max( ( len( skaters ) for skaters in ranked.values() ), default=0 )
      averages = []

      for slot in range( start, depth + 1 ):
         toi = []
         goals = []
         assists = []

         for skaters in ranked.values():
            if len( skaters ) < slot:
               continue

            player_id = skaters[ slot + Position.LAST ]
            usage = usages[ player_id ]
            pace = paces.get( player_id, SeasonPace( 0.0, 0.0 ) )
            toi.append( usage.toi )
            goals.append( pace.goals )
            assists.append( pace.assists )

         if not toi:
            continue

         count = len( toi )
         averages.append(
            SlotAverage(
               slot,
               sum( toi ) / count,
               sum( goals ) / count,
               sum( assists ) / count ) )

      return averages


   @classmethod
   def _ranked(
         cls,
         usages: dict[ int, IceUsage ] ) -> dict[ Team, list[ int ] ]:
      by_team: dict[ Team, list[ int ] ] = {}

      for player_id, usage in usages.items():
         by_team.setdefault( usage.team, [] ).append( player_id )

      for team, skaters in by_team.items():
         skaters.sort(
            key=lambda player_id: LastToi.key(
               player_id,
               usages[ player_id ].toi ) )
         by_team[ team ] = skaters

      return by_team
