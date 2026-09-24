from __future__ import annotations

from .availability_binder import AvailabilityBinder
from .availability_enumerator import AvailabilityEnumerator
from .depth_group import DepthGroup
from .dressed_lineup_builder import DressedLineupBuilder
from .games_share import GamesShare
from .ice_skater import IceSkater
from .mix_delta import MixDelta
from .slot_average import SlotAverage


class IceAllocator():
   @classmethod
   def project(
         cls,
         regulars: list[ IceSkater ],
         extras: list[ IceSkater ],
         slot_averages: list[ SlotAverage ],
         prior_shares: list[ float ],
         group: DepthGroup ) -> list[ tuple[ IceSkater, float ] ]:
      prior = cls._prior( regulars, prior_shares )
      healthy = cls._healthy( regulars )
      return [
         (
            skater,
            cls._toi(
               skater,
               regulars,
               extras,
               slot_averages,
               prior,
               healthy,
               group ) )
         for skater in regulars
      ]


   @classmethod
   def _toi(
         cls,
         skater: IceSkater,
         regulars: list[ IceSkater ],
         extras: list[ IceSkater ],
         slot_averages: list[ SlotAverage ],
         prior: list[ IceSkater ],
         healthy: list[ IceSkater ],
         group: DepthGroup ) -> float:
      current = cls._mix(
         skater,
         regulars,
         extras,
         slot_averages,
         group )

      index = [ row.player_id for row in regulars ].index( skater.player_id )
      return MixDelta.resolve(
         current,
         cls._mix( prior[ index ], prior, extras, slot_averages, group ),
         cls._mix( healthy[ index ], healthy, extras, slot_averages, group ) )


   @classmethod
   def _mix(
         cls,
         skater: IceSkater,
         regulars: list[ IceSkater ],
         extras: list[ IceSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> float:
      others = [
         other
         for other in regulars
         if other.player_id != skater.player_id
      ]
      total = 0.0
      weight = 0.0

      for state in AvailabilityEnumerator.resolve( others ):
         denom = DressedLineupBuilder.build(
            [ skater, *state.playing ],
            extras,
            slot_averages,
            group ).implied
         total += state.share * group.ice_minutes * skater.implied / denom
         weight += state.share

      return total / weight


   @classmethod
   def _prior(
         cls,
         regulars: list[ IceSkater ],
         shares: list[ float ] ) -> list[ IceSkater ]:
      return AvailabilityBinder.bind( regulars, shares )


   @classmethod
   def _healthy(
         cls,
         regulars: list[ IceSkater ] ) -> list[ IceSkater ]:
      return AvailabilityBinder.bind(
         regulars,
         [ GamesShare.FULL ] * len( regulars ) )
