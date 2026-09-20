from __future__ import annotations

from datetime import date

from api.aging_curve_fitter import AgingCurveFitter
from api.aging_factor import AgingFactor
from api.club_league import ClubLeague
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


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
      position=list( SkaterPosition )[ Position.FIRST ],
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
      age=age,
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Fit_TestConsecutiveSeasons_ExpectRatioOfMeans() -> None:
   seasons = [
      _season( 1, 20232024, 24.2, 10.0, 20.0 ),
      _season( 1, 20242025, 25.2, 12.0, 22.0 ),
      _season( 2, 20232024, 24.8, 30.0, 40.0 ),
      _season( 2, 20242025, 25.8, 24.0, 32.0 ),
   ]
   mean_goals = 10.0 + 30.0
   mean_assists = 20.0 + 40.0
   assert AgingCurveFitter.fit( seasons, [] ) == [
      AgingFactor(
         24,
         ( ( 12.0 - 10.0 ) + ( 24.0 - 30.0 ) ) / mean_goals,
         ( ( 22.0 - 20.0 ) + ( 32.0 - 40.0 ) ) / mean_assists )
   ]


def Test_Fit_TestLowPaceSwing_ExpectRatioOfMeansNotMeanOfPercents() -> None:
   seasons = [
      _season( 1, 20232024, 24.1, 5.0, 5.0 ),
      _season( 1, 20242025, 25.1, 10.0, 10.0 ),
      _season( 2, 20232024, 24.4, 40.0, 40.0 ),
      _season( 2, 20242025, 25.4, 40.0, 40.0 ),
   ]
   mean_pace = 5.0 + 40.0
   delta = ( 10.0 - 5.0 ) + ( 40.0 - 40.0 )
   rate = delta / mean_pace
   assert AgingCurveFitter.fit( seasons, [] ) == [
      AgingFactor( 24, rate, rate )
   ]


def Test_Fit_TestGapYear_ExpectSkipped() -> None:
   seasons = [
      _season( 1, 20222023, 24.1, 20.0, 20.0 ),
      _season( 1, 20242025, 26.1, 40.0, 40.0 ),
   ]
   assert AgingCurveFitter.fit( seasons, [] ) == []


def Test_Fit_TestNeighborRates_ExpectCountWeighted() -> None:
   seasons = [
      _season( 1, 20212022, 24.1, 10.0, 10.0 ),
      _season( 1, 20222023, 25.1, 11.0, 11.0 ),
      _season( 2, 20212022, 25.1, 10.0, 10.0 ),
      _season( 2, 20222023, 26.1, 10.0, 10.0 ),
      _season( 3, 20222023, 25.2, 10.0, 10.0 ),
      _season( 3, 20232024, 26.2, 10.0, 10.0 ),
      _season( 4, 20222023, 25.3, 10.0, 10.0 ),
      _season( 4, 20232024, 26.3, 10.0, 10.0 ),
      _season( 5, 20222023, 26.1, 10.0, 10.0 ),
      _season( 5, 20232024, 27.1, 9.0, 9.0 ),
   ]
   n_24 = 1
   n_25 = 3
   n_26 = 1
   rate_24 = ( 11.0 - 10.0 ) / 10.0
   rate_25 = 0.0
   rate_26 = ( 9.0 - 10.0 ) / 10.0
   total = n_24 + n_25 + n_26
   smoothed = ( n_24 * rate_24 + n_25 * rate_25 + n_26 * rate_26 ) / total
   factors = AgingCurveFitter.fit( seasons, [] )
   by_age = { factor.age: factor for factor in factors }
   assert by_age[ 25 ] == AgingFactor( 25, smoothed, smoothed )


def Test_Fit_TestSameLeagueOtherSeasons_ExpectRatioOfMeans() -> None:
   league = list( ClubLeague )[ Position.FIRST ].value
   other_seasons = [
      _other( 1, 20232024, league, 16.2, 10.0, 20.0 ),
      _other( 1, 20242025, league, 17.2, 12.0, 22.0 ),
      _other( 2, 20232024, league, 16.8, 30.0, 40.0 ),
      _other( 2, 20242025, league, 17.8, 24.0, 32.0 ),
   ]
   mean_goals = 10.0 + 30.0
   mean_assists = 20.0 + 40.0
   assert AgingCurveFitter.fit( [], other_seasons ) == [
      AgingFactor(
         16,
         ( ( 12.0 - 10.0 ) + ( 24.0 - 30.0 ) ) / mean_goals,
         ( ( 22.0 - 20.0 ) + ( 32.0 - 40.0 ) ) / mean_assists )
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
   assert AgingCurveFitter.fit( [], other_seasons ) == []


def Test_Fit_TestNhlAndOtherSeasons_ExpectBothAges() -> None:
   league = list( ClubLeague )[ Position.FIRST ].value
   seasons = [
      _season( 1, 20232024, 24.2, 10.0, 20.0 ),
      _season( 1, 20242025, 25.2, 12.0, 22.0 ),
   ]
   other_seasons = [
      _other( 2, 20232024, league, 16.2, 10.0, 20.0 ),
      _other( 2, 20242025, league, 17.2, 12.0, 22.0 ),
   ]
   factors = AgingCurveFitter.fit( seasons, other_seasons )
   by_age = { factor.age: factor for factor in factors }
   assert by_age[ 16 ] == AgingFactor(
      16,
      ( 12.0 - 10.0 ) / 10.0,
      ( 22.0 - 20.0 ) / 20.0 )
   assert by_age[ 24 ] == AgingFactor(
      24,
      ( 12.0 - 10.0 ) / 10.0,
      ( 22.0 - 20.0 ) / 20.0 )


def Test_Fit_TestPastLastAge_ExpectOmitted() -> None:
   seasons = [
      _season( 1, 20222023, 40.2, 10.0, 20.0 ),
      _season( 1, 20232024, 41.2, 8.0, 16.0 ),
      _season( 1, 20242025, 42.2, 4.0, 8.0 ),
   ]
   assert AgingCurveFitter.fit( seasons, [] ) == [
      AgingFactor(
         AgingCurveFitter.LAST_AGE,
         ( 8.0 - 10.0 ) / 10.0,
         ( 16.0 - 20.0 ) / 20.0 )
   ]
