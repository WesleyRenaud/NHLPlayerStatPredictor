from __future__ import annotations

from collections import defaultdict

from ..aging.league_arrival import LeagueArrival
from ..aging.league_arrival_averager import LeagueArrivalAverager
from ..aging.league_factor import LeagueFactor
from ..depth.nhl_player_season_ice_scale import NhlPlayerSeasonIceScale
from .prior_year import PriorYear
from .production_growth import ProductionGrowth
from .production_history_predictor import ProductionHistoryPredictor
from ..projections.scoring_component_shares import ScoringComponentShares
from ..projections.scoring_paces import ScoringPaces
from ..projections.translated_pace_averager import TranslatedPaceAverager
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_season import SkaterSeason


class PriorYearBuilder():
   WIDTH = 3


   @classmethod
   def build(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ],
         year: int,
         component_shares: list[ ScoringComponentShares ],
         player_ice_scales: list[ NhlPlayerSeasonIceScale ] | None = None,
         arrivals: list[ LeagueArrival ] | None = None,
         scoring_growth: list[ ProductionGrowth ] | None = None ) -> list[ PriorYear ]:
      priors = [
         prior for prior in cls.history(
            seasons, factors, component_shares, player_ice_scales, arrivals, year - 1, scoring_growth )
         if prior.year < year
      ]
      qualified = cls._without_other_leagues( priors )
      return sorted( qualified, key=lambda prior: prior.year, reverse=True )[ :cls.WIDTH ]


   @classmethod
   def history(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ],
         component_shares: list[ ScoringComponentShares ],
         player_ice_scales: list[ NhlPlayerSeasonIceScale ] | None = None,
         arrivals: list[ LeagueArrival ] | None = None,
         entering_year: int | None = None,
         scoring_growth: list[ ProductionGrowth ] | None = None ) -> list[ PriorYear ]:
      by_year: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         start_year = Season.start_year( season.season_id )

         by_year[ start_year ].append( season )

      established = cls._is_established( by_year, entering_year )
      qualified: list[ PriorYear ] = []

      for start_year, year_seasons in by_year.items():
         production = cls._production_seasons( year_seasons, established )
         combined = TranslatedPaceAverager.year(
            production, factors, component_shares, player_ice_scales )

         if combined is None or not combined.games:
            continue

         age = max( season.age for season in production )
         qualified.append(
            PriorYear(
               start_year,
               scoring=combined.scoring,
               pim_pace=combined.penalty_minutes,
               games=combined.games,
               nhl_games=combined.nhl_games,
               age=age,
               shots_pace=combined.shots,
               arrival=cls._arrival(
                  production,
                  factors,
                  arrivals,
                  component_shares,
                  scoring_growth,
                  start_year,
                  entering_year,
                  established,
                  age ) ) )

      return qualified


   @classmethod
   def _without_other_leagues( cls, priors: list[ PriorYear ] ) -> list[ PriorYear ]:
      if any( prior.nhl_games >= PriorYear.MIN_GAMES for prior in priors ):
         return [ prior for prior in priors if prior.nhl_games ]

      return priors


   @classmethod
   def _is_established(
         cls,
         seasons_by_year: dict[ int, list[ SkaterSeason ] ],
         entering_year: int | None ) -> bool:
      return any(
         cls._nhl_games( year_seasons ) >= PriorYear.MIN_GAMES
         for year, year_seasons in seasons_by_year.items()
         if entering_year is None or year <= entering_year )


   @classmethod
   def _nhl_games( cls, seasons: list[ SkaterSeason ] ) -> int:
      return sum(
         season.games_played
         for season in seasons
         if isinstance( season, NhlSkaterSeason ) )


   @classmethod
   def _production_seasons(
         cls,
         seasons: list[ SkaterSeason ],
         established: bool ) -> list[ SkaterSeason ]:
      nhl = [
         season for season in seasons
         if isinstance( season, NhlSkaterSeason ) and season.games_played ]
      other = [
         season for season in seasons
         if isinstance( season, OtherLeagueSkaterSeason ) and season.games_played ]

      if established and nhl:
         return nhl

      if not established and other and cls._nhl_games( seasons ) < PriorYear.MIN_GAMES:
         return other

      return [ season for season in seasons if season.games_played ]


   @classmethod
   def _arrival(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ],
         arrivals: list[ LeagueArrival ] | None,
         component_shares: list[ ScoringComponentShares ],
         scoring_growth: list[ ProductionGrowth ] | None,
         start_year: int,
         entering_year: int | None,
         established: bool,
         age: int ) -> ScoringPaces | None:
      if established or start_year != entering_year or not arrivals or scoring_growth is None:
         return None

      return LeagueArrivalAverager.scoring(
         seasons,
         factors,
         arrivals,
         component_shares,
         ProductionHistoryPredictor.one_year_multiplier( scoring_growth, age ) )
