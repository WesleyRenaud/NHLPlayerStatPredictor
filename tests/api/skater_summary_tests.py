from __future__ import annotations

from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.skater_summary import SkaterSummary
from api.team import Team


def Test_FromRow_TestSummaryJson_ExpectFields() -> None:
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   summary = SkaterSummary.from_row(
      {
         'playerId': 8478402,
         'skaterFullName': 'Connor McDavid',
         'positionCode': position.value,
         'teamAbbrevs': team.value,
         'gamesPlayed': 82,
         'goals': 44,
         'assists': 79,
         'points': 123,
      } )
   assert summary.player_id == 8478402
   assert summary.player_name == 'Connor McDavid'
   assert summary.position == position
   assert summary.team_abbrevs == [ team ]
   assert summary.points == 123


def Test_FromRow_TestTradedPlayer_ExpectTeams() -> None:
   teams = list( Team )
   first = teams[ Position.FIRST ]
   second = teams[ Position.SECOND ]
   summary = SkaterSummary.from_row(
      {
         'playerId': 1,
         'skaterFullName': 'Sample Player',
         'positionCode': list( SkaterPosition )[ Position.FIRST ].value,
         'teamAbbrevs': f'{ first.value },{ second.value }',
         'gamesPlayed': 82,
         'goals': 10,
         'assists': 20,
         'points': 30,
      } )
   assert summary.team_abbrevs == [ first, second ]
