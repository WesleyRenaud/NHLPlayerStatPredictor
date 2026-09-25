from __future__ import annotations

from datetime import date

from api.aging.aging_curve_fitter import AgingCurveFitter
from api.aging.aging_factor import AgingFactor
from api.shared.enums.position import Position
from api.skaters.club_league import ClubLeague
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _season(
      player_id: int,
      season_id: int,
      age: float,
      g_pace: float,
      a_pace: float ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=age,
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


def _other(
      player_id: int,
      season_id: int,
      league: str,
      age: float,
      g_pace: float,
      a_pace: float ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      league=league,
      position=SkaterPosition( 'C' ),
      age=age,
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Fit_TestConsecutiveSeasons_ExpectRatioOfMeans() -> None:
   first = _season( 1, 20232024, 24.2, 10.0, 20.0 )
   first_next = _season( 1, 20242025, 25.2, 12.0, 22.0 )
   second = _season( 2, 20232024, 24.8, 30.0, 40.0 )
   second_next = _season( 2, 20242025, 25.8, 24.0, 32.0 )
   seasons = [ first, first_next, second, second_next ]
   goal_pace = first.g_pace + second.g_pace
   assist_pace = first.a_pace + second.a_pace

   factors = AgingCurveFitter.fit( seasons, [] )

   assert factors == [
      AgingFactor(
         first.completed_age(),
         ( ( first_next.g_pace - first.g_pace ) + ( second_next.g_pace - second.g_pace ) )
         / goal_pace,
         ( ( first_next.a_pace - first.a_pace ) + ( second_next.a_pace - second.a_pace ) )
         / assist_pace )
   ]


def Test_Fit_TestLowPaceSwing_ExpectRatioOfMeansNotMeanOfPercents() -> None:
   first = _season( 1, 20232024, 24.1, 5.0, 5.0 )
   first_next = _season( 1, 20242025, 25.1, 10.0, 10.0 )
   second = _season( 2, 20232024, 24.4, 40.0, 40.0 )
   second_next = _season( 2, 20242025, 25.4, 40.0, 40.0 )
   seasons = [ first, first_next, second, second_next ]
   goal_pace = first.g_pace + second.g_pace
   assist_pace = first.a_pace + second.a_pace
   goal_change = ( first_next.g_pace - first.g_pace ) + ( second_next.g_pace - second.g_pace )
   assist_change = ( first_next.a_pace - first.a_pace ) + ( second_next.a_pace - second.a_pace )

   factors = AgingCurveFitter.fit( seasons, [] )

   assert factors == [
      AgingFactor(
         first.completed_age(),
         goal_change / goal_pace,
         assist_change / assist_pace )
   ]


def Test_Fit_TestGapYear_ExpectSkipped() -> None:
   seasons = [
      _season( 1, 20222023, 24.1, 20.0, 20.0 ),
      _season( 1, 20242025, 26.1, 40.0, 40.0 ),
   ]

   factors = AgingCurveFitter.fit( seasons, [] )

   assert factors == []


def Test_Fit_TestNeighborRates_ExpectCountWeighted() -> None:
   age_24 = _season( 1, 20212022, 24.1, 10.0, 10.0 )
   age_24_next = _season( 1, 20222023, 25.1, 11.0, 11.0 )
   first_25 = _season( 2, 20212022, 25.1, 10.0, 10.0 )
   first_25_next = _season( 2, 20222023, 26.1, 10.0, 10.0 )
   second_25 = _season( 3, 20222023, 25.2, 10.0, 10.0 )
   second_25_next = _season( 3, 20232024, 26.2, 10.0, 10.0 )
   third_25 = _season( 4, 20222023, 25.3, 10.0, 10.0 )
   third_25_next = _season( 4, 20232024, 26.3, 10.0, 10.0 )
   age_26 = _season( 5, 20222023, 26.1, 10.0, 10.0 )
   age_26_next = _season( 5, 20232024, 27.1, 9.0, 9.0 )
   seasons = [
      age_24,
      age_24_next,
      first_25,
      first_25_next,
      second_25,
      second_25_next,
      third_25,
      third_25_next,
      age_26,
      age_26_next,
   ]
   n_24 = 1
   n_25 = 3
   n_26 = 1
   rate_24 = ( age_24_next.g_pace - age_24.g_pace ) / age_24.g_pace
   rate_25 = ( first_25_next.g_pace - first_25.g_pace ) / first_25.g_pace
   rate_26 = ( age_26_next.g_pace - age_26.g_pace ) / age_26.g_pace
   smoothed = ( n_24 * rate_24 + n_25 * rate_25 + n_26 * rate_26 ) / ( n_24 + n_25 + n_26 )
   mid_age = first_25.completed_age()

   factors = AgingCurveFitter.fit( seasons, [] )

   assert next( factor for factor in factors if factor.age == mid_age ) == AgingFactor(
      mid_age,
      smoothed,
      smoothed )


def Test_Fit_TestSameLeagueOtherSeasons_ExpectRatioOfMeans() -> None:
   league = list( ClubLeague )[ Position.FIRST ].value
   first = _other( 1, 20232024, league, 16.2, 10.0, 20.0 )
   first_next = _other( 1, 20242025, league, 17.2, 12.0, 22.0 )
   second = _other( 2, 20232024, league, 16.8, 30.0, 40.0 )
   second_next = _other( 2, 20242025, league, 17.8, 24.0, 32.0 )
   other_seasons = [ first, first_next, second, second_next ]
   goal_pace = first.g_pace + second.g_pace
   assist_pace = first.a_pace + second.a_pace

   factors = AgingCurveFitter.fit( [], other_seasons )

   assert factors == [
      AgingFactor(
         first.completed_age(),
         ( ( first_next.g_pace - first.g_pace ) + ( second_next.g_pace - second.g_pace ) )
         / goal_pace,
         ( ( first_next.a_pace - first.a_pace ) + ( second_next.a_pace - second.a_pace ) )
         / assist_pace )
   ]


def Test_Fit_TestCrossLeagueOtherSeasons_ExpectSkipped() -> None:
   other_seasons = [
      _other(
         1,
         20232024,
         list( ClubLeague )[ Position.FIRST ].value,
         16.2,
         10.0,
         20.0 ),
      _other(
         1,
         20242025,
         list( ClubLeague )[ Position.SECOND ].value,
         17.2,
         12.0,
         22.0 ),
   ]

   factors = AgingCurveFitter.fit( [], other_seasons )

   assert factors == []


def Test_Fit_TestNhlAndOtherSeasons_ExpectBothAges() -> None:
   league = list( ClubLeague )[ Position.FIRST ].value
   nhl = _season( 1, 20232024, 24.2, 10.0, 20.0 )
   nhl_next = _season( 1, 20242025, 25.2, 12.0, 22.0 )
   other = _other( 2, 20232024, league, 16.2, 10.0, 20.0 )
   other_next = _other( 2, 20242025, league, 17.2, 12.0, 22.0 )
   nhl_goals = ( nhl_next.g_pace - nhl.g_pace ) / nhl.g_pace
   nhl_assists = ( nhl_next.a_pace - nhl.a_pace ) / nhl.a_pace
   other_goals = ( other_next.g_pace - other.g_pace ) / other.g_pace
   other_assists = ( other_next.a_pace - other.a_pace ) / other.a_pace

   factors = AgingCurveFitter.fit( [ nhl, nhl_next ], [ other, other_next ] )

   assert next( factor for factor in factors if factor.age == other.completed_age() ) == AgingFactor(
      other.completed_age(),
      other_goals,
      other_assists )
   assert next( factor for factor in factors if factor.age == nhl.completed_age() ) == AgingFactor(
      nhl.completed_age(),
      nhl_goals,
      nhl_assists )


def Test_Fit_TestPastLastAge_ExpectOmitted() -> None:
   first = _season( 1, 20222023, 40.2, 10.0, 20.0 )
   second = _season( 1, 20232024, 41.2, 8.0, 16.0 )
   third = _season( 1, 20242025, 42.2, 4.0, 8.0 )
   seasons = [ first, second, third ]

   factors = AgingCurveFitter.fit( seasons, [] )

   assert factors == [
      AgingFactor(
         AgingCurveFitter.LAST_AGE,
         ( second.g_pace - first.g_pace ) / first.g_pace,
         ( second.a_pace - first.a_pace ) / first.a_pace )
   ]
