from __future__ import annotations

from collections import defaultdict

from ..aging.league_factor import LeagueFactor
from .prior_year import PriorYear
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
         component_shares: list[ ScoringComponentShares ] ) -> list[ PriorYear ]:
      qualified = sorted(
         ( prior for prior in cls.history( seasons, factors, component_shares ) if prior.year < year ),
         key=lambda prior: prior.year,
         reverse=True )
      return qualified[ :PriorYearBuilder.WIDTH ]


   @classmethod
   def history(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ],
         component_shares: list[ ScoringComponentShares ] ) -> list[ PriorYear ]:
      by_year: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         start_year = Season.start_year( season.season_id )

         by_year[ start_year ].append( season )

      qualified: list[ PriorYear ] = []

      for start_year, year_seasons in by_year.items():
         combined = TranslatedPaceAverager.year( year_seasons, factors, component_shares )

         if combined is None or not combined.games:
            continue

         qualified.append(
            PriorYear(
               start_year,
               scoring=combined.scoring,
               pim_pace=combined.penalty_minutes,
               games=combined.games,
               nhl_games=combined.nhl_games,
               age=max( season.age for season in year_seasons ),
               shots_pace=combined.shots ) )

      return qualified
