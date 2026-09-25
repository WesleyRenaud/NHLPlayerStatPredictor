from __future__ import annotations

from dataclasses import replace

from .depth_group import DepthGroup
from .ice_chosen_share import IceChosenShare
from .ice_skater import IceSkater
from ..shared.enums.position import Position


class ChosenShareBinder():
   @classmethod
   def bind(
         cls,
         skaters: list[ IceSkater ],
         shares: list[ IceChosenShare ],
         group: DepthGroup ) -> list[ IceSkater ]:
      knots = sorted(
         [
            share
            for share in shares
            if share.skater_group is group.skater_group
         ],
         key=lambda share: share.toi )

      if not knots:
         return skaters

      return [
         replace(
            skater,
            availability=skater.availability * cls._chosen( skater.last_toi, knots ) )
         for skater in skaters
      ]


   @classmethod
   def _chosen(
         cls,
         last_toi: float | None,
         knots: list[ IceChosenShare ] ) -> float:
      if last_toi is None or last_toi <= knots[ Position.FIRST ].toi:
         return knots[ Position.FIRST ].chosen

      for low, high in zip( knots, knots[ Position.SECOND: ] ):
         if last_toi <= high.toi:
            return cls._between( last_toi, low, high )

      return knots[ Position.LAST ].chosen


   @classmethod
   def _between(
         cls,
         last_toi: float,
         low: IceChosenShare,
         high: IceChosenShare ) -> float:
      span = high.toi - low.toi

      if not span:
         return high.chosen

      weight = ( last_toi - low.toi ) / span
      return low.chosen + weight * ( high.chosen - low.chosen )
