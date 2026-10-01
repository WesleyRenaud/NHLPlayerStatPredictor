from __future__ import annotations

import pytest

from api.projections.projection import Projection


def Test_ToDict_TestProjection_ExpectMappedFields() -> None:
   projection = Projection(
      goals=12,
      assists=34,
      points=46,
      penalty_minutes=18,
      games_played=70,
      power_play_goals=5,
      power_play_points=12,
      projected_toi=None )

   payload = projection.to_dict()

   assert payload == {
      'goals': projection.goals,
      'assists': projection.assists,
      'points': projection.points,
      'penaltyMinutes': 18,
      'gamesPlayed': projection.games_played,
      'powerPlayGoals': 5,
      'powerPlayPoints': 12,
      'projectedToi': None,
   }

   assert list( payload ) == [
      'goals',
      'assists',
      'points',
      'penaltyMinutes',
      'gamesPlayed',
      'powerPlayGoals',
      'powerPlayPoints',
      'projectedToi',
   ]


def Test_Init_TestPowerPlayGoalsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Power-play projection exceeds total scoring projection' ):
      Projection( goals=2, assists=4, points=6, penalty_minutes=None, games_played=70, power_play_goals=3, power_play_points=4, projected_toi=None )


def Test_Init_TestPowerPlayAssistsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Power-play projection exceeds total scoring projection' ):
      Projection( goals=2, assists=4, points=6, penalty_minutes=None, games_played=70, power_play_goals=1, power_play_points=6, projected_toi=None )
