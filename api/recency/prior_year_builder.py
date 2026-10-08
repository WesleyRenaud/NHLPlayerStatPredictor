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
from ..projections.translated_pace_averager import TranslatedPaceAverager
from ..season import Season
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
      qualified = sorted(
         ( prior for prior in cls.history(
            seasons, factors, component_shares, player_ice_scales, arrivals, year - 1, scoring_growth )
            if prior.year < year ),
         key=lambda prior: prior.year,
         reverse=True )
      return qualified[ :PriorYearBuilder.WIDTH ]


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

      qualified: list[ PriorYear ] = []

      for start_year, year_seasons in by_year.items():
         combined = TranslatedPaceAverager.year( year_seasons, factors, component_shares, player_ice_scales )

         if combined is None or not combined.games:
            continue

         age = max( season.age for season in year_seasons )
         arrival = None

         if arrivals and scoring_growth is not None and start_year == entering_year:
            arrival = LeagueArrivalAverager.scoring(
               year_seasons,
               factors,
               arrivals,
               component_shares,
               ProductionHistoryPredictor.one_year_multiplier( scoring_growth, age ) )

         qualified.append(
            PriorYear(
               start_year,
               scoring=combined.scoring,
               pim_pace=combined.penalty_minutes,
               games=combined.games,
               nhl_games=combined.nhl_games,
               age=age,
               shots_pace=combined.shots,
               arrival=arrival ) )

      return qualified
