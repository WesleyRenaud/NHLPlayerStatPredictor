from __future__ import annotations

from api.shared.enums.position import Position
from api.skaters.team import Team
from api.skaters.team_name_change import TeamNameChange


def Test_Members_TestValues_ExpectTeamNames() -> None:
   names = { member.name for member in Team }

   for change in TeamNameChange:
      assert change.name not in names
      assert change.value in names


def Test_Current_TestKnownChange_ExpectSuccessor() -> None:
   assert TeamNameChange.current( 'UTAH_HOCKEY_CLUB' ) == Team( 'UTA' ).name


def Test_Current_TestUnknownKey_ExpectUnchanged() -> None:
   key = list( Team )[ Position.FIRST ].name
   assert TeamNameChange.current( key ) == key
