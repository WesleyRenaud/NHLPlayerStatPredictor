from __future__ import annotations

from api.depth.ice_usage import IceUsage
from api.depth.retired_roster_binder import RetiredRosterBinder
from api.shared.enums.position import Position
from api.skaters.player_status import PlayerStatus
from api.skaters.roster_skater import RosterSkater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _roster( player_id: int ) -> RosterSkater:
   return RosterSkater(
      player_id,
      'Rostered',
      SkaterPosition( 'C' ),
      list( Team )[ Position.FIRST ] )


def _usage( player_id: int ) -> dict[ int, IceUsage ]:
   return {
      player_id: IceUsage(
         19.1,
         67,
         list( Team )[ Position.SECOND ],
         SkaterPosition( 'C' ) )
   }


def Test_Bind_TestInactiveUsage_ExpectAdded() -> None:
   player_id = 4
   bound = RetiredRosterBinder.bind(
      [ _roster( 1 ) ],
      _usage( player_id ),
      [ PlayerStatus( player_id, False ) ],
      { player_id: 'Retired' } )
   assert bound[ Position.FIRST ].player_id == 1
   assert bound[ Position.LAST ].player_id == player_id
   assert bound[ Position.LAST ].player_name == 'Retired'
   assert bound[ Position.LAST ].team is list( Team )[ Position.SECOND ]


def Test_Bind_TestAlreadyRostered_ExpectUnchanged() -> None:
   player_id = 1
   bound = RetiredRosterBinder.bind(
      [ _roster( player_id ) ],
      _usage( player_id ),
      [ PlayerStatus( player_id, False ) ],
      { player_id: 'Retired' } )
   assert bound == [ _roster( player_id ) ]


def Test_Bind_TestActiveMissing_ExpectUnchanged() -> None:
   player_id = 4
   bound = RetiredRosterBinder.bind(
      [ _roster( 1 ) ],
      _usage( player_id ),
      [ PlayerStatus( player_id, True ) ],
      { player_id: 'Unsigned' } )
   assert bound == [ _roster( 1 ) ]


def Test_Bind_TestMissingName_ExpectSkipped() -> None:
   player_id = 4
   bound = RetiredRosterBinder.bind(
      [ _roster( 1 ) ],
      _usage( player_id ),
      [ PlayerStatus( player_id, False ) ],
      {} )
   assert bound == [ _roster( 1 ) ]


def Test_Missing_TestInactiveUsage_ExpectId() -> None:
   player_id = 4
   assert RetiredRosterBinder.missing(
      [ _roster( 1 ) ],
      _usage( player_id ),
      [ PlayerStatus( player_id, False ) ] ) == [ player_id ]


def Test_Missing_TestAlreadyRostered_ExpectEmpty() -> None:
   player_id = 1
   assert RetiredRosterBinder.missing(
      [ _roster( player_id ) ],
      _usage( player_id ),
      [ PlayerStatus( player_id, False ) ] ) == []


def Test_Missing_TestActiveMissing_ExpectEmpty() -> None:
   player_id = 4
   assert RetiredRosterBinder.missing(
      [ _roster( 1 ) ],
      _usage( player_id ),
      [ PlayerStatus( player_id, True ) ] ) == []
