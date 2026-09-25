from __future__ import annotations

from api.depth.depth_core_builder import DepthCoreBuilder
from api.depth.depth_group import DepthGroup
from api.depth.ice_skater import IceSkater
from api.depth.last_core import LastCore
from api.depth.league_filler import LeagueFiller
from api.depth.slot_average import SlotAverage
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _skater( player_id: int, implied: float ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      implied,
      implied,
      1.0 )


def Test_Build_TestRankedByToi_ExpectRegularsAndExtra() -> None:
   group = DepthGroup.defense()
   extra_id = 7
   regular_ids = list( range( 1, NhlLineupSelector.DRESSED_DEFENSE + 1 ) )

   core = DepthCoreBuilder.build(
      [
         _skater( extra_id, 12.0 ),
         _skater( 1, 26.0 ),
         _skater( 2, 24.0 ),
         _skater( 3, 20.0 ),
         _skater( 4, 19.0 ),
         _skater( 5, 16.0 ),
         _skater( 6, 15.0 ),
         _skater( 8, 11.0 ),
      ],
      group,
      [] )

   assert [ skater.player_id for skater in core.regulars ] == regular_ids
   assert len( core.extras ) == LastCore.EXTRA
   assert core.extras[ Position.FIRST ].player_id == extra_id


def Test_Build_TestShortRoster_ExpectLeagueExtra() -> None:
   group = DepthGroup.defense()
   slot = SlotAverage( group.spare_slot, 14.0, 1.0, 2.0 )
   slots = [ slot ]

   core = DepthCoreBuilder.build( [ _skater( 1, 22.0 ) ], group, slots )

   assert [ skater.player_id for skater in core.regulars ] == [ 1 ]
   assert len( core.extras ) == LastCore.EXTRA
   assert core.extras[ Position.FIRST ].player_id == LeagueFiller.player_id(
      group.spare_slot )
   assert core.extras[ Position.FIRST ].implied == slot.toi
