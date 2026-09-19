from __future__ import annotations

from api.position import Position


def Test_First_TestIndex_ExpectZero() -> None:
   assert Position.FIRST == 0


def Test_Second_TestIndex_ExpectOne() -> None:
   assert Position.SECOND == 1


def Test_SecondLast_TestIndex_ExpectNegativeTwo() -> None:
   assert Position.SECOND_LAST == -2
