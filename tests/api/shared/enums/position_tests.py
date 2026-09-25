from __future__ import annotations

from api.shared.enums.position import Position
from api.shared.enums.shared_enum_values import SharedEnumValues


def Test_Position_TestSharedJson_ExpectSingleSourceOfTruth() -> None:
   shared_members = SharedEnumValues.load_integers( 'position.json' )

   actual = {
      name: member.value
      for name, member in Position.__members__.items()
   }

   assert actual == shared_members


def Test_Position_TestListIndexing_ExpectElements() -> None:
   first = 'a'
   second = 'b'
   third = 'c'
   fourth = 'd'
   items = [ first, second, third, fourth ]

   assert items[ Position.FIRST ] == first
   assert items[ Position.SECOND ] == second
   assert items[ Position.THIRD ] == third
   assert items[ Position.FOURTH ] == fourth
   assert items[ Position.LAST ] == fourth
   assert items[ Position.SECOND_LAST ] == third
