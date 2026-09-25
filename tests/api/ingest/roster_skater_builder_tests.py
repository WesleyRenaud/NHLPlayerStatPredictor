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
   position = SkaterPosition( 'C' )
   forward_id = 1
   defense_id = 2
   goalie_id = 3
   forward_first = 'First'
   forward_last = 'Forward'
   defense_first = 'Second'
   defense_last = 'Defense'
   goalie_first = 'Third'
   goalie_last = 'Goalie'
   goalie_position = 'G'
   forward = _player( forward_id, forward_first, forward_last, position.value )
   defense = _player( defense_id, defense_first, defense_last, position.value )
   goalie = _player( goalie_id, goalie_first, goalie_last, goalie_position )
   payload = {
      RosterSkaterBuilder.FORWARD_KEY: [ forward ],
      RosterSkaterBuilder.DEFENSE_KEY: [ defense ],
      'goalies': [ goalie ],
   }

   rows = RosterSkaterBuilder.build( team, payload )

   assert rows == [
      RosterSkater( forward_id, f'{ forward_first } { forward_last }', position, team ),
      RosterSkater( defense_id, f'{ defense_first } { defense_last }', position, team ),
   ]
