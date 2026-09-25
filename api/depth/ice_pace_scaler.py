from __future__ import annotations

from ..projections.season_pace import SeasonPace


class IcePaceScaler():
   @classmethod
   def ratio( cls, last_toi: float, projected_toi: float ) -> float:
      return projected_toi / last_toi


   @classmethod
   def adjust(
         cls,
         pace: SeasonPace,
         last_toi: float,
         projected_toi: float ) -> SeasonPace:
      scale = cls.ratio( last_toi, projected_toi )
      return SeasonPace(
         goals=pace.goals * scale,
         assists=pace.assists * scale )
