from __future__ import annotations

from api.aging.aging_pair_totals import AgingPairTotals
from api.aging.aging_season_paces import AgingSeasonPaces
from api.depth.usable_nhl_ice import UsableNhlIce
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season import SkaterSeason


def _season(
      g_pace: float,
      a_pace: float,
      games_played: int = 1,
      goals: int = 0,
      assists: int = 0 ) -> SkaterSeason:
   return SkaterSeason(
      player_id=1,
      season_id=20232024,
      age=28.0,
      games_played=games_played,
      goals=goals,
      assists=assists,
      points=goals + assists,
      g_pace=g_pace,
      a_pace=a_pace,
      position=SkaterPosition( 'C' ) )


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

   percent = totals.percent()

   assert percent == (
      totals.goal_change / totals.goal_pace,
      totals.assist_change / totals.assist_pace )


def Test_Adding_TestOneAssistGameThenFull_ExpectBorrowedMix() -> None:
   thin = _season( 0.0, 84.0, games_played=1, assists=1 )
   full = _season( 20.0, 24.0, games_played=UsableNhlIce.MIN_GAMES, goals=20, assists=24 )
   thin_goals, thin_assists = AgingSeasonPaces.resolve( thin, full )
   full_goals, full_assists = AgingSeasonPaces.resolve( full, thin )

   totals = AgingPairTotals.empty().adding( thin, full )

   assert totals == AgingPairTotals(
      1,
      thin_goals,
      thin_assists,
      full_goals - thin_goals,
      full_assists - thin_assists )


def Test_Percent_TestZeroPace_ExpectNone() -> None:
   current = _season( 0.0, 20.0 )
   following = _season( 5.0, 22.0 )

   added = AgingPairTotals.empty().adding( current, following ).percent()
   empty = AgingPairTotals.empty().percent()

   assert added is None
   assert empty is None
