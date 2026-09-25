from __future__ import annotations


class LeagueFiller():
   @classmethod
   def player_id( cls, slot: int ) -> int:
      return -slot


   @classmethod
   def slot( cls, player_id: int ) -> int:
      return -player_id


   @classmethod
   def is_filler( cls, player_id: int ) -> bool:
      return player_id < 0
