from __future__ import annotations

from dataclasses import replace

from api.aging.league_arrival import LeagueArrival
from api.aging.league_arrival_fitter import LeagueArrivalFitter
from api.recency.prior_year import PriorYear
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from tests.api.aging.league_factor_fitter_tests import _nhl, _other


def _full_other( player_id: int, season_id: int, age: float, league: str = 'AAA' ) -> OtherLeagueSkaterSeason:
   return replace(
      _other( player_id, season_id, league, age, 50.0, 50.0 ),
      games_played=PriorYear.MIN_GAMES )


def _full_nhl(
      player_id: int, season_id: int, age: float, g_pace: float = 20.0, a_pace: float = 20.0 ) -> NhlSkaterSeason:
   return replace(
      _nhl( player_id, season_id, age, g_pace, a_pace ),
      games_played=PriorYear.MIN_GAMES )


def Test_Fit_TestNextFullSeason_ExpectArrivalsAtThatAgeOnly() -> None:
   age = 18
   arrivals = [
      _full_other( player_id, 20242025, age )
      for player_id in range( LeagueArrivalFitter.MIN_ARRIVALS )
   ]
   following = [
      _full_nhl( player_id, 20252026, age + 1 )
      for player_id in range( LeagueArrivalFitter.MIN_ARRIVALS )
   ]
   same_year = _full_nhl( 0, 20242025, age, g_pace=80.0, a_pace=80.0 )
   cup = _full_nhl( 50, 20252026, age + 1.0, g_pace=90.0, a_pace=90.0 )
   cup = replace( cup, games_played=LeagueArrivalFitter.MIN_NHL_GAMES - 1 )
   cup_other = _full_other( 50, 20242025, age )
   thin = [
      _full_other( 100 + index, 20242025, 19 )
      for index in range( LeagueArrivalFitter.MIN_ARRIVALS - 1 )
   ]
   thin_nhl = [
      _full_nhl( 100 + index, 20252026, 20.2, g_pace=5.0, a_pace=5.0 )
      for index in range( LeagueArrivalFitter.MIN_ARRIVALS - 1 )
   ]

   fitted = LeagueArrivalFitter.fit(
      [ *following, same_year, cup, *thin_nhl ],
      [ *arrivals, cup_other, *thin ] )

   source = arrivals[ 0 ]
   assert fitted == [ LeagueArrival( source.league, age, ( 20.0 + 20.0 ) / ( source.g_pace + source.a_pace ) ) ]



def Test_Fit_TestPriorNhlSeason_ExpectLeftOut() -> None:
   age = 18
   arrivals = [
      _full_other( player_id, 20242025, age )
      for player_id in range( LeagueArrivalFitter.MIN_ARRIVALS )
   ]
   following = [
      _full_nhl( player_id, 20252026, age + 1 )
      for player_id in range( LeagueArrivalFitter.MIN_ARRIVALS )
   ]
   veteran_id = 90
   prior = _full_nhl( veteran_id, 20232024, age - 1, g_pace=80.0, a_pace=80.0 )
   short_prior = replace(
      _full_nhl( veteran_id + 1, 20232024, age - 1 ),
      games_played=PriorYear.MIN_GAMES - 1 )
   veteran_other = _full_other( veteran_id, 20242025, age )
   short_other = _full_other( veteran_id + 1, 20242025, age )
   veteran_next = _full_nhl( veteran_id, 20252026, age + 1, g_pace=90.0, a_pace=90.0 )
   short_next = _full_nhl( veteran_id + 1, 20252026, age + 1, g_pace=90.0, a_pace=90.0 )

   fitted = LeagueArrivalFitter.fit(
      [ *following, prior, short_prior, veteran_next, short_next ],
      [ *arrivals, veteran_other, short_other ] )

   source = arrivals[ 0 ]
   assert fitted == [ LeagueArrival( source.league, age, ( 20.0 + 20.0 ) / ( source.g_pace + source.a_pace ) ) ]



def Test_Fit_TestTenGameNhlSeason_ExpectIncluded() -> None:
   age = 18
   arrivals = [
      _full_other( player_id, 20242025, age )
      for player_id in range( LeagueArrivalFitter.MIN_ARRIVALS )
   ]
   following = [
      _full_nhl( player_id, 20252026, age + 1 )
      for player_id in range( LeagueArrivalFitter.MIN_ARRIVALS )
   ]
   short_id = 70
   short_games = LeagueArrivalFitter.MIN_NHL_GAMES
   short_other = _full_other( short_id, 20242025, age )
   short_nhl = replace(
      _full_nhl( short_id, 20252026, age + 1, g_pace=40.0, a_pace=40.0 ),
      games_played=short_games )
   below = replace(
      _full_nhl( short_id + 1, 20252026, age + 1, g_pace=90.0, a_pace=90.0 ),
      games_played=short_games - 1 )
   below_other = _full_other( short_id + 1, 20242025, age )
   full_games = PriorYear.MIN_GAMES
   full_nhl_pace = 40.0
   short_nhl_pace = 80.0
   other_pace = short_other.g_pace + short_other.a_pace
   nhl_points = LeagueArrivalFitter.MIN_ARRIVALS * full_games * full_nhl_pace + short_games * short_nhl_pace
   other_points = (
      LeagueArrivalFitter.MIN_ARRIVALS * full_games * other_pace + short_games * other_pace )

   fitted = LeagueArrivalFitter.fit(
      [ *following, short_nhl, below ],
      [ *arrivals, short_other, below_other ] )

   assert fitted == [ LeagueArrival( short_other.league, age, nhl_points / other_points ) ]
