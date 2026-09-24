from __future__ import annotations

from api.skater_group import SkaterGroup
from api.skater_position import SkaterPosition


def Test_Members_TestValues_ExpectUniqueStrings() -> None:
   values = [ member.value for member in SkaterGroup ]
   assert values
   assert len( values ) == len( set( values ) )

   for member in SkaterGroup:
      assert isinstance( member.value, str )
      assert SkaterGroup( member.value ) is member


def Test_Of_TestSkaterPositions_ExpectGroups() -> None:
   assert SkaterGroup.of( SkaterPosition( 'C' ) ) is SkaterGroup.FORWARD
   assert SkaterGroup.of( SkaterPosition( 'L' ) ) is SkaterGroup.FORWARD
   assert SkaterGroup.of( SkaterPosition( 'R' ) ) is SkaterGroup.FORWARD
   assert SkaterGroup.of( SkaterPosition( 'F' ) ) is SkaterGroup.FORWARD
   assert SkaterGroup.of( SkaterPosition( 'D' ) ) is SkaterGroup.DEFENSE


def Test_Position_TestGroups_ExpectSkaterPosition() -> None:
   assert SkaterGroup.FORWARD.position is SkaterPosition.FORWARD
   assert SkaterGroup.DEFENSE.position is SkaterPosition.DEFENSE


def Test_Positions_TestGroups_ExpectSkaterPositions() -> None:
   assert SkaterGroup.FORWARD.positions == {
      SkaterPosition.CENTER,
      SkaterPosition.FORWARD,
      SkaterPosition.LEFT_WING,
      SkaterPosition.RIGHT_WING,
   }
   assert SkaterGroup.DEFENSE.positions == { SkaterPosition.DEFENSE }
