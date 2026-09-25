from __future__ import annotations

from api.depth.depth_group import DepthGroup
from api.depth.last_core import LastCore
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.shared.enums.position import Position
from api.skaters.roster_skater import RosterSkater
from api.skaters.skater_group import SkaterGroup
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_Forwards_TestLineup_ExpectForwardConstants() -> None:
   group = DepthGroup.forwards()
   assert group.dressed_count == NhlLineupSelector.DRESSED_FORWARDS
   assert group.spare_slot == NhlLineupSelector.DRESSED_FORWARDS + 1
   assert group.extra_count == LastCore.EXTRA
   assert group.roster_count == NhlLineupSelector.DRESSED_FORWARDS + LastCore.EXTRA
   assert group.ice_minutes == DepthGroup.FORWARD_ICE_MINUTES
   assert group.label == 'F'
   assert group.skater_group is SkaterGroup.FORWARD
   assert group.positions == SkaterGroup.FORWARD.positions


def Test_Defense_TestLineup_ExpectDefenseConstants() -> None:
   group = DepthGroup.defense()
   assert group.dressed_count == NhlLineupSelector.DRESSED_DEFENSE
   assert group.spare_slot == NhlLineupSelector.DRESSED_DEFENSE + 1
   assert group.extra_count == LastCore.EXTRA
   assert group.roster_count == NhlLineupSelector.DRESSED_DEFENSE + LastCore.EXTRA
   assert group.ice_minutes == DepthGroup.DEFENSE_ICE_MINUTES
   assert group.label == 'D'
   assert group.skater_group is SkaterGroup.DEFENSE
   assert group.positions == SkaterGroup.DEFENSE.positions


def Test_Skaters_TestTeamAndPosition_ExpectGroupMembers() -> None:
   team = list( Team )[ Position.FIRST ]
   other = list( Team )[ Position.SECOND ]
   forward = RosterSkater( 1, 'C', SkaterPosition( 'C' ), team )
   defense = RosterSkater( 2, 'D', SkaterPosition( 'D' ), team )
   elsewhere = RosterSkater( 3, 'C', SkaterPosition( 'C' ), other )
   roster = [ forward, defense, elsewhere ]
   assert DepthGroup.forwards().skaters( roster, team ) == [ forward ]
   assert DepthGroup.defense().skaters( roster, team ) == [ defense ]


def Test_Contains_TestPositions_ExpectGroupMembership() -> None:
   forwards = DepthGroup.forwards()
   defense = DepthGroup.defense()
   assert forwards.contains( SkaterPosition( 'C' ) )
   assert forwards.contains( SkaterPosition( 'L' ) )
   assert forwards.contains( SkaterPosition( 'F' ) )
   assert not forwards.contains( SkaterPosition( 'D' ) )
   assert defense.contains( SkaterPosition( 'D' ) )
   assert not defense.contains( SkaterPosition( 'C' ) )
