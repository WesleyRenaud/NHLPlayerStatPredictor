from __future__ import annotations

from collections import defaultdict

from ..aging.league_factor import LeagueFactor
from .prior_year import PriorYear
from ..projections.translated_pace_averager import TranslatedPaceAverager
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.skater_season import SkaterSeason


class PriorYearBuilder():
   WIDTH = 3


   @classmethod
   def build(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ],
         year: int ) -> list[ PriorYear ]:
      qualified = sorted(
         cls._qualified( seasons, factors, year ),
         key=lambda prior: prior.year,
         reverse=True )
      run = qualified[ :1 ]

      for prior in qualified[ 1: ]:
         if len( run ) == PriorYearBuilder.WIDTH or prior.year != run[ Position.LAST ].year - 1:
            break

         run.append( prior )

      return run


   @classmethod
   def _qualified(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ],
         year: int ) -> list[ PriorYear ]:
      by_year: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         start_year = Season.start_year( season.season_id )

         if start_year < year:
            by_year[ start_year ].append( season )

      qualified: list[ PriorYear ] = []

      for start_year, year_seasons in by_year.items():
         combined = TranslatedPaceAverager.year( year_seasons, factors )

         if combined is None or combined.games < PriorYear.MIN_GAMES:
            continue

         qualified.append(
            PriorYear(
               start_year,
               combined.pace,
               combined.games,
               sum(
                  season.games_played
                  for season in year_seasons
                  if isinstance( season, NhlSkaterSeason ) ),
               max( season.age for season in year_seasons ) ) )

      return qualified
