from __future__ import annotations

from .availability_enumerator import AvailabilityEnumerator
from .depth_chart import DepthChart
from .depth_core_builder import DepthCoreBuilder
from .depth_group import DepthGroup
from .ice_allocator import IceAllocator
from .ice_skater import IceSkater
from .ice_usage import IceUsage
from .last_core import LastCore
from .shared.enums.position import Position
from .slot_average import SlotAverage
from .team import Team


class DepthChartBuilder():
   @classmethod
   def build(
         cls,
         team: Team,
         skaters: list[ IceSkater ],
         slot_averages: list[ SlotAverage ],
         ice_usages: dict[ int, IceUsage ],
         season_length: int,
         group: DepthGroup,
         pace_games: int ) -> DepthChart:
      core = DepthCoreBuilder.build( skaters, group, slot_averages )
      projected = IceAllocator.project(
         core.regulars,
         core.extras,
         slot_averages,
         cls._prior_shares( team, ice_usages, season_length, group ),
         group )
      projected = sorted(
         projected,
         key=lambda item: (
            -item[ Position.LAST ],
            item[ Position.FIRST ].player_id ) )
      return DepthChart(
         team,
         projected,
         core.extras,
         AvailabilityEnumerator.games_out(
            [ skater for skater, _toi in projected ],
            pace_games ),
         group.skater_group )


   @classmethod
   def _prior_shares(
         cls,
         team: Team,
         ice_usages: dict[ int, IceUsage ],
         season_length: int,
         group: DepthGroup ) -> list[ float ]:
      return LastCore.shares(
         team,
         ice_usages,
         season_length,
         group.dressed_count,
         group.positions )
