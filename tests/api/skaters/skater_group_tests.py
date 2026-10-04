from __future__ import annotations

from api.skaters.skater_group import SkaterGroup
from api.skaters.skater_position import SkaterPosition


def Test_Of_TestSkaterPositions_ExpectGroups() -> None:
   center = SkaterPosition( 'C' )
   left = SkaterPosition( 'L' )
   right = SkaterPosition( 'R' )
   forward = SkaterPosition( 'F' )
   defense = SkaterPosition( 'D' )

   groups = [
      SkaterGroup.of( center ),
      SkaterGroup.of( left ),
      SkaterGroup.of( right ),
      SkaterGroup.of( forward ),
      SkaterGroup.of( defense ),
   ]

   assert groups == [
      SkaterGroup( 'F' ),
      SkaterGroup( 'F' ),
      SkaterGroup( 'F' ),
      SkaterGroup( 'F' ),
      SkaterGroup( 'D' ),
   ]


def Test_Position_TestGroups_ExpectSkaterPosition() -> None:
   forward = SkaterGroup( 'F' )
   defense = SkaterGroup( 'D' )

   positions = ( forward.position, defense.position )

   assert positions == ( SkaterPosition( 'F' ), SkaterPosition( 'D' ) )


def Test_Positions_TestGroups_ExpectSkaterPositions() -> None:
   forward = SkaterGroup( 'F' )
   defense = SkaterGroup( 'D' )

   positions = ( forward.positions, defense.positions )

   assert positions == (
      {
         SkaterPosition( 'C' ),
         SkaterPosition( 'F' ),
         SkaterPosition( 'L' ),
         SkaterPosition( 'R' ),
      },
      { SkaterPosition( 'D' ) },
   )
