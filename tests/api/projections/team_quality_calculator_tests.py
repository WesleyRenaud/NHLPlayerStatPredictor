from __future__ import annotations

from api.projections.career_pace import CareerPace
from api.projections.last_season_skater import LastSeasonSkater
from api.projections.team_quality_calculator import TeamQualityCalculator


def _skater( player_id: int, games: float, points: float ) -> LastSeasonSkater:
   return LastSeasonSkater(
      player_id=player_id,
      games=games,
      pace=CareerPace( points / 2.0, points / 2.0 ) )


def Test_Average_TestEmpty_ExpectNone() -> None:
   assert TeamQualityCalculator.average( [] ) is None


def Test_Average_TestMixedGames_ExpectGamesWeightedPoints() -> None:
   heavy = _skater( 1, 80.0, 100.0 )
   light = _skater( 2, 20.0, 20.0 )
   total = heavy.games + light.games
   assert TeamQualityCalculator.average( [ heavy, light ] ) == (
      heavy.games * ( heavy.pace.goals + heavy.pace.assists )
      + light.games * ( light.pace.goals + light.pace.assists ) ) / total
