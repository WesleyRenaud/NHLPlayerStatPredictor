from __future__ import annotations

from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season import SkaterSeason


def Test_CompletedAge_TestFractionalAge_ExpectTruncatedYears() -> None:
   season = SkaterSeason(
      player_id=1,
      season_id=20252026,
      age=28.7,
      games_played=82,
      goals=20,
      assists=30,
      points=50,
      g_pace=20.0,
      a_pace=30.0,
      position=SkaterPosition( 'C' ) )
   assert season.completed_age() == 28
