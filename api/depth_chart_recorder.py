from __future__ import annotations

from .availability_projector import AvailabilityProjector
from .availability_weight_store import AvailabilityWeightStore
from .depth_chart import DepthChart
from .depth_chart_builder import DepthChartBuilder
from .depth_chart_store import DepthChartStore
from .depth_group import DepthGroup
from .ice_skater_assembler import IceSkaterAssembler
from .ice_usage import IceUsage
from .ice_usage_parser import IceUsageParser
from .nhl_client import NhlClient
from .nhl_only_season_filter import NhlOnlySeasonFilter
from .other_league_season_provider import OtherLeagueSeasonProvider
from .paths import Paths
from .recency_target_resolver import RecencyTargetResolver
from .roster_skater import RosterSkater
from .roster_skater_ingester import RosterSkaterIngester
from .season import Season
from .skater_season_provider import SkaterSeasonProvider
from .skater_season_years import SkaterSeasonYears
from .slot_average import SlotAverage
from .slot_average_store import SlotAverageStore
from .team import Team


class DepthChartRecorder():
   @classmethod
   def main( cls, force: bool = False ) -> None:
      seasons = NhlClient.seasons( force=force )
      DepthChartStore.write(
         cls.record(
            Season.pace_games( seasons ),
            force ) )


   @classmethod
   def record(
         cls,
         pace_games: int,
         force: bool = False ) -> list[ DepthChart ]:
      ice_usages = IceUsageParser.parse(
         NhlClient.skater_timeonice( RecencyTargetResolver.prior(), force ) )
      roster = RosterSkaterIngester.build_rows( force=force )
      availabilities = cls._availabilities( roster )
      slot_averages = SlotAverageStore.read()
      charts = []

      for team in cls._teams( roster ):
         charts.extend(
            cls._team_charts(
               team,
               roster,
               ice_usages,
               availabilities,
               slot_averages,
               pace_games ) )

      return charts


   @classmethod
   def _team_charts(
         cls,
         team: Team,
         roster: list[ RosterSkater ],
         ice_usages: dict[ int, IceUsage ],
         availabilities: dict[ int, float ],
         slot_averages: list[ SlotAverage ],
         pace_games: int ) -> list[ DepthChart ]:
      charts = []

      for group in ( DepthGroup.forwards(), DepthGroup.defense() ):
         print(
            f'Recording depth chart { team.value } { group.label }...',
            flush=True )
         charts.append(
            DepthChartBuilder.build(
               team,
               IceSkaterAssembler.build(
                  group.skaters( roster, team ),
                  ice_usages,
                  availabilities ),
               slot_averages,
               group,
               pace_games ) )

      return charts


   @classmethod
   def _availabilities( cls, roster: list[ RosterSkater ] ) -> dict[ int, float ]:
      player_ids = [ row.player_id for row in roster ]
      by_player = SkaterSeasonYears.by_player(
         NhlOnlySeasonFilter.keep(
            SkaterSeasonProvider.seasons_for_player_ids(
               player_ids,
               Paths.DB_PATH ),
            OtherLeagueSeasonProvider.seasons_for_player_ids(
               player_ids,
               Paths.DB_PATH ) ) )
      weights = AvailabilityWeightStore.read()
      target = RecencyTargetResolver.resolve()
      return {
         player_id: AvailabilityProjector.resolve(
            by_player.get( player_id, [] ),
            weights,
            target )
         for player_id in player_ids
      }


   @classmethod
   def _teams( cls, roster: list[ RosterSkater ] ) -> list[ Team ]:
      teams: list[ Team ] = []
      seen: set[ Team ] = set()

      for row in roster:
         if row.team in seen:
            continue

         seen.add( row.team )
         teams.append( row.team )

      return sorted( teams, key=lambda team: team.value )
