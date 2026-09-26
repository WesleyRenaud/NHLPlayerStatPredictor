from __future__ import annotations

from datetime import date

from api.aging.aging_season_paces import AgingSeasonPaces
from api.depth.usable_nhl_ice import UsableNhlIce
from api.projections.player_aging_fitter import PlayerAgingFitter
from api.projections.player_aging_rate import PlayerAgingRate
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _season(
      season_id: int,
      g_pace: float,
      a_pace: float,
      games_played: int = 1,
      goals: int = 0,
      assists: int = 0 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.0,
      team=list( Team )[ Position.FIRST ],
      games_played=games_played,
      goals=goals,
      assists=assists,
      points=goals + assists,
      schedule_games=1,
      pace_games=1,
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0 )


def Test_Fit_TestConsecutiveSeasons_ExpectRatioOfMeans() -> None:
   first = _season( 20212022, 10.0, 20.0 )
   second = _season( 20222023, 12.0, 22.0 )
   third = _season( 20232024, 8.0, 18.0 )
   seasons = [ first, second, third ]

   rate = PlayerAgingFitter.fit( seasons )

   assert rate == PlayerAgingRate(
      2,
      ( ( second.g_pace - first.g_pace ) + ( third.g_pace - second.g_pace ) )
      / ( first.g_pace + second.g_pace ),
      ( ( second.a_pace - first.a_pace ) + ( third.a_pace - second.a_pace ) )
      / ( first.a_pace + second.a_pace ) )


def Test_Fit_TestLowPaceSwing_ExpectRatioOfMeansNotMeanOfPercents() -> None:
   first = _season( 20222023, 5.0, 5.0 )
   second = _season( 20232024, 10.0, 10.0 )
   third = _season( 20242025, 10.0, 10.0 )
   seasons = [ first, second, third ]

   rate = PlayerAgingFitter.fit( seasons )

   assert rate == PlayerAgingRate(
      2,
      ( ( second.g_pace - first.g_pace ) + ( third.g_pace - second.g_pace ) )
      / ( first.g_pace + second.g_pace ),
      ( ( second.a_pace - first.a_pace ) + ( third.a_pace - second.a_pace ) )
      / ( first.a_pace + second.a_pace ) )


def Test_Fit_TestGapYear_ExpectSkipped() -> None:
   seasons = [
      _season( 20212022, 20.0, 20.0 ),
      _season( 20232024, 40.0, 40.0 ),
   ]

   rate = PlayerAgingFitter.fit( seasons )

   assert rate is None


def Test_Fit_TestOneAssistGame_ExpectBorrowedMixAndBothPairs() -> None:
   coffee = _season( 20232024, 0.0, 84.0, games_played=1, assists=1 )
   rookie = _season(
      20242025,
      20.0,
      24.0,
      games_played=UsableNhlIce.MIN_GAMES,
      goals=20,
      assists=24 )
   jump = _season(
      20252026,
      40.0,
      30.0,
      games_played=UsableNhlIce.MIN_GAMES,
      goals=40,
      assists=30 )
   seasons = [ coffee, rookie, jump ]
   coffee_goals, coffee_assists = AgingSeasonPaces.resolve( coffee, rookie )

   rate = PlayerAgingFitter.fit( seasons )

   assert rate == PlayerAgingRate(
      2,
      ( ( rookie.g_pace - coffee_goals ) + ( jump.g_pace - rookie.g_pace ) )
      / ( coffee_goals + rookie.g_pace ),
      ( ( rookie.a_pace - coffee_assists ) + ( jump.a_pace - rookie.a_pace ) )
      / ( coffee_assists + rookie.a_pace ) )


def Test_Fit_TestOlderThanWindow_ExpectRecentPairsOnly() -> None:
   old = _season( 20182019, 100.0, 100.0 )
   first = _season( 20192020, 10.0, 10.0 )
   second = _season( 20202021, 10.0, 10.0 )
   third = _season( 20212022, 10.0, 10.0 )
   fourth = _season( 20222023, 10.0, 10.0 )
   fifth = _season( 20232024, 10.0, 10.0 )
   seasons = [ old, first, second, third, fourth, fifth ]

   rate = PlayerAgingFitter.fit( seasons )

   assert rate == PlayerAgingRate(
      PlayerAgingFitter.WINDOW,
      (
         ( second.g_pace - first.g_pace )
         + ( third.g_pace - second.g_pace )
         + ( fourth.g_pace - third.g_pace )
         + ( fifth.g_pace - fourth.g_pace )
      ) / ( first.g_pace + second.g_pace + third.g_pace + fourth.g_pace ),
      (
         ( second.a_pace - first.a_pace )
         + ( third.a_pace - second.a_pace )
         + ( fourth.a_pace - third.a_pace )
         + ( fifth.a_pace - fourth.a_pace )
      ) / ( first.a_pace + second.a_pace + third.a_pace + fourth.a_pace ) )
