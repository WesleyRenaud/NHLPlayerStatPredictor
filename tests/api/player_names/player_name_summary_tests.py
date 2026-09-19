from __future__ import annotations

from api.player_names.player_name_summary import PlayerNameSummary
from api.season import Season
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def Test_AsJson_TestSummary_ExpectMappedFields() -> None:
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   summary = PlayerNameSummary( 1, 'Stub Skater', position, team, 20202021 )
   payload = summary.as_json()
   assert payload[ 'playerId' ] == summary.player_id
   assert payload[ 'playerName' ] == summary.player_name
   assert payload[ 'position' ] == position.value
   assert payload[ 'team' ] == team.value
   assert payload[ 'firstSeason' ] == Season.label( summary.first_season_id )
