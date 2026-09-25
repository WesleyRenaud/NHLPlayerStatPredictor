from __future__ import annotations

from api.shared.enums.position import Position
from api.skaters.team import Team
from api.skaters.team_name_change import TeamNameChange


def Test_Members_TestValues_ExpectTeamNames() -> None:
   team_names = { member.name for member in Team }
   changes = list( TeamNameChange )

   renamed = { change.name for change in changes }
   successors = { change.value for change in changes }

   assert renamed.isdisjoint( team_names )
   assert successors <= team_names


def Test_Current_TestKnownChange_ExpectSuccessor() -> None:
   change = list( TeamNameChange )[ Position.FIRST ]
   successor = Team( 'UTA' )

   current = TeamNameChange.current( change.name )

   assert current == successor.name


def Test_Current_TestUnknownKey_ExpectUnchanged() -> None:
   key = list( Team )[ Position.FIRST ].name

   current = TeamNameChange.current( key )

   assert current == key
