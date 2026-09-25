from __future__ import annotations

from .depth_chart import DepthChart
from .ice_skater import IceSkater
from .skater_ice import SkaterIce


class SkaterIceRecorder():
   @classmethod
   def record( cls, charts: list[ DepthChart ] ) -> list[ SkaterIce ]:
      return [
         cls._row( skater, toi )
         for chart in charts
         for skater, toi in chart.regulars
      ]


   @classmethod
   def _row( cls, skater: IceSkater, toi: float ) -> SkaterIce:
      return SkaterIce( skater.player_id, skater.last_toi, skater.implied, toi )
