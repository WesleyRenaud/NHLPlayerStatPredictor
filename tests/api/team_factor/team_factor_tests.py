from __future__ import annotations

from api.availability.games_share import GamesShare
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup
from api.skaters.team import Team
from api.team_factor.team_factor import TeamFactor
from api.team_factor.team_factor_skater import TeamFactorSkater


def Test_ToDict_TestFactor_ExpectSeasonTeamRateAndSkaters() -> None:
   skater = TeamFactorSkater( 97, 120.5, SkaterGroup( 'F' ), GamesShare.FULL, False, None )
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
      [ TeamFactorSkater( 29, 88.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ) ] )
   assert TeamFactor.from_row( factor.to_dict() ) == factor


def Test_Rate_TestMatchingSeasonAndTeam_ExpectRate() -> None:
   team = list( Team )[ Position.FIRST ]
   factor = TeamFactor(
      20252026,
      team,
      0.87,
      [ TeamFactorSkater( 97, 120.5, SkaterGroup( 'F' ), GamesShare.FULL, False, None ) ] )
   assert TeamFactor.rate( [ factor ], factor.season, team ) == factor.rate


def Test_Excluding_TestPlayerInLineup_ExpectShareRemoved() -> None:
   player_id = 97
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      1.2,
      [
         TeamFactorSkater( player_id, 40.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
         TeamFactorSkater( 29, 60.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
      ] )
   assert factor.excluding( player_id ) == factor.rate * 60.0 / 100.0


def Test_Excluding_TestPlayerMissing_ExpectPublishedRate() -> None:
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      1.2,
      [ TeamFactorSkater( 29, 60.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ) ] )
   assert factor.excluding( 97 ) == factor.rate


def Test_TeammateRate_TestMatchingSeasonAndTeam_ExpectExcludedRate() -> None:
   team = list( Team )[ Position.FIRST ]
   player_id = 97
   factor = TeamFactor(
      20262027,
      team,
      1.2,
      [
         TeamFactorSkater( player_id, 40.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
         TeamFactorSkater( 29, 60.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
      ] )
   assert TeamFactor.teammate_rate(
      [ factor ],
      factor.season,
      team,
      player_id ) == factor.excluding( player_id )


def Test_Excluding_TestInjuredDefense_ExpectTeammatesWhenPlaying() -> None:
   extra = TeamFactorSkater(
      7,
      10.0,
      SkaterGroup( 'D' ),
      GamesShare.FULL,
      True,
      None )
   injured = TeamFactorSkater( 1, 20.0, SkaterGroup( 'D' ), 0.5, False, None )
   rest = [
      TeamFactorSkater( index, 20.0, SkaterGroup( 'D' ), GamesShare.FULL, False, None )
      for index in range( 2, 7 )
   ]
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      1.0,
      [ injured, extra, *rest ] )
   total = factor.dressed_total()
   assert abs( factor.excluding( 1 ) * total - 100.0 ) < 0.001
   assert abs( factor.excluding( 2 ) * total - 95.0 ) < 0.001


def Test_DressedTotal_TestSamePrior_ExpectHealthySix() -> None:
   regulars = [
      TeamFactorSkater( index, 20.0, SkaterGroup( 'D' ), 0.5, False, 0.5 )
      for index in range( 1, 7 )
   ]
   extra = TeamFactorSkater(
      7,
      10.0,
      SkaterGroup( 'D' ),
      GamesShare.FULL,
      True,
      None )
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      1.0,
      [ extra, *regulars ] )
   assert abs( factor.dressed_total() - 120.0 ) < 0.001
