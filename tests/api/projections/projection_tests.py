from __future__ import annotations

import pytest

from api.projections.projection import Projection


def Test_ToDict_TestProjection_ExpectMappedFields() -> None:
   projection = Projection( 12, 34, 46, 70, 5, 12 )

   payload = projection.to_dict()

   assert payload == {
      'goals': projection.goals,
      'assists': projection.assists,
      'points': projection.points,
      'gamesPlayed': projection.games_played,
      'powerPlayGoals': 5,
      'powerPlayPoints': 12,
      'projectedToi': None,
   }

   assert list( payload ) == [
      'goals',
      'assists',
      'points',
      'gamesPlayed',
      'powerPlayGoals',
      'powerPlayPoints',
      'projectedToi',
   ]


def Test_Init_TestPowerPlayGoalsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Power-play projection exceeds total scoring projection' ):
      Projection( 2, 4, 6, 70, 3, 4 )


def Test_Init_TestPowerPlayAssistsExceedTotal_ExpectValueError() -> None:
   with pytest.raises( ValueError, match='Power-play projection exceeds total scoring projection' ):
      Projection( 2, 4, 6, 70, 1, 6 )
