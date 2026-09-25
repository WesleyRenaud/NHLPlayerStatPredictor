from __future__ import annotations

from api.depth.last_toi import LastToi


def Test_Key_TestToi_ExpectNegativeThenId() -> None:
   player_id = 7
   toi = 24.1

   key = LastToi.key( player_id, toi )

   assert key == ( -toi, player_id )
