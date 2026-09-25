from __future__ import annotations

from api.ingest.roster_skater_builder import RosterSkaterBuilder
from api.shared.enums.position import Position
from api.skaters.roster_skater import RosterSkater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _player(
      player_id: int,
      first: str,
      last: str,
      position: str ) -> dict[ str, object ]:
   return {
      'id': player_id,
      'firstName': { 'default': first },
      'lastName': { 'default': last },
      'positionCode': position,
   }


def Test_Build_TestSkatersAndGoalies_ExpectSkatersOnly() -> None:
   team = list( Team )[ Position.FIRST ]
   position = list( SkaterPosition )[ Position.FIRST ]
   forward = _player( 1, 'First', 'Forward', position.value )
   defense = _player( 2, 'Second', 'Defense', position.value )
   goalie = _player( 3, 'Third', 'Goalie', 'G' )
   rows = RosterSkaterBuilder.build(
      team,
      {
         RosterSkaterBuilder.FORWARD_KEY: [ forward ],
         RosterSkaterBuilder.DEFENSE_KEY: [ defense ],
         'goalies': [ goalie ],
      } )
   assert rows == [
      RosterSkater( 1, 'First Forward', position, team ),
      RosterSkater( 2, 'Second Defense', position, team ),
   ]
