from __future__ import annotations

from ..availability.availability_enumerator import AvailabilityEnumerator
from .chosen_share_binder import ChosenShareBinder
from .depth_chart import DepthChart
from .depth_core_builder import DepthCoreBuilder
from .depth_group import DepthGroup
from .ice_allocator import IceAllocator
from .ice_chosen_share import IceChosenShare
from .ice_skater import IceSkater
from ..shared.enums.position import Position
from ..skaters.team import Team
from .slot_average import SlotAverage


class DepthChartBuilder():
   @classmethod
   def build(
         cls,
         team: Team,
         skaters: list[ IceSkater ],
         slot_averages: list[ SlotAverage ],
         chosen_shares: list[ IceChosenShare ],
         group: DepthGroup,
         pace_games: int ) -> DepthChart:
      core = DepthCoreBuilder.build( skaters, group, slot_averages )
      regulars = ChosenShareBinder.bind(
         core.regulars,
         chosen_shares,
         group )
      projected = IceAllocator.project(
         regulars,
         core.extras,
         slot_averages,
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
