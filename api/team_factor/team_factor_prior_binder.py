from __future__ import annotations

from ..depth.depth_chart import DepthChart
from ..depth.depth_group import DepthGroup
from ..depth.ice_usage import IceUsage
from ..depth.last_core import LastCore
from ..depth.last_toi import LastToi
from .teammate_skater import TeammateSkater


class TeamFactorPriorBinder():
   @classmethod
   def bind(
         cls,
         regulars: list[ TeammateSkater ],
         chart: DepthChart,
         usages: dict[ int, IceUsage ],
         season_length: int,
         group: DepthGroup ) -> list[ TeammateSkater ]:
      shares = LastCore.shares(
         chart.team,
         usages,
         season_length,
         group.dressed_count,
         group.positions )
      assigned = {
         player_id: shares[ index ]
         for index, player_id in enumerate( cls._rank_ids( chart ) )
      }
      return [
         TeammateSkater(
            skater.player_id,
            skater.contribution,
            skater.availability,
            assigned[ skater.player_id ] )
         for skater in regulars
      ]


   @classmethod
   def _rank_ids( cls, chart: DepthChart ) -> list[ int ]:
      ranked = sorted(
         [ skater for skater, _toi in chart.regulars ],
         key=lambda skater: LastToi.key( skater.player_id, skater.implied ) )
      return [ skater.player_id for skater in ranked ]
