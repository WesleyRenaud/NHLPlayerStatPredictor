from __future__ import annotations

from datetime import date

from api.aging_pair_totals import AgingPairTotals
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.team import Team


def _season( g_pace: float, a_pace: float ) -> SkaterSeason:
   return SkaterSeason(
      player_id=1,
      season_id=20232024,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.0,
      team=list( Team )[ Position.FIRST ],
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0 )


def Test_Adding_TestPair_ExpectPaceAndChange() -> None:
   current = _season( 10.0, 20.0 )
   following = _season( 12.0, 18.0 )
   totals = AgingPairTotals.empty().adding( current, following )
   assert totals == AgingPairTotals(
      1,
      current.g_pace,
      current.a_pace,
      following.g_pace - current.g_pace,
      following.a_pace - current.a_pace )


def Test_Percent_TestTotals_ExpectRatioOfMeans() -> None:
   first = _season( 10.0, 20.0 )
   second = _season( 12.0, 22.0 )
   third = _season( 8.0, 18.0 )
   totals = AgingPairTotals.empty().adding( first, second ).adding( second, third )
   assert totals.percent() == (
      totals.goal_change / totals.goal_pace,
      totals.assist_change / totals.assist_pace )


def Test_Percent_TestZeroPace_ExpectNone() -> None:
   current = _season( 0.0, 20.0 )
   following = _season( 5.0, 22.0 )
   assert AgingPairTotals.empty().adding( current, following ).percent() is None
   assert AgingPairTotals.empty().percent() is None
