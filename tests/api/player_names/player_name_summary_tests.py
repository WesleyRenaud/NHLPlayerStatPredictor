from __future__ import annotations

from api.player_names.player_name_summary import PlayerNameSummary
from api.season import Season
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_ToDict_TestSummary_ExpectMappedFields() -> None:
   position = SkaterPosition( 'C' )
   team = Team( 'MTL' )
   summary = PlayerNameSummary( 1, 'Stub Skater', position, team, 20202021 )

   payload = summary.to_dict()

   assert payload == {
      'playerId': summary.player_id,
      'playerName': summary.player_name,
      'position': position.value,
      'team': team.value,
      'firstSeason': Season.label( summary.first_season_id ),
   }
