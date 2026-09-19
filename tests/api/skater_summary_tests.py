from __future__ import annotations

from api.skater_position import SkaterPosition
from api.skater_summary import SkaterSummary
from api.team import Team


def Test_FromRow_TestSummaryJson_ExpectFields() -> None:
   summary = SkaterSummary.from_row(
      {
         'playerId': 8478402,
         'skaterFullName': 'Connor McDavid',
         'positionCode': 'C',
         'teamAbbrevs': 'EDM',
         'gamesPlayed': 82,
         'goals': 44,
         'assists': 79,
         'points': 123,
      } )
   assert summary.player_id == 8478402
   assert summary.player_name == 'Connor McDavid'
   assert summary.position == SkaterPosition.CENTER
   assert summary.team_abbrevs == [ Team.EDMONTON_OILERS ]
   assert summary.points == 123


def Test_FromRow_TestTradedPlayer_ExpectTeams() -> None:
   summary = SkaterSummary.from_row(
      {
         'playerId': 1,
         'skaterFullName': 'Sample Player',
         'positionCode': 'C',
         'teamAbbrevs': 'CHI,TOR',
         'gamesPlayed': 82,
         'goals': 10,
         'assists': 20,
         'points': 30,
      } )
   assert summary.team_abbrevs == [
      Team.CHICAGO_BLACKHAWKS,
      Team.TORONTO_MAPLE_LEAFS,
   ]
