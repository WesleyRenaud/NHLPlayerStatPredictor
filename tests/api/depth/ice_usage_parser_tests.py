from __future__ import annotations

from api.depth.ice_usage_parser import IceUsageParser
from api.skaters.team import Team


def Test_Parse_TestDefenseRow_ExpectUsage() -> None:
   usages = IceUsageParser.parse( [
      {
         'playerId': 7,
         'positionCode': 'D',
         'gamesPlayed': 80,
         'timeOnIcePerGame': 1480.8,
         'teamAbbrevs': 'MIN',
      },
      {
         'playerId': 97,
         'positionCode': 'C',
         'gamesPlayed': 80,
         'timeOnIcePerGame': 1200.0,
         'teamAbbrevs': 'EDM',
      },
   ] )
   assert set( usages ) == { 7, 97 }
   assert usages[ 7 ].toi == 24.68
   assert usages[ 7 ].games == 80
   assert usages[ 7 ].team == Team( 'MIN' )
   assert usages[ 7 ].position.value == 'D'
   assert usages[ 97 ].toi == 20.0
   assert usages[ 97 ].position.value == 'C'


def Test_Parse_TestTraded_ExpectPrimaryTeam() -> None:
   usages = IceUsageParser.parse( [
      {
         'playerId': 43,
         'positionCode': 'D',
         'gamesPlayed': 74,
         'timeOnIcePerGame': 1664.4,
         'teamAbbrevs': 'VAN,MIN',
      },
   ] )
   assert usages[ 43 ].team == Team( 'MIN' )
