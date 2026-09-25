from __future__ import annotations

from datetime import date

from api.aging.aging_factor import AgingFactor
from api.aging.league_factor import LeagueFactor
from api.aging.league_factor_fitter import LeagueFactorFitter
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


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
      games_played=10,
      goals=1,
      assists=1,
      points=2,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Fit_TestSameYear_ExpectRatioOfMeans() -> None:
   league = 'AAA'
   first_nhl = _nhl( 1, 20252026, 20.2, 10.0, 20.0 )
   second_nhl = _nhl( 2, 20252026, 21.4, 30.0, 40.0 )
   first_other = _other( 1, 20252026, league, 20.2, 50.0, 80.0 )
   second_other = _other( 2, 20252026, league, 21.4, 90.0, 120.0 )

   factors = LeagueFactorFitter.fit(
      [ first_nhl, second_nhl ],
      [ first_other, second_other ],
      [] )

   assert factors == [
      LeagueFactor(
         league,
         ( first_nhl.g_pace + first_nhl.a_pace + second_nhl.g_pace + second_nhl.a_pace )
         / ( first_other.g_pace + first_other.a_pace + second_other.g_pace + second_other.a_pace ) )
   ]


def Test_Fit_TestLowPaceSwing_ExpectRatioOfMeansNotMeanOfPercents() -> None:
   league = 'AAA'
   first_nhl = _nhl( 1, 20252026, 20.1, 5.0, 5.0 )
   second_nhl = _nhl( 2, 20252026, 20.4, 40.0, 40.0 )
   first_other = _other( 1, 20252026, league, 20.1, 10.0, 10.0 )
   second_other = _other( 2, 20252026, league, 20.4, 40.0, 40.0 )

   factors = LeagueFactorFitter.fit(
      [ first_nhl, second_nhl ],
      [ first_other, second_other ],
      [] )

   assert factors == [
      LeagueFactor(
         league,
         ( first_nhl.g_pace + first_nhl.a_pace + second_nhl.g_pace + second_nhl.a_pace )
         / ( first_other.g_pace + first_other.a_pace + second_other.g_pace + second_other.a_pace ) )
   ]


def Test_Fit_TestConsecutiveYear_ExpectAgeAdjusted() -> None:
   league = 'AAA'
   aging = AgingFactor( 18, 0.10, 0.20 )
   other_goals = 100.0
   other_assists = 80.0
   nhl_goals = 40.0
   nhl_assists = 48.0
   nhl = _nhl( 1, 20242025, 19.2, nhl_goals, nhl_assists )
   other = _other( 1, 20232024, league, 18.2, other_goals, other_assists )
   aged_goals = other.g_pace * ( 1.0 + aging.goals )
   aged_assists = other.a_pace * ( 1.0 + aging.assists )

   factors = LeagueFactorFitter.fit( [ nhl ], [ other ], [ aging ] )

   assert factors == [
      LeagueFactor(
         league,
         ( nhl.g_pace + nhl.a_pace ) / ( aged_goals + aged_assists ) )
   ]


def Test_Fit_TestMissingAgingRow_ExpectSkipped() -> None:
   league = 'AAA'
   nhl = _nhl( 1, 20242025, 19.2, 40.0, 40.0 )
   other = _other( 1, 20232024, league, 18.2, 100.0, 100.0 )

   factors = LeagueFactorFitter.fit( [ nhl ], [ other ], [] )

   assert factors == []


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
         ( same_nhl.g_pace + same_nhl.a_pace ) / ( other.g_pace + other.a_pace ) )
   ]


def Test_Fit_TestUnevenGoalsAndAssists_ExpectSharedPointsRate() -> None:
   league = 'AAA'
   nhl = _nhl( 1, 20252026, 20.2, 10.0, 20.0 )
   other = _other( 1, 20252026, league, 20.2, 10.0, 80.0 )

   factors = LeagueFactorFitter.fit( [ nhl ], [ other ], [] )

   assert factors == [
      LeagueFactor(
         league,
         ( nhl.g_pace + nhl.a_pace ) / ( other.g_pace + other.a_pace ) )
   ]


def Test_Fit_TestZeroNhlPace_ExpectSkipped() -> None:
   league = 'AAA'
   nhl = _nhl( 1, 20252026, 20.2, 0.0, 0.0 )
   other = _other( 1, 20252026, league, 20.2, 50.0, 80.0 )

   factors = LeagueFactorFitter.fit( [ nhl ], [ other ], [] )

   assert factors == []


def Test_Fit_TestReverseYear_ExpectAgeAdjustedBack() -> None:
   league = 'AAA'
   aging = AgingFactor( 24, 0.10, 0.20 )
   nhl = _nhl( 1, 20232024, 24.2, 22.0, 36.0 )
   other = _other( 1, 20242025, league, 25.2, 50.0, 80.0 )
   aged_goals = other.g_pace / ( 1.0 + aging.goals )
   aged_assists = other.a_pace / ( 1.0 + aging.assists )

   factors = LeagueFactorFitter.fit( [ nhl ], [ other ], [ aging ] )

   assert factors == [
      LeagueFactor(
         league,
         ( nhl.g_pace + nhl.a_pace ) / ( aged_goals + aged_assists ) )
   ]
