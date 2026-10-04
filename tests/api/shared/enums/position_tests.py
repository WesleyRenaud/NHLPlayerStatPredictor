from __future__ import annotations

import runpy
from unittest.mock import Mock

import pytest

import api.shared.enums.position as position_module
from api.shared.enums.position import Position
from api.shared.enums.shared_enum_values import SharedEnumValues


def Test_Position_TestMockedMembers_ExpectLoadedEnum( monkeypatch: pytest.MonkeyPatch ) -> None:
   shared_members = { 'TEST_FIRST': 0, 'TEST_LAST': -1 }
   loader = Mock( return_value=shared_members )
   monkeypatch.setattr( SharedEnumValues, 'load_integers', loader )

   namespace = runpy.run_path(
      position_module.__file__, run_name='api.shared.enums._position_test' )
   actual = { name: member.value for name, member in namespace[ 'Position' ].__members__.items() }

   assert actual == shared_members
   loader.assert_called_once_with( 'position.json' )


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
