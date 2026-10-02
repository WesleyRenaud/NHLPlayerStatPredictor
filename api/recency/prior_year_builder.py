from __future__ import annotations

from collections import defaultdict

from ..aging.league_factor import LeagueFactor
from .prior_year import PriorYear
from ..projections.season_pace import SeasonPace
from ..projections.translated_pace_averager import TranslatedPaceAverager
from ..season import Season
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
      return qualified[ :PriorYearBuilder.WIDTH ]


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
               pace=SeasonPace( combined.goals, combined.assists ),
               power_play_pace=combined.power_play_pace(),
               short_handed_pace=combined.short_handed_pace(),
               pim_pace=combined.penalty_minutes,
               games=combined.games,
               nhl_games=sum(
                  season.games_played
                  for season in year_seasons
                  if isinstance( season, NhlSkaterSeason ) ),
               age=max( season.age for season in year_seasons ),
               playoff_surplus=cls._playoff_surplus( year_seasons ) ) )

      return qualified


   @classmethod
   def _playoff_surplus( cls, year_seasons: list[ SkaterSeason ] ) -> SeasonPace:
      for season in year_seasons:
         if isinstance( season, NhlSkaterSeason ):
            return season.playoff_surplus()

      return SeasonPace.zero()
