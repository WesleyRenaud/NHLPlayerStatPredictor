from __future__ import annotations

from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_summary import SkaterSummary
from api.skaters.team import Team


def Test_FromRow_TestSummaryJson_ExpectFields() -> None:
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   summary = SkaterSummary(
      8478402,
      'Connor McDavid',
      position,
      [ team ],
      82,
      44,
      79,
      123,
      12,
      20,
      60,
      2,
      4 )

   loaded = SkaterSummary.from_row( {
      'playerId': summary.player_id,
      'skaterFullName': summary.player_name,
      'positionCode': summary.position.value,
      'teamAbbrevs': team.value,
      'gamesPlayed': summary.games_played,
      'goals': summary.goals,
      'assists': summary.assists,
      'points': summary.points,
      'penaltyMinutes': summary.penalty_minutes,
      'ppGoals': summary.power_play_goals,
      'ppPoints': summary.power_play_points,
      'shGoals': summary.short_handed_goals,
      'shPoints': summary.short_handed_points,
   } )

   assert loaded == summary


def Test_FromRow_TestTradedPlayer_ExpectTeams() -> None:
   teams = list( Team )
   first = teams[ Position.FIRST ]
   second = teams[ Position.SECOND ]
   position = list( SkaterPosition )[ Position.FIRST ]
   summary = SkaterSummary(
      1,
      'Sample Player',
      position,
      [ first, second ],
      82,
      10,
      20,
      30,
      8,
      2,
      8,
      1,
      2 )

   loaded = SkaterSummary.from_row( {
      'playerId': summary.player_id,
      'skaterFullName': summary.player_name,
      'positionCode': summary.position.value,
      'teamAbbrevs': f'{ first.value },{ second.value }',
      'gamesPlayed': summary.games_played,
      'goals': summary.goals,
      'assists': summary.assists,
      'points': summary.points,
      'penaltyMinutes': summary.penalty_minutes,
      'ppGoals': summary.power_play_goals,
      'ppPoints': summary.power_play_points,
      'shGoals': summary.short_handed_goals,
      'shPoints': summary.short_handed_points,
   } )

   assert loaded == summary
