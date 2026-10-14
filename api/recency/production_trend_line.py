from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class ProductionTrendLine():
   level: float


   @classmethod
   def fit( cls, paces: list[ float ] ) -> ProductionTrendLine:
      count = len( paces )
      years = list( range( count ) )
      mean_year = ( count - 1 ) / 2.0
      mean_pace = sum( paces ) / count
      variance = sum( ( year - mean_year ) ** 2 for year in years )
      slope = sum(
         ( year - mean_year ) * ( pace - mean_pace )
         for year, pace in zip( years, paces, strict=True ) ) / variance
      newest_year = count - 1
      level = mean_pace + slope * ( newest_year - mean_year )

      return cls( level )
