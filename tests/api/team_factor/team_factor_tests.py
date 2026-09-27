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
