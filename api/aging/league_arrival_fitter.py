from __future__ import annotations

from .league_arrival import LeagueArrival
from .league_arrival_totals import LeagueArrivalTotals
from ..recency.prior_year import PriorYear
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_season_years import SkaterSeasonYears


class LeagueArrivalFitter():
   """How a first NHL season arrives from another league the year before, age included."""

   MIN_ARRIVALS = 5
   MIN_NHL_GAMES = 10


   @classmethod
   def fit(
         cls,
         nhl_seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ] ) -> list[ LeagueArrival ]:
      history = SkaterSeasonYears.by_player( nhl_seasons )
      nhl_by_player = SkaterSeasonYears.by_player( [
         season for season in nhl_seasons
         if season.games_played >= cls.MIN_NHL_GAMES
      ] )
      totals: list[ LeagueArrivalTotals ] = []

      for season in other_seasons:
         if season.games_played < PriorYear.MIN_GAMES:
            continue

         if cls._already_played_in_nhl( history.get( season.player_id, [] ), season ):
            continue

         following = SkaterSeasonYears.at_year(
            nhl_by_player.get( season.player_id, [] ),
            Season.start_year( season.season_id ) + 1 )

         if following is None or season.g_pace + season.a_pace <= 0.0:
            continue

         cls._include( totals, season, following )

      return cls._arrivals( totals )


   @classmethod
   def _already_played_in_nhl(
         cls,
         seasons: list[ NhlSkaterSeason ],
         other: OtherLeagueSkaterSeason ) -> bool:
      year = Season.start_year( other.season_id )

      for season in seasons:
         if Season.start_year( season.season_id ) < year and season.games_played > 0:
            return True

      return False


   @classmethod
   def _include(
         cls,
         totals: list[ LeagueArrivalTotals ],
         other: OtherLeagueSkaterSeason,
         following: NhlSkaterSeason ) -> None:
      for index, total in enumerate( totals ):
         if total.matches( other ):
            totals[ index ] = total.adding( other, following )
            return

      totals.append( LeagueArrivalTotals.from_seasons( other, following ) )


   @classmethod
   def _arrivals( cls, totals: list[ LeagueArrivalTotals ] ) -> list[ LeagueArrival ]:
      arrivals: list[ LeagueArrival ] = []

      for total in sorted( totals, key=lambda total: ( total.league, total.age ) ):
         rate = total.rate()

         if total.arrival_count >= cls.MIN_ARRIVALS and rate is not None:
            arrivals.append( LeagueArrival( total.league, total.age, rate ) )

      return arrivals
