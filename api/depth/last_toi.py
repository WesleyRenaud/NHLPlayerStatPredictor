from __future__ import annotations


class LastToi():
   @classmethod
   def key( cls, player_id: int, toi: float ) -> tuple[ float, int ]:
      return ( -toi, player_id )
