from __future__ import annotations

from unittest.mock import Mock

import pytest

from api.skaters.team import Team
from api.skaters.team_name_change import TeamNameChange


@pytest.fixture
def team( monkeypatch: pytest.MonkeyPatch ) -> Team:
   member = Team.ANAHEIM_DUCKS
   monkeypatch.setattr( Team, '_member_map_', {
      'TEST_ACCENTED_TEAM': member,
      'TEST_DOTTED_TEAM': member,
      'TEST_SUCCESSOR': member,
   } )
   monkeypatch.setattr( TeamNameChange, '_member_map_', {} )
   return member


def Test_FromName_TestAccentedName_ExpectTeam( team: Team ) -> None:
   name = 'Tést Accented Team'

   resolved = Team.from_name( name )

   assert resolved is team


def Test_FromName_TestDottedName_ExpectTeam( team: Team ) -> None:
   name = 'Test. Dotted Team'

   resolved = Team.from_name( name )

   assert resolved is team


def Test_FromName_TestRenamedTeam_ExpectSuccessor(
      team: Team,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   name = 'Old Test Team'
   rename = Mock( return_value='TEST_SUCCESSOR' )
   monkeypatch.setattr( TeamNameChange, 'current', rename )

   resolved = Team.from_name( name )

   assert resolved is team
   rename.assert_called_once_with( 'OLD_TEST_TEAM' )
