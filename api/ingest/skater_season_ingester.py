from __future__ import annotations

from ..aging.aging_curve_fitter import AgingCurveFitter
from ..aging.aging_factor_store import AgingFactorStore
from ..aging.league_factor_fitter import LeagueFactorFitter
from ..aging.league_factor_store import LeagueFactorStore
from ..availability.availability_decay_fitter import AvailabilityDecayFitter
from ..availability.availability_weight_store import AvailabilityWeightStore
from ..availability.mixed_season_share_binder import MixedSeasonShareBinder
from ..depth.depth_chart_recorder import DepthChartRecorder
from ..depth.depth_chart_store import DepthChartStore
from ..depth.depth_group import DepthGroup
from ..depth.ice_chosen_share_fitter import IceChosenShareFitter
from ..depth.ice_chosen_share_store import IceChosenShareStore
from ..depth.ice_usage_parser import IceUsageParser
from ..depth.skater_ice_recorder import SkaterIceRecorder
from ..depth.skater_ice_store import SkaterIceStore
from ..depth.slot_average_fitter import SlotAverageFitter
from ..depth.slot_average_store import SlotAverageStore
from .nhl_client import NhlClient
from .other_league_season_ingester import OtherLeagueSeasonIngester
from ..paths import Paths
from .player_landing_fetcher import PlayerLandingFetcher
from .previous_team_factor_builder import PreviousTeamFactorBuilder
from ..projections.baseline_roster_pace_builder import BaselineRosterPaceBuilder
from ..projections.season_pace import SeasonPace
from ..recency.recency_decay_fitter import RecencyDecayFitter
from ..recency.scoring_weight_store import ScoringWeightStore
from ..recency_target_resolver import RecencyTargetResolver
from .roster_skater_ingester import RosterSkaterIngester
from ..season import Season
from .skater_season_builder import SkaterSeasonBuilder
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_season_store import OtherLeagueSeasonStore
from ..skaters.player_status_builder import PlayerStatusBuilder
from ..skaters.player_status_store import PlayerStatusStore
from ..skaters.roster_skater import RosterSkater
from ..skaters.roster_skater_store import RosterSkaterStore
from ..skaters.skater_season_store import SkaterSeasonStore
from ..team_factor.team_factor_fitter import TeamFactorFitter
from ..team_factor.team_factor_store import TeamFactorStore


class SkaterSeasonIngester():
   @classmethod
   def main( cls, force: bool = False ) -> None:
      rows = SkaterSeasonBuilder.build_all( force=force )
      SkaterSeasonStore.insert_rows( rows, str( Paths.DB_PATH ) )
      roster_rows = RosterSkater.with_last_played(
         RosterSkaterIngester.build_rows( force=force ),
         rows )
      RosterSkaterStore.insert_rows( roster_rows, str( Paths.DB_PATH ) )
      player_ids = cls._player_ids( rows, roster_rows )
      landings = PlayerLandingFetcher.fetch( player_ids, force=force )
      other_rows = OtherLeagueSeasonIngester.build_rows(
         player_ids,
         landings,
         NhlClient.seasons( force=force ),
         Season.pace_games( NhlClient.seasons( force=force ) ) )
      OtherLeagueSeasonStore.insert_rows( other_rows, str( Paths.DB_PATH ) )
      PlayerStatusStore.insert_rows(
         PlayerStatusBuilder.build_all( player_ids, landings ),
         str( Paths.DB_PATH ) )
      weights = RecencyDecayFitter.fit( rows )
      ScoringWeightStore.write( weights )
      AvailabilityWeightStore.write(
         AvailabilityDecayFitter.fit(
            MixedSeasonShareBinder.bind( rows, other_rows ) ) )
      aging_factors = AgingCurveFitter.fit( rows, other_rows )
      AgingFactorStore.write( aging_factors )
      league_factors = LeagueFactorFitter.fit( rows, other_rows, aging_factors )
      LeagueFactorStore.write( league_factors )
      previous_season_id = RecencyTargetResolver.prior()
      current_season = RecencyTargetResolver.resolve()
      seasons = NhlClient.seasons( force=force )
      last_played_ids = sorted( {
         previous_season_id,
         *(
            row.last_played_season_id
            for row in roster_rows
            if row.last_played_season_id is not None ) } )
      usages_by_season = {
         season_id: IceUsageParser.parse(
            NhlClient.skater_timeonice( season_id, force ) )
         for season_id in last_played_ids
      }
      usages = usages_by_season[ previous_season_id ]
      paces = {
         row.player_id: SeasonPace( row.g_pace, row.a_pace )
         for row in rows
         if row.season_id == previous_season_id
      }
      d_usages = {
         player_id: usage
         for player_id, usage in usages.items()
         if DepthGroup.defense().contains( usage.position )
      }
      f_usages = {
         player_id: usage
         for player_id, usage in usages.items()
         if DepthGroup.forwards().contains( usage.position )
      }
      slots = SlotAverageFitter.fit(
         d_usages,
         paces,
         DepthGroup.defense().spare_slot ) + SlotAverageFitter.fit(
            f_usages,
            paces,
            DepthGroup.forwards().spare_slot )
      SlotAverageStore.write( slots )
      season_length = Season.prior( seasons ).number_of_games
      IceChosenShareStore.write(
         IceChosenShareFitter.fit(
            d_usages,
            season_length,
            DepthGroup.defense() )
         + IceChosenShareFitter.fit(
            f_usages,
            season_length,
            DepthGroup.forwards() ) )
      previous_factors = PreviousTeamFactorBuilder.build(
         last_played_ids,
         landings,
         slots,
         usages_by_season,
         seasons,
         Season.pace_games( seasons ) )
      charts = DepthChartRecorder.record(
         Season.pace_games( seasons ),
         {
            factor.team: factor.rate
            for factor in previous_factors
            if factor.season == previous_season_id
         },
         force=force )
      DepthChartStore.write( charts )
      ice_rows = SkaterIceRecorder.record( charts )
      SkaterIceStore.write( ice_rows )
      TeamFactorStore.write(
         sorted(
            [
               *previous_factors,
               *TeamFactorFitter.current(
                  current_season,
                  BaselineRosterPaceBuilder.build(
                     roster_rows,
                     rows + other_rows,
                     weights,
                     current_season,
                     league_factors,
                     aging_factors ),
                  slots,
                  charts,
                  usages,
                  season_length,
                  { row.player_id: row for row in ice_rows } )
            ],
            key=lambda factor: ( factor.season, factor.team.value ) ) )
      print( f'Ingested { len( rows ) } skater-seasons.', flush=True )


   @classmethod
   def _player_ids(
         cls,
         rows: list[ NhlSkaterSeason ],
         roster_rows: list[ RosterSkater ] ) -> list[ int ]:
      return sorted(
         { row.player_id for row in rows } | { row.player_id for row in roster_rows } )


if __name__ == '__main__':
   SkaterSeasonIngester.main()
