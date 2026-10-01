from __future__ import annotations

import pytest

from api.projections.projection import Projection


def Test_ToDict_TestProjection_ExpectMappedFields() -> None:
   projection = Projection( 12, 34, 46, 70, 5, 12, 1, 3 )

   payload = projection.to_dict()

   assert payload == {
      'goals': projection.goals,
      'assists': projection.assists,
      'points': projection.points,
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
      'gamesPlayed',
      'powerPlayGoals',
      'powerPlayPoints',
      'shortHandedGoals',
      'shortHandedPoints',
      'projectedToi',
   ]


def Test_Init_TestPowerPlayAndShortHandedGoalsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Special-teams projection exceeds total scoring projection' ):
      Projection( 2, 4, 6, 70, 1, 2, 2, 2 )


def Test_Init_TestPowerPlayAndShortHandedPointsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Special-teams projection exceeds total scoring projection' ):
      Projection( 2, 4, 6, 70, 1, 2, 1, 5 )
