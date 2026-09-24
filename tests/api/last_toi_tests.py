from __future__ import annotations

from api.last_toi import LastToi


def Test_Key_TestToi_ExpectNegativeThenId() -> None:
   assert LastToi.key( 7, 24.1 ) == ( -24.1, 7 )
