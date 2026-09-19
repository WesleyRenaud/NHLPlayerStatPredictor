from __future__ import annotations

from api.skater_position import SkaterPosition


def Test_Center_TestCode_ExpectC() -> None:
   assert SkaterPosition.CENTER == 'C'


def Test_Defense_TestCode_ExpectD() -> None:
   assert SkaterPosition.DEFENSE == 'D'


def Test_LeftWing_TestCode_ExpectL() -> None:
   assert SkaterPosition.LEFT_WING == 'L'


def Test_RightWing_TestCode_ExpectR() -> None:
   assert SkaterPosition.RIGHT_WING == 'R'
