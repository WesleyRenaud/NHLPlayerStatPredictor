from __future__ import annotations

from ..skaters.player_status import PlayerStatus


class RetiredAvailabilityBinder():
   @classmethod
   def bind(
         cls,
         availabilities: dict[ int, float ],
         statuses: list[ PlayerStatus ] ) -> dict[ int, float ]:
      inactive = PlayerStatus.inactive_ids( statuses )
      return {
         player_id: 0.0 if player_id in inactive else share
         for player_id, share in availabilities.items()
      }
