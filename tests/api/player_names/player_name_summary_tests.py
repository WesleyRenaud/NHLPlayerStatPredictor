from __future__ import annotations

from api.player_names.player_name_summary import PlayerNameSummary
from api.season import Season
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_ToDict_TestSummary_ExpectMappedFields() -> None:
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   summary = PlayerNameSummary( 1, 'Stub Skater', position, team, 20202021 )
   payload = summary.to_dict()
   assert payload[ 'playerId' ] == summary.player_id
   assert payload[ 'playerName' ] == summary.player_name
   assert payload[ 'position' ] == position.value
   assert payload[ 'team' ] == team.value
   assert payload[ 'firstSeason' ] == Season.label( summary.first_season_id )
