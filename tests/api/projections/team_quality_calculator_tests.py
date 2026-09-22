from __future__ import annotations

from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.previous_season_skater import PreviousSeasonSkater
from api.projections.season_pace import SeasonPace
from api.projections.team_quality_calculator import TeamQualityCalculator
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _skater( player_id: int, games: int, points: float ) -> PreviousSeasonSkater:
   return PreviousSeasonSkater(
      player_id=player_id,
      games=games,
      pace=SeasonPace( points / 2.0, points / 2.0 ),
      position=SkaterPosition( 'C' ) )


def Test_Average_TestEmpty_ExpectNone() -> None:
   assert TeamQualityCalculator.average( [] ) is None


def Test_Average_TestMixedGames_ExpectGamesWeightedPoints() -> None:
   heavy = _skater( 1, 80, 100.0 )
   light = _skater( 2, 20, 20.0 )
   assert TeamQualityCalculator.average( [ heavy, light ] ) == (
      ( heavy.contribution + light.contribution )
      / ( 80 + 20 ) )


def Test_Total_TestProjected_ExpectPaceSum() -> None:
   team = list( Team )[ Position.FIRST ]
   heavy = CurrentSeasonNhlSkater(
      1,
      SeasonPace( 50.0, 50.0 ),
      team,
      SkaterPosition( 'C' ) )
   light = CurrentSeasonNhlSkater(
      2,
      SeasonPace( 10.0, 10.0 ),
      team,
      SkaterPosition( 'C' ) )
   assert TeamQualityCalculator.total( [ heavy, light ] ) == (
      heavy.contribution + light.contribution )


def Test_Total_TestMixedGames_ExpectGamesWeightedSum() -> None:
   team = list( Team )[ Position.FIRST ]
   heavy = PreviousSeasonNhlSkater(
      1,
      80,
      SeasonPace( 50.0, 50.0 ),
      SkaterPosition( 'C' ),
      team )
   light = PreviousSeasonNhlSkater(
      2,
      20,
      SeasonPace( 10.0, 10.0 ),
      SkaterPosition( 'C' ),
      team )
   assert TeamQualityCalculator.total( [ heavy, light ] ) == (
      heavy.contribution + light.contribution )
