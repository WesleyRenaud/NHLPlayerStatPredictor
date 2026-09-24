from __future__ import annotations

from dataclasses import replace

from .ice_skater import IceSkater
from .last_toi import LastToi


class AvailabilityBinder():
   @classmethod
   def bind(
         cls,
         skaters: list[ IceSkater ],
         shares: list[ float ] ) -> list[ IceSkater ]:
      ranked = sorted(
         skaters,
         key=lambda skater: LastToi.key( skater.player_id, skater.implied ) )
      bound = {}

      for index, skater in enumerate( ranked ):
         bound[ skater.player_id ] = replace(
            skater,
            availability=shares[ index ] )

      return [ bound[ skater.player_id ] for skater in skaters ]
