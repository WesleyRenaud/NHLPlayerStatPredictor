from __future__ import annotations

from dataclasses import replace

import pytest

from api.projections.player_career_stats import PlayerCareerStats
from api.skaters.skater_summary import SkaterSummary
from api.time import Time


def _summary() -> SkaterSummary:
   return SkaterSummary.from_row( {
      'playerId': 7, 'skaterFullName': 'Stub Skater', 'positionCode': 'C', 'teamAbbrevs': 'COL',
      'gamesPlayed': 20, 'goals': 5, 'assists': 7, 'points': 12, 'penaltyMinutes': 4,
      'evGoals': 3, 'evPoints': 7, 'ppGoals': 1, 'ppPoints': 3, 'shGoals': 1, 'shPoints': 2,
      'shots': 40, 'timeOnIcePerGame': 1200.0,
   } )


def Test_FromSummaries_TestUnequalSeasons_ExpectSummedCountsAndWeightedRates() -> None:
   first = _summary()
   second = replace( first, games_played=2, shots=10, time_on_ice_per_game=1500.0 )
   summaries = [ first, second ]

   career = PlayerCareerStats.from_summaries( summaries )

   expected_counts = {
      'gamesPlayed': first.games_played + second.games_played,
      'goals': first.goals + second.goals,
      'assists': first.assists + second.assists,
      'points': first.points + second.points,
      'penaltyMinutes': first.penalty_minutes + second.penalty_minutes,
      'shots': first.shots + second.shots,
      'evenStrengthGoals': first.even_strength_goals + second.even_strength_goals,
      'evenStrengthPoints': first.even_strength_points + second.even_strength_points,
      'powerPlayGoals': first.power_play_goals + second.power_play_goals,
      'powerPlayPoints': first.power_play_points + second.power_play_points,
      'shortHandedGoals': first.short_handed_goals + second.short_handed_goals,
      'shortHandedPoints': first.short_handed_points + second.short_handed_points,
   }
   total_ice = sum( season.games_played * season.time_on_ice_per_game for season in summaries )
   average_ice = total_ice / expected_counts[ 'gamesPlayed' ]
   percentage = 100 * expected_counts[ 'goals' ] / expected_counts[ 'shots' ]
   assert career.time_on_ice_per_game == pytest.approx( average_ice )
   assert career.shooting_percentage == pytest.approx( percentage )
   assert career.to_dict() == {
      **expected_counts,
      'timeOnIcePerGame': Time.clock_string( Time.minutes( average_ice ) ),
      'shootingPercentage': pytest.approx( percentage ),
   }


def Test_FromSummaries_TestNoShots_ExpectUnavailablePercentageAndRecordedIce() -> None:
   summary = replace( _summary(), goals=0, shots=0 )
   career = PlayerCareerStats.from_summaries( [ summary ] )

   assert career.games_played == summary.games_played
   assert career.time_on_ice_per_game == summary.time_on_ice_per_game
   assert career.shooting_percentage is None
   assert career.to_dict()[ 'timeOnIcePerGame' ] == Time.clock_string( Time.minutes( summary.time_on_ice_per_game ) )
   assert career.to_dict()[ 'shootingPercentage' ] is None
