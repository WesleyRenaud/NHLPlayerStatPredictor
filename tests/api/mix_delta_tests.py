from __future__ import annotations

from api.mix_delta import MixDelta


def Test_Resolve_TestPrior_ExpectHealthyPlusChange() -> None:
   assert MixDelta.resolve( 22.0, 21.0, 20.0 ) == 21.0
