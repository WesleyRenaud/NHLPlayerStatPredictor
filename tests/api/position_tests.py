from __future__ import annotations

from api.position import Position


def Test_Members_TestValues_ExpectUniqueInts() -> None:
   values = [ member.value for member in Position ]
   assert values
   assert len( values ) == len( set( values ) )

   for member in Position:
      assert isinstance( member.value, int )
      assert Position( member.value ) is member


def Test_Index_TestSequence_ExpectMembersSelectItems() -> None:
   items = [ 'a', 'b', 'c', 'd' ]
   assert items[ Position.FIRST ] == 'a'
   assert items[ Position.SECOND ] == 'b'
   assert items[ Position.THIRD ] == 'c'
   assert items[ Position.FOURTH ] == 'd'
   assert items[ Position.LAST ] == 'd'
   assert items[ Position.SECOND_LAST ] == 'c'
