from __future__ import annotations

from ..availability.availability_projector import AvailabilityProjector
from ..availability.availability_weight_store import AvailabilityWeightStore
from ..availability.mixed_season_share_binder import MixedSeasonShareBinder
from ..availability.retired_availability_binder import RetiredAvailabilityBinder
from .club_ice_provider import ClubIceProvider
from .depth_chart import DepthChart
from .depth_chart_builder import DepthChartBuilder
from .depth_chart_store import DepthChartStore
from .depth_group import DepthGroup
from .ice_skater_assembler import IceSkaterAssembler
from ..ingest.nhl_client import NhlClient
from ..ingest.roster_skater_ingester import RosterSkaterIngester
from ..paths import Paths
from ..recency_target_resolver import RecencyTargetResolver
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
from .usable_nhl_ice import UsableNhlIce


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
      roster = RosterSkaterIngester.build_rows( force=force )
      statuses = PlayerStatusStore.read( str( Paths.DB_PATH ) )
      availabilities = RetiredAvailabilityBinder.bind(
         cls._availabilities( roster ),
         statuses )
      slot_averages = SlotAverageStore.read()
      chosen_shares = SlotChosenShareStore.read()
      ices_by_player = cls._ices_by_player( roster )
      charts = []

      for team in cls._teams( roster ):
         charts.extend(
            cls._team_charts(
               team,
               roster,
               ices_by_player,
               availabilities,
               slot_averages,
               chosen_shares,
               pace_games,
               team_rates ) )

      return charts


   @classmethod
   def _team_charts(
         cls,
         team: Team,
         roster: list[ RosterSkater ],
         ices_by_player: dict[ int, UsableNhlIce | None ],
         availabilities: dict[ int, float ],
         slot_averages: list[ SlotAverage ],
         chosen_shares: list[ SlotChosenShare ],
         pace_games: int,
         team_rates: dict[ Team, float ] ) -> list[ DepthChart ]:
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
                  ices_by_player,
                  availabilities,
                  team_rates ),
               slot_averages,
               chosen_shares,
               group,
               pace_games ) )

      return charts


   @classmethod
   def _ices_by_player(
         cls,
         roster: list[ RosterSkater ] ) -> dict[ int, UsableNhlIce | None ]:
      return {
         row.player_id: ClubIceProvider.resolve( row.player_id )
         for row in roster
      }


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
