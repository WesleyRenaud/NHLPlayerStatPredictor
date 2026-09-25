from __future__ import annotations

from api.depth.ice_usage_parser import IceUsageParser
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team
from api.time import Time


def Test_Parse_TestDefenseRow_ExpectUsage() -> None:
   defense_id = 7
   forward_id = 97
   games = 80
   defense_seconds = 1480.8
   forward_seconds = 1200.0
   defense_team = Team( 'MIN' )
   forward_team = Team( 'EDM' )
   rows = [
      {
         'playerId': defense_id,
         'positionCode': 'D',
         'gamesPlayed': games,
         'timeOnIcePerGame': defense_seconds,
         'teamAbbrevs': defense_team.value,
      },
      {
         'playerId': forward_id,
         'positionCode': 'C',
         'gamesPlayed': games,
         'timeOnIcePerGame': forward_seconds,
         'teamAbbrevs': forward_team.value,
      },
   ]

   usages = IceUsageParser.parse( rows )

   assert set( usages ) == { defense_id, forward_id }
   assert usages[ defense_id ].toi == Time.minutes( defense_seconds )
   assert usages[ defense_id ].games == games
   assert usages[ defense_id ].team == defense_team
   assert usages[ defense_id ].position == SkaterPosition( 'D' )
   assert usages[ forward_id ].toi == Time.minutes( forward_seconds )
   assert usages[ forward_id ].position == SkaterPosition( 'C' )


def Test_Parse_TestTraded_ExpectPrimaryTeam() -> None:
   player_id = 43
   first = Team( 'VAN' )
   primary = Team( 'MIN' )

   usages = IceUsageParser.parse( [
      {
         'playerId': player_id,
         'positionCode': 'D',
         'gamesPlayed': 74,
         'timeOnIcePerGame': 1664.4,
         'teamAbbrevs': f'{ first.value },{ primary.value }',
      },
   ] )

   assert usages[ player_id ].team == primary
