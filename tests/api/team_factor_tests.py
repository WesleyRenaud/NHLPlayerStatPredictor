from __future__ import annotations

from api.shared.enums.position import Position
from api.team import Team
from api.team_factor import TeamFactor
from api.team_factor_skater import TeamFactorSkater


def Test_ToDict_TestFactor_ExpectSeasonTeamRateAndSkaters() -> None:
   skater = TeamFactorSkater( 97, 120.5 )
   factor = TeamFactor(
      20252026,
      list( Team )[ Position.FIRST ],
      0.87,
      [ skater ] )
   assert factor.to_dict() == {
      'season': factor.season,
      'team': factor.team.value,
      'rate': factor.rate,
      'skaters': [ skater.to_dict() ],
   }


def Test_FromRow_TestDict_ExpectFactor() -> None:
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.SECOND ],
      1.12,
      [ TeamFactorSkater( 29, 88.0 ) ] )
   assert TeamFactor.from_row( factor.to_dict() ) == factor


def Test_Rate_TestMatchingSeasonAndTeam_ExpectRate() -> None:
   team = list( Team )[ Position.FIRST ]
   factor = TeamFactor(
      20252026,
      team,
      0.87,
      [ TeamFactorSkater( 97, 120.5 ) ] )
   assert TeamFactor.rate( [ factor ], factor.season, team ) == factor.rate


def Test_Excluding_TestPlayerInLineup_ExpectShareRemoved() -> None:
   player_id = 97
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      1.2,
      [
         TeamFactorSkater( player_id, 40.0 ),
         TeamFactorSkater( 29, 60.0 ),
      ] )
   assert factor.excluding( player_id ) == factor.rate * 60.0 / 100.0


def Test_Excluding_TestPlayerMissing_ExpectPublishedRate() -> None:
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      1.2,
      [ TeamFactorSkater( 29, 60.0 ) ] )
   assert factor.excluding( 97 ) == factor.rate


def Test_Excluding_TestEmptyLineup_ExpectPublishedRate() -> None:
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      1.2,
      [] )
   assert factor.excluding( 97 ) == factor.rate


def Test_MateRate_TestMatchingSeasonAndTeam_ExpectExcludedRate() -> None:
   team = list( Team )[ Position.FIRST ]
   player_id = 97
   factor = TeamFactor(
      20262027,
      team,
      1.2,
      [
         TeamFactorSkater( player_id, 40.0 ),
         TeamFactorSkater( 29, 60.0 ),
      ] )
   assert TeamFactor.mate_rate(
      [ factor ],
      factor.season,
      team,
      player_id ) == factor.excluding( player_id )
