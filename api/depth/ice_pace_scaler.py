from __future__ import annotations

from dataclasses import replace
from typing import overload

from ..projections.power_play_pace import PowerPlayPace
from ..projections.season_pace import SeasonPace

class IcePaceScaler():
   @classmethod
   def ratio( cls, last_toi: float, projected_toi: float ) -> float:
      return projected_toi / last_toi


   @overload
   @classmethod
   def adjust(
         cls: type[ IcePaceScaler ],
         pace: SeasonPace,
         last_toi: float,
         projected_toi: float ) -> SeasonPace: ...


   @overload
   @classmethod
   def adjust(
         cls: type[ IcePaceScaler ],
         pace: PowerPlayPace,
         last_toi: float,
         projected_toi: float ) -> PowerPlayPace: ...


   @classmethod
   def adjust(
         cls,
         pace: SeasonPace | PowerPlayPace,
         last_toi: float,
         projected_toi: float ) -> SeasonPace | PowerPlayPace:
      scale = cls.ratio( last_toi, projected_toi )
      return replace(
         pace,
         goals=pace.goals * scale,
         assists=pace.assists * scale )
