from __future__ import annotations

from api.projections.nhl_history_season import NhlHistorySeason
from api.projections.player_history_season import PlayerHistorySeason
from api.season import Season
from api.skaters.skater_summary import SkaterSummary


def Test_FromSummary_TestNhlStats_ExpectExplicitComponentsAndAllTeams() -> None:
   season_id = 20252026
   summary = SkaterSummary.from_row( {
      'playerId': 7, 'skaterFullName': 'Stub Skater', 'positionCode': 'C', 'teamAbbrevs': 'COL,EDM',
      'gamesPlayed': 20, 'goals': 5, 'assists': 7, 'points': 12, 'penaltyMinutes': 4,
      'evGoals': 0, 'evPoints': 7, 'ppGoals': 4, 'ppPoints': 4, 'shGoals': 1, 'shPoints': 1,
      'shots': 40, 'timeOnIcePerGame': 1200.0,
   } )

   season = NhlHistorySeason.from_summary( season_id, summary )

   assert isinstance( season, PlayerHistorySeason )
   assert season.to_dict() == {
      'seasonId': season_id, 'seasonLabel': Season.label( season_id ),
      'league': 'NHL', 'team': ', '.join( team.value for team in summary.team_abbrevs ),
      **summary.stats_dict(),
   }
