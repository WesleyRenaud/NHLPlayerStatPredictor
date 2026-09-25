from __future__ import annotations

from ..availability.availability_projector import AvailabilityProjector
from ..availability.availability_weight_store import AvailabilityWeightStore
from ..availability.mixed_season_share_binder import MixedSeasonShareBinder
from ..availability.retired_availability_binder import RetiredAvailabilityBinder
from .club_ice import ClubIce
from .club_ice_provider import ClubIceProvider
from .depth_chart import DepthChart
from .depth_chart_builder import DepthChartBuilder
from .depth_chart_store import DepthChartStore
from .depth_group import DepthGroup
from .ice_skater_assembler import IceSkaterAssembler
from .ice_usage import IceUsage
from .ice_usage_parser import IceUsageParser
from ..ingest.nhl_client import NhlClient
from ..ingest.roster_skater_ingester import RosterSkaterIngester
from ..paths import Paths
from ..recency_target_resolver import RecencyTargetResolver
from .retired_roster_binder import RetiredRosterBinder
from ..season import Season
from ..skaters.other_league_season_provider import OtherLeagueSeasonProvider
from ..skaters.player_status_store import PlayerStatusStore
from ..skaters.roster_skater import RosterSkater
from ..skaters.skater_season_provider import SkaterSeasonProvider
from ..skaters.skater_season_years import SkaterSeasonYears
from ..skaters.team import Team
from .slot_average import SlotAverage
from .slot_average_store import SlotAverageStore
from .slot_chosen_share import SlotChosenShare
from .slot_chosen_share_store import SlotChosenShareStore
from ..team_factor.team_factor_store import TeamFactorStore


class DepthChartRecorder():
   @classmethod
   def main( cls, force: bool = False ) -> None:
      seasons = NhlClient.seasons( force=force )
      DepthChartStore.write(
         cls.record(
            Season.pace_games( seasons ),
            cls._team_rates(),
            force ) )


   @classmethod
   def record(
         cls,
         pace_games: int,
         team_rates: dict[ Team, float ],
         force: bool = False ) -> list[ DepthChart ]:
      prior = RecencyTargetResolver.prior()
      ice_usages = IceUsageParser.parse(
         NhlClient.skater_timeonice( prior, force ) )
      ices_by_player = {
         player_id: ClubIceProvider.resolve( player_id, prior )
         for player_id in ice_usages
      }
      roster = RosterSkaterIngester.build_rows( force=force )
      statuses = PlayerStatusStore.read( str( Paths.DB_PATH ) )
      roster = RetiredRosterBinder.bind(
         roster,
         ice_usages,
         statuses,
         cls._names( RetiredRosterBinder.missing( roster, ice_usages, statuses ) ) )
      availabilities = RetiredAvailabilityBinder.bind(
         cls._availabilities( roster ),
         statuses )
      slot_averages = SlotAverageStore.read()
      chosen_shares = SlotChosenShareStore.read()
      charts = []

      for team in cls._teams( roster ):
         charts.extend(
            cls._team_charts(
               team,
               roster,
               ice_usages,
               availabilities,
               slot_averages,
               chosen_shares,
               pace_games,
               team_rates,
               ices_by_player ) )

      return charts


   @classmethod
   def _team_charts(
         cls,
         team: Team,
         roster: list[ RosterSkater ],
         ice_usages: dict[ int, IceUsage ],
         availabilities: dict[ int, float ],
         slot_averages: list[ SlotAverage ],
         chosen_shares: list[ SlotChosenShare ],
         pace_games: int,
         team_rates: dict[ Team, float ],
         ices_by_player: dict[ int, list[ ClubIce ] ] ) -> list[ DepthChart ]:
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
                  availabilities,
                  team_rates,
                  ices_by_player ),
               slot_averages,
               chosen_shares,
               group,
               pace_games ) )

      return charts


   @classmethod
   def _availabilities( cls, roster: list[ RosterSkater ] ) -> dict[ int, float ]:
      player_ids = [ row.player_id for row in roster ]
      by_player = SkaterSeasonYears.by_player(
         MixedSeasonShareBinder.bind(
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
   def _names( cls, player_ids: list[ int ] ) -> dict[ int, str ]:
      if not player_ids:
         return {}

      names = {}

      for season in SkaterSeasonProvider.seasons_for_player_ids(
            player_ids,
            Paths.DB_PATH ):
         names[ season.player_id ] = season.player_name

      return names


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


   @classmethod
   def _team_rates( cls ) -> dict[ Team, float ]:
      prior = RecencyTargetResolver.prior()
      return {
         factor.team: factor.rate
         for factor in TeamFactorStore.read()
         if factor.season == prior
      }
