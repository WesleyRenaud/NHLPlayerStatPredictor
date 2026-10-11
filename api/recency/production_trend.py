from __future__ import annotations

from .prior_year import PriorYear
from .production_keep_band import ProductionKeepBand
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason


class ProductionTrend():
   # Seasons before the latest year. The line is fit on these, not on the latest year.
   PRIOR_SEASONS = 5

   STEEP_DECLINE = ProductionKeepBand( relative_slope_below=-0.078, kept_share=0.78 )
   MILD_DECLINE = ProductionKeepBand( relative_slope_below=-0.017, kept_share=0.52 )
   FLAT = ProductionKeepBand( relative_slope_below=0.031, kept_share=0.55 )
   MILD_RISE = ProductionKeepBand( relative_slope_below=0.096, kept_share=0.65 )
   STEEP_RISE_KEPT = 0.82


   @classmethod
   def kept( cls, relative_slope: float ) -> float:
      bands = ( cls.STEEP_DECLINE, cls.MILD_DECLINE, cls.FLAT, cls.MILD_RISE )

      for band in bands:
         if relative_slope < band.relative_slope_below:
            return band.kept_share

      return cls.STEEP_RISE_KEPT


   @classmethod
   def at_latest( cls, level: float, latest_pace: float, kept: float ) -> float:
      gap = latest_pace - level

      return level + kept * gap


   @classmethod
   def seasons(
         cls,
         nhl_seasons: list[ NhlSkaterSeason ],
         target_year: int ) -> list[ NhlSkaterSeason ] | None:
      by_year: dict[ int, list[ NhlSkaterSeason ] ] = {}

      for season in nhl_seasons:
         start_year = Season.start_year( season.season_id )

         if start_year < target_year:
            by_year.setdefault( start_year, [] ).append( season )

      latest_year = max( by_year, default=None )

      if latest_year is None:
         return None

      window: list[ NhlSkaterSeason ] = []

      for year in range( latest_year - cls.PRIOR_SEASONS, latest_year + 1 ):
         season = cls.full_season( by_year.get( year, [] ) )

         if season is None:
            return None

         window.append( season )

      return window


   @classmethod
   def full_season( cls, seasons: list[ NhlSkaterSeason ] ) -> NhlSkaterSeason | None:
      qualified = [
         season for season in seasons
         if season.games_played >= PriorYear.MIN_GAMES
      ]

      if len( qualified ) != 1:
         return None

      return qualified[ 0 ]
