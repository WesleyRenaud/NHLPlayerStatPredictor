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
      short_handed_goals=1,
      short_handed_points=3,
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
      'shortHandedGoals': 1,
      'shortHandedPoints': 3,
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
      'shortHandedGoals',
      'shortHandedPoints',
      'projectedToi',
   ]


def Test_Init_TestPowerPlayAndShortHandedGoalsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Special-teams projection exceeds total scoring projection' ):
      Projection( 2, 4, 6, None, 70, 1, 2, 2, 2 )


def Test_Init_TestPowerPlayAndShortHandedPointsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Special-teams projection exceeds total scoring projection' ):
      Projection( 2, 4, 6, None, 70, 1, 2, 1, 5 )


def Test_Init_TestPowerPlayGoalsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Special-teams projection exceeds total scoring projection' ):
      Projection( 2, 4, 6, None, 70, 3, 4, 0, 0 )


def Test_Init_TestPowerPlayAssistsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Special-teams projection exceeds total scoring projection' ):
      Projection( 2, 4, 6, None, 70, 1, 6, 0, 0 )
