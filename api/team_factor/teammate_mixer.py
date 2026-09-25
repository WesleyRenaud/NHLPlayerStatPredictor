from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from ..availability.availability_enumerator import AvailabilityEnumerator
from ..availability.games_share import GamesShare
from ..depth.depth_group import DepthGroup
from ..depth.dressed_points_builder import DressedPointsBuilder
from ..depth.slot_average import SlotAverage
from .mix_delta import MixDelta
from .teammate_skater import TeammateSkater


class TeammateMixer():
   @classmethod
   def expected(
         cls,
         regulars: list[ TeammateSkater ],
         extras: list[ TeammateSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> float:
      return cls._delta(
         regulars,
         lambda present: cls._expected(
            present,
            extras,
            slot_averages,
            group ) )


   @classmethod
   def teammates(
         cls,
         player_id: int,
         regulars: list[ TeammateSkater ],
         extras: list[ TeammateSkater ],
         slot_averages: list[ SlotAverage ],
         group: DepthGroup ) -> float:
      player = cls._regular( player_id, regulars )

      if player is not None:
         return cls._delta(
            regulars,
            lambda present: cls._regular_teammates(
               next(
                  skater
                  for skater in present
                  if skater.player_id == player_id ),
               present,
               extras,
               slot_averages,
               group ) )

      index = cls._extra_index( player_id, extras )

      if index is not None:
         return cls._delta(
            regulars,
            lambda present: cls._extra_teammates(
               index,
               present,
               extras,
               slot_averages,
               group ) )

      return cls.expected( regulars, extras, slot_averages, group )


   @classmethod
   def _delta(
         cls,
         regulars: list[ TeammateSkater ],
         compute: Callable[ [ list[ TeammateSkater ] ], float ] ) -> float:
      current = compute( regulars )

      if any( skater.prior_availability is None for skater in regulars ):
         return current

      prior = [
         replace( skater, availability=skater.prior_availability )
         for skater in regulars
      ]
      healthy = [
         replace( skater, availability=GamesShare.FULL )
         for skater in regulars
      ]
      return MixDelta.resolve(
         current,
         compute( prior ),
         compute( healthy ) )


   @classmethod
   def _expected(
         cls,
         regulars: list[ TeammateSkater ],
         extras: list[ TeammateSkater ],
         fills: list[ SlotAverage ],
         group: DepthGroup ) -> float:
      total = 0.0
      weight = 0.0

      for state in AvailabilityEnumerator.resolve( regulars ):
         total += state.share * DressedPointsBuilder.build(
            list( state.playing ),
            extras,
            fills,
            group ).total
         weight += state.share

      return total / weight


   @classmethod
   def _regular_teammates(
         cls,
         player: TeammateSkater,
         regulars: list[ TeammateSkater ],
         extras: list[ TeammateSkater ],
         slots: list[ SlotAverage ],
         group: DepthGroup ) -> float:
      others = [
         skater
         for skater in regulars
         if skater.player_id != player.player_id
      ]
      total = 0.0
      weight = 0.0

      for state in AvailabilityEnumerator.resolve( others ):
         dressed = DressedPointsBuilder.build(
            [ player, *state.playing ],
            extras,
            slots,
            group ).total
         total += state.share * ( dressed - player.contribution )
         weight += state.share

      return total / weight


   @classmethod
   def _extra_teammates(
         cls,
         index: int,
         regulars: list[ TeammateSkater ],
         extras: list[ TeammateSkater ],
         slots: list[ SlotAverage ],
         group: DepthGroup ) -> float:
      extra = extras[ index ]
      total = 0.0
      weight = 0.0

      for state in AvailabilityEnumerator.resolve( regulars ):
         open_slots = group.dressed_count - len( state.playing )

         if open_slots <= index:
            continue

         dressed = DressedPointsBuilder.build(
            list( state.playing ),
            extras,
            slots,
            group ).total
         total += state.share * ( dressed - extra.contribution )
         weight += state.share

      if not weight:
         return cls._expected( regulars, extras, slots, group )

      return total / weight


   @classmethod
   def _regular(
         cls,
         player_id: int,
         regulars: list[ TeammateSkater ] ) -> TeammateSkater | None:
      for skater in regulars:
         if skater.player_id == player_id:
            return skater

      return None


   @classmethod
   def _extra_index(
         cls,
         player_id: int,
         extras: list[ TeammateSkater ] ) -> int | None:
      for index, skater in enumerate( extras ):
         if skater.player_id == player_id:
            return index

      return None
