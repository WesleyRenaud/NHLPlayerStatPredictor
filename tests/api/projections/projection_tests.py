from __future__ import annotations

from api.projections.projection import Projection


def Test_ToDict_TestProjection_ExpectMappedFields() -> None:
   projection = Projection(
      even_strength_goals=6,
      even_strength_points=31,
      penalty_minutes=18,
      games_played=70,
      power_play_goals=5,
      power_play_points=12,
      short_handed_goals=1,
      short_handed_points=3,
      projected_toi=None )

   payload = projection.to_dict()

   assert payload == {
      'goals': projection.goals,
      'assists': projection.assists,
      'points': projection.points,
      'penaltyMinutes': projection.penalty_minutes,
      'gamesPlayed': projection.games_played,
      'powerPlayGoals': projection.power_play_goals,
      'powerPlayPoints': projection.power_play_points,
      'shortHandedGoals': projection.short_handed_goals,
      'shortHandedPoints': projection.short_handed_points,
      'evenStrengthGoals': projection.even_strength_goals,
      'evenStrengthPoints': projection.even_strength_points,
      'shots': projection.shots,
      'shootingPercentage': projection.shooting_percentage,
      'projectedToi': projection.projected_toi,
   }

   assert list( payload ) == [
      'goals',
      'assists',
      'points',
      'penaltyMinutes',
      'gamesPlayed',
      'powerPlayGoals',
      'powerPlayPoints',
      'shortHandedGoals',
      'shortHandedPoints',
      'evenStrengthGoals',
      'evenStrengthPoints',
      'shots',
      'shootingPercentage',
      'projectedToi',
   ]


def Test_Totals_TestComponents_ExpectSumsOfStoredCounts() -> None:
   projection = Projection(
      even_strength_goals=6,
      even_strength_points=31,
      penalty_minutes=None,
      games_played=70,
      power_play_goals=5,
      power_play_points=12,
      short_handed_goals=1,
      short_handed_points=3 )

   expected_goals = (
      projection.even_strength_goals + projection.power_play_goals + projection.short_handed_goals )
   expected_points = (
      projection.even_strength_points + projection.power_play_points + projection.short_handed_points )
   expected_assists = (
      projection.even_strength_points - projection.even_strength_goals
      + projection.power_play_points - projection.power_play_goals
      + projection.short_handed_points - projection.short_handed_goals )

   assert projection.goals == expected_goals
   assert projection.points == expected_points
   assert projection.assists == expected_assists
   assert projection.points == projection.goals + projection.assists


def Test_Totals_TestZeroComponents_ExpectZeroScoring() -> None:
   projection = Projection( 0, 0, None, 70, 0, 0, 0, 0 )

   assert projection.goals == 0
   assert projection.assists == 0
   assert projection.points == 0
