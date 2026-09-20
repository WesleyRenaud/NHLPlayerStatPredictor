from __future__ import annotations

from datetime import date

from api.aging_factor import AgingFactor
from api.league_factor import LeagueFactor
from api.league_factor_fitter import LeagueFactorFitter
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _nhl(
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
      games_played=10,
      goals=1,
      assists=1,
      points=2,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Fit_TestSameYear_ExpectRatioOfMeans() -> None:
   league = 'AAA'
   factors = LeagueFactorFitter.fit(
      [
         _nhl( 1, 20252026, 20.2, 10.0, 20.0 ),
         _nhl( 2, 20252026, 21.4, 30.0, 40.0 ),
      ],
      [
         _other( 1, 20252026, league, 20.2, 50.0, 80.0 ),
         _other( 2, 20252026, league, 21.4, 90.0, 120.0 ),
      ],
      [] )
   assert factors == [
      LeagueFactor(
         league,
         ( 10.0 + 30.0 ) / ( 50.0 + 90.0 ),
         ( 20.0 + 40.0 ) / ( 80.0 + 120.0 ) )
   ]


def Test_Fit_TestLowPaceSwing_ExpectRatioOfMeansNotMeanOfPercents() -> None:
   league = 'AAA'
   factors = LeagueFactorFitter.fit(
      [
         _nhl( 1, 20252026, 20.1, 5.0, 5.0 ),
         _nhl( 2, 20252026, 20.4, 40.0, 40.0 ),
      ],
      [
         _other( 1, 20252026, league, 20.1, 10.0, 10.0 ),
         _other( 2, 20252026, league, 20.4, 40.0, 40.0 ),
      ],
      [] )
   rate = ( 5.0 + 40.0 ) / ( 10.0 + 40.0 )
   assert factors == [ LeagueFactor( league, rate, rate ) ]


def Test_Fit_TestConsecutiveYear_ExpectAgeAdjusted() -> None:
   league = 'AAA'
   aging = AgingFactor( 18, 0.10, 0.20 )
   other_goals = 100.0
   other_assists = 80.0
   nhl_goals = 40.0
   nhl_assists = 48.0
   factors = LeagueFactorFitter.fit(
      [ _nhl( 1, 20242025, 19.2, nhl_goals, nhl_assists ) ],
      [ _other( 1, 20232024, league, 18.2, other_goals, other_assists ) ],
      [ aging ] )
   assert factors == [
      LeagueFactor(
         league,
         nhl_goals / ( other_goals * ( 1.0 + aging.goals ) ),
         nhl_assists / ( other_assists * ( 1.0 + aging.assists ) ) )
   ]


def Test_Fit_TestMissingAgingRow_ExpectSkipped() -> None:
   league = 'AAA'
   assert LeagueFactorFitter.fit(
      [ _nhl( 1, 20242025, 19.2, 40.0, 40.0 ) ],
      [ _other( 1, 20232024, league, 18.2, 100.0, 100.0 ) ],
      [] ) == []


def Test_Fit_TestSameYearAndNext_ExpectSameYearPair() -> None:
   league = 'AAA'
   same_nhl = _nhl( 1, 20232024, 18.2, 20.0, 30.0 )
   next_nhl = _nhl( 1, 20242025, 19.2, 80.0, 90.0 )
   other = _other( 1, 20232024, league, 18.2, 40.0, 60.0 )
   factors = LeagueFactorFitter.fit(
      [ same_nhl, next_nhl ],
      [ other ],
      [ AgingFactor( 18, 0.50, 0.50 ) ] )
   assert factors == [
      LeagueFactor(
         league,
         same_nhl.g_pace / other.g_pace,
         same_nhl.a_pace / other.a_pace )
   ]


def Test_Fit_TestZeroNhlPace_ExpectSkipped() -> None:
   league = 'AAA'
   assert LeagueFactorFitter.fit(
      [ _nhl( 1, 20252026, 20.2, 0.0, 0.0 ) ],
      [ _other( 1, 20252026, league, 20.2, 50.0, 80.0 ) ],
      [] ) == []


def Test_Fit_TestReverseYear_ExpectAgeAdjustedBack() -> None:
   league = 'AAA'
   aging = AgingFactor( 24, 0.10, 0.20 )
   nhl = _nhl( 1, 20232024, 24.2, 22.0, 36.0 )
   other = _other( 1, 20242025, league, 25.2, 50.0, 80.0 )
   factors = LeagueFactorFitter.fit( [ nhl ], [ other ], [ aging ] )
   assert factors == [
      LeagueFactor(
         league,
         nhl.g_pace / ( other.g_pace / ( 1.0 + aging.goals ) ),
         nhl.a_pace / ( other.a_pace / ( 1.0 + aging.assists ) ) )
   ]
