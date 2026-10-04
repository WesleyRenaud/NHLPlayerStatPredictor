from __future__ import annotations

from unittest.mock import Mock

import pytest

from api.skaters.team_name_change import TeamNameChange


def Test_Current_TestKnownChange_ExpectSuccessor( monkeypatch: pytest.MonkeyPatch ) -> None:
   old_name = 'OLD_TEST_TEAM'
   successor = 'NEW_TEST_TEAM'
   monkeypatch.setattr( TeamNameChange, '_member_map_', { old_name: Mock( value=successor ) } )

   current = TeamNameChange.current( old_name )

   assert current == successor


def Test_Current_TestUnknownKey_ExpectUnchanged( monkeypatch: pytest.MonkeyPatch ) -> None:
   key = 'UNCHANGED_TEST_TEAM'
   monkeypatch.setattr( TeamNameChange, '_member_map_', {} )

   current = TeamNameChange.current( key )

   assert current == key
