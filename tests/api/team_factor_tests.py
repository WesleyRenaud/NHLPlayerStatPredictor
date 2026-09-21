from __future__ import annotations

from api.shared.enums.position import Position
from api.team import Team
from api.team_factor import TeamFactor


def Test_ToDict_TestFactor_ExpectSeasonTeamAndRate() -> None:
   factor = TeamFactor( 20252026, list( Team )[ Position.FIRST ], 0.87 )
   assert factor.to_dict() == {
      'season': factor.season,
      'team': factor.team.value,
      'rate': factor.rate,
   }


def Test_FromRow_TestDict_ExpectFactor() -> None:
   factor = TeamFactor( 20262027, list( Team )[ Position.SECOND ], 1.12 )
   assert TeamFactor.from_row( factor.to_dict() ) == factor


def Test_Rate_TestMatchingSeasonAndTeam_ExpectRate() -> None:
   team = list( Team )[ Position.FIRST ]
   factor = TeamFactor( 20252026, team, 0.87 )
   assert TeamFactor.rate( [ factor ], factor.season, team ) == factor.rate
