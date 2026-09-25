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

   payload = factor.to_dict()

   assert payload == {
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

   loaded = TeamFactor.from_row( factor.to_dict() )

   assert loaded == factor


def Test_Rate_TestMatchingSeasonAndTeam_ExpectRate() -> None:
   team = list( Team )[ Position.FIRST ]
   factor = TeamFactor(
      20252026,
      team,
      0.87,
      [ TeamFactorSkater( 97, 120.5, SkaterGroup( 'F' ), GamesShare.FULL, False, None ) ] )

   rate = TeamFactor.rate( [ factor ], factor.season, team )

   assert rate == factor.rate


def Test_Excluding_TestPlayerInLineup_ExpectShareRemoved() -> None:
   player_id = 97
   teammate_id = 29
   player_pace = 40.0
   teammate_pace = 60.0
   rate = 1.2
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      rate,
      [
         TeamFactorSkater( player_id, player_pace, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
         TeamFactorSkater( teammate_id, teammate_pace, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
      ] )

   excluded = factor.excluding( player_id )

   assert excluded == rate * teammate_pace / ( player_pace + teammate_pace )


def Test_Excluding_TestPlayerMissing_ExpectPublishedRate() -> None:
   rate = 1.2
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      rate,
      [ TeamFactorSkater( 29, 60.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ) ] )

   excluded = factor.excluding( 97 )

   assert excluded == factor.rate


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

   teammate_rate = TeamFactor.teammate_rate(
      [ factor ],
      factor.season,
      team,
      player_id )

   assert teammate_rate == factor.excluding( player_id )


def Test_Excluding_TestInjuredDefense_ExpectTeammatesWhenPlaying() -> None:
   extra_pace = 10.0
   regular_pace = 20.0
   extra = TeamFactorSkater(
      7,
      extra_pace,
      SkaterGroup( 'D' ),
      GamesShare.FULL,
      True,
      None )
   injured = TeamFactorSkater( 1, regular_pace, SkaterGroup( 'D' ), 0.5, False, None )
   rest = [
      TeamFactorSkater( index, regular_pace, SkaterGroup( 'D' ), GamesShare.FULL, False, None )
      for index in range( 2, 7 )
   ]
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      1.0,
      [ injured, extra, *rest ] )
   healthy = rest[ Position.FIRST ]

   total = factor.dressed_total()
   injured_teammates = factor.excluding( injured.player_id ) * total
   healthy_teammates = factor.excluding( healthy.player_id ) * total

   assert abs(
      injured_teammates
      - sum( skater.contribution for skater in rest ) ) < 0.001
   mixed = (
      injured.availability * injured.contribution
      + ( 1.0 - injured.availability ) * extra.contribution
      + sum(
         skater.contribution
         for skater in rest
         if skater.player_id != healthy.player_id ) )
   assert abs( healthy_teammates - mixed ) < 0.001


def Test_DressedTotal_TestHalfOut_ExpectCurrentMix() -> None:
   extra_pace = 10.0
   regular_pace = 20.0
   extra = TeamFactorSkater(
      7,
      extra_pace,
      SkaterGroup( 'D' ),
      GamesShare.FULL,
      True,
      None )
   injured = TeamFactorSkater( 1, regular_pace, SkaterGroup( 'D' ), 0.5, False, 0.5 )
   rest = [
      TeamFactorSkater( index, regular_pace, SkaterGroup( 'D' ), GamesShare.FULL, False, 0.5 )
      for index in range( 2, 7 )
   ]
   factor = TeamFactor(
      20262027,
      list( Team )[ Position.FIRST ],
      1.0,
      [ injured, extra, *rest ] )
   playing = [ injured, *rest ]
   healthy = sum( skater.contribution for skater in playing )
   filled = sum( skater.contribution for skater in rest ) + extra.contribution

   total = factor.dressed_total()

   assert abs(
      total
      - injured.availability * healthy
      - ( 1.0 - injured.availability ) * filled ) < 0.001
