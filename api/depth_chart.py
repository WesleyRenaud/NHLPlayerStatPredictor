from __future__ import annotations

from dataclasses import dataclass

from .ice_skater import IceSkater
from .skater_group import SkaterGroup
from .team import Team
from .types import Types


@dataclass( frozen=True )
class DepthChart():
   team: Team
   regulars: list[ tuple[ IceSkater, float ] ]
   extras: list[ IceSkater ]
   games_out: list[ float ]
   skater_group: SkaterGroup


   def to_dict( self ) -> Types.JsonObject:
      return {
         'team': self.team.value,
         'skater_group': self.skater_group.value,
         'regulars': [
            self._member( skater, toi )
            for skater, toi in self.regulars
         ],
         'games_out': [ round( games, 1 ) for games in self.games_out ],
         'extras': [
            self._member( skater, skater.implied )
            for skater in self.extras
         ],
      }


   @staticmethod
   def _member( skater: IceSkater, toi: float ) -> Types.JsonObject:
      return {
         'player_id': skater.player_id,
         'player_name': skater.player_name,
         'toi': round( toi, 2 ),
         'implied': round( skater.implied, 2 ),
         'last_toi': None if skater.last_toi is None else round( skater.last_toi, 2 ),
         'availability': round( skater.availability, 3 ),
      }
