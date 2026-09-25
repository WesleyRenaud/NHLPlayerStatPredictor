from __future__ import annotations

from ..availability.games_share import GamesShare
from .depth_group import DepthGroup
from .ice_usage import IceUsage
from .last_toi import LastToi
from ..shared.enums.position import Position
from ..skaters.team import Team
from .slot_chosen_share import SlotChosenShare


class SlotChosenShareFitter():
   @classmethod
   def fit(
         cls,
         usages: dict[ int, IceUsage ],
         season_length: int,
         group: DepthGroup ) -> list[ SlotChosenShare ]:
      ranked = cls._ranked( usages )
      depth = 0

      for skaters in ranked:
         depth = max( depth, len( skaters ) )

      shares = []
      reference = 0.0

      for slot in range( 1, depth + 1 ):
         dress = []

         for skaters in ranked:
            if len( skaters ) < slot:
               continue

            player_id = skaters[ slot + Position.LAST ]
            dress.append(
               GamesShare.resolve( usages[ player_id ].games, season_length ) )

         if not dress:
            continue

         dress_share = sum( dress ) / len( dress )

         if not reference:
            reference = dress_share

         shares.append(
            SlotChosenShare(
               slot,
               group.skater_group,
               dress_share,
               GamesShare.FULL if not reference else min(
                  GamesShare.FULL,
                  dress_share / reference ) ) )

      return shares


   @classmethod
   def _ranked( cls, usages: dict[ int, IceUsage ] ) -> list[ list[ int ] ]:
      by_team: dict[ Team, list[ int ] ] = {}

      for player_id, usage in usages.items():
         by_team.setdefault( usage.team, [] ).append( player_id )

      for skaters in by_team.values():
         skaters.sort(
            key=lambda player_id: LastToi.key(
               player_id,
               usages[ player_id ].toi * usages[ player_id ].games ) )

      return list( by_team.values() )
