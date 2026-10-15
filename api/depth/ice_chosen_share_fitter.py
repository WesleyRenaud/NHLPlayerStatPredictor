from __future__ import annotations

from ..availability.games_share import GamesShare
from .depth_group import DepthGroup
from .ice_chosen_share import IceChosenShare
from .ice_usage import IceUsage
from ..shared.enums.position import Position
from .usable_nhl_ice import UsableNhlIce


class IceChosenShareFitter():
   @classmethod
   def fit(
         cls,
         usages: dict[ int, IceUsage ],
         season_length: int,
         group: DepthGroup ) -> list[ IceChosenShare ]:
      return cls._shares( cls._binned( usages, season_length ), group )


   @classmethod
   def _binned(
         cls,
         usages: dict[ int, IceUsage ],
         season_length: int ) -> dict[ float, list[ float ] ]:
      by_toi: dict[ float, list[ float ] ] = {}

      for usage in usages.values():
         if usage.games < UsableNhlIce.MIN_GAMES:
            continue

         by_toi.setdefault( cls._bin( usage.toi ), [] ).append(
            GamesShare.resolve( usage.games, season_length ) )

      return by_toi


   @classmethod
   def _shares(
         cls,
         by_toi: dict[ float, list[ float ] ],
         group: DepthGroup ) -> list[ IceChosenShare ]:
      if not by_toi:
         return []

      tois = sorted( by_toi, reverse=True )
      reference = cls._mean( by_toi[ tois[ Position.FIRST ] ] )
      ceiling = GamesShare.FULL
      shares = []

      for toi in tois:
         dress_share = cls._mean( by_toi[ toi ] )
         chosen = cls._chosen( dress_share, reference, ceiling )
         ceiling = chosen
         shares.append(
            IceChosenShare(
               toi,
               group.skater_group,
               dress_share,
               chosen ) )

      return sorted( shares, key=lambda share: share.toi )


   @classmethod
   def _chosen(
         cls,
         dress_share: float,
         reference: float,
         ceiling: float ) -> float:
      if not reference:
         return GamesShare.FULL

      return min( ceiling, GamesShare.FULL, dress_share / reference )


   @classmethod
   def _bin( cls, toi: float ) -> float:
      return float( round( toi ) )


   @classmethod
   def _mean( cls, shares: list[ float ] ) -> float:
      return sum( shares ) / len( shares )
