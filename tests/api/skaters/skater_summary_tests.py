from __future__ import annotations

from dataclasses import replace

import pytest

from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_summary import SkaterSummary
from api.skaters.team import Team
from api.time import Time


def _summary() -> SkaterSummary:
   return SkaterSummary(
      7, 'Stub Skater', SkaterPosition( 'C' ), [ Team( 'COL' ) ],
      3, 1, 2, 3, 4, 0, 0, 0, 0, 1, 3, 10, 1280.0 )


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
      4,
      22,
      59,
      250,
      1280.0 )

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
      'evGoals': summary.even_strength_goals,
      'evPoints': summary.even_strength_points,
      'shots': summary.shots,
      'timeOnIcePerGame': summary.time_on_ice_per_game,
   } )

   assert loaded == summary


def Test_StatsDict_TestObservedTotals_ExpectUnscaledCountsAndFormattedTime() -> None:
   summary = _summary()

   assert summary.stats_dict() == {
      'goals': summary.goals,
      'assists': summary.assists,
      'points': summary.points,
      'gamesPlayed': summary.games_played,
      'penaltyMinutes': summary.penalty_minutes,
      'evenStrengthGoals': summary.even_strength_goals,
      'evenStrengthPoints': summary.even_strength_points,
      'powerPlayGoals': summary.power_play_goals,
      'powerPlayPoints': summary.power_play_points,
      'shortHandedGoals': summary.short_handed_goals,
      'shortHandedPoints': summary.short_handed_points,
      'shots': summary.shots,
      'shootingPercentage': pytest.approx( 100 * summary.goals / summary.shots ),
      'timeOnIcePerGame': Time.clock_string( Time.minutes( summary.time_on_ice_per_game ) ),
   }


def Test_StatsDict_TestNoShots_ExpectUnavailablePercentage() -> None:
   summary = replace( _summary(), shots=0, goals=0 )

   stats = summary.stats_dict()

   assert stats[ 'shots' ] == 0
   assert stats[ 'shootingPercentage' ] is None


@pytest.mark.parametrize( 'goals', [ 0, 1 ] )
def Test_ShootingPercentage_TestRecordedShots_ExpectGoalToShotPercentage( goals: int ) -> None:
   summary = replace( _summary(), goals=goals )

   assert summary.shooting_percentage == pytest.approx( 100 * summary.goals / summary.shots )
   assert summary.stats_dict()[ 'shootingPercentage' ] == summary.shooting_percentage


def Test_ShootingPercentage_TestNoShots_ExpectNone() -> None:
   summary = replace( _summary(), shots=0, goals=0 )

   assert summary.shooting_percentage is None


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
      2,
      7,
      20,
      100,
      1200.0 )

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
      'evGoals': summary.even_strength_goals,
      'evPoints': summary.even_strength_points,
      'shots': summary.shots,
      'timeOnIcePerGame': summary.time_on_ice_per_game,
   } )

   assert loaded == summary
