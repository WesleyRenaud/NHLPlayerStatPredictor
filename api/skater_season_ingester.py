from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from .aging_curve_fitter import AgingCurveFitter
from .aging_factor_store import AgingFactorStore
from .availability_decay_fitter import AvailabilityDecayFitter
from .availability_weight_store import AvailabilityWeightStore
from .config import Config
from .depth_chart_recorder import DepthChartRecorder
from .depth_chart_store import DepthChartStore
from .depth_group import DepthGroup
from .ice_usage_parser import IceUsageParser
from .league_factor_fitter import LeagueFactorFitter
from .league_factor_store import LeagueFactorStore
from .nhl_client import NhlClient
from .nhl_only_season_filter import NhlOnlySeasonFilter
from .nhl_skater_season import NhlSkaterSeason
from .nhl_team_split_builder import NhlTeamSplitBuilder
from .other_league_season_ingester import OtherLeagueSeasonIngester
from .other_league_season_store import OtherLeagueSeasonStore
from .paths import Paths
from .player_landing_fetcher import PlayerLandingFetcher
from .player_status_builder import PlayerStatusBuilder
from .player_status_store import PlayerStatusStore
from .projections.baseline_roster_pace_builder import BaselineRosterPaceBuilder
from .projections.season_pace import SeasonPace
from .recency_decay_fitter import RecencyDecayFitter
from .recency_target_resolver import RecencyTargetResolver
from .roster_skater import RosterSkater
from .roster_skater_ingester import RosterSkaterIngester
from .roster_skater_store import RosterSkaterStore
from .scoring_weight_store import ScoringWeightStore
from .season import Season
from .season_length import SeasonLength
from .skater_bio import SkaterBio
from .skater_ice_recorder import SkaterIceRecorder
from .skater_ice_store import SkaterIceStore
from .skater_season_key import SkaterSeasonKey
from .skater_season_store import SkaterSeasonStore
from .skater_summary import SkaterSummary
from .slot_average_fitter import SlotAverageFitter
from .slot_average_store import SlotAverageStore
from .team_factor_fitter import TeamFactorFitter
from .team_factor_store import TeamFactorStore


class SkaterSeasonIngester():
   SEASON_WORKERS = 4


   @classmethod
   def main( cls, force: bool = False ) -> None:
      rows = cls.build_all_rows( force=force )
      SkaterSeasonStore.insert_rows( rows, str( Paths.DB_PATH ) )
      roster_rows = RosterSkaterIngester.build_rows( force=force )
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
            NhlOnlySeasonFilter.keep( rows, other_rows ) ) )
      aging_factors = AgingCurveFitter.fit( rows, other_rows )
      AgingFactorStore.write( aging_factors )
      league_factors = LeagueFactorFitter.fit( rows, other_rows, aging_factors )
      LeagueFactorStore.write( league_factors )
      previous_season_id = RecencyTargetResolver.prior()
      current_season = RecencyTargetResolver.resolve()
      usages = IceUsageParser.parse(
         NhlClient.skater_timeonice( previous_season_id, force ) )
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
      seasons = NhlClient.seasons( force=force )
      season_length = Season.prior( seasons ).number_of_games
      charts = DepthChartRecorder.record(
         force=force,
         pace_games=Season.pace_games( seasons ) )
      DepthChartStore.write( charts )
      ice_rows = SkaterIceRecorder.record( charts )
      SkaterIceStore.write( ice_rows )
      TeamFactorStore.write(
         TeamFactorFitter.fit(
            current_season,
            previous_season_id,
            NhlTeamSplitBuilder.build(
               landings,
               previous_season_id,
               Season.pace_games( NhlClient.seasons( force=force ) ) ),
            BaselineRosterPaceBuilder.build(
               roster_rows,
               rows + other_rows,
               weights,
               current_season,
               league_factors,
               aging_factors ),
            season_length,
            slots,
            charts,
            usages,
            { row.player_id: row for row in ice_rows } ) )
      print( f'Ingested { len( rows ) } skater-seasons.', flush=True )


   @classmethod
   def build_all_rows( cls, force: bool = False ) -> list[ NhlSkaterSeason ]:
      seasons = NhlClient.seasons( force=force )
      pace_games = Season.pace_games( seasons )
      rows: list[ NhlSkaterSeason ] = []
      seen: set[ SkaterSeasonKey ] = set()

      for season_rows in cls._season_rows( cls._seasons( seasons ), pace_games, force ):
         for row in season_rows:
            key = row.key()

            if key in seen:
               continue

            seen.add( key )
            rows.append( row )

      return rows


   @classmethod
   def _season_rows(
         cls,
         seasons: list[ SeasonLength ],
         pace_games: int,
         force: bool ) -> list[ list[ NhlSkaterSeason ] ]:
      with ThreadPoolExecutor( max_workers=SkaterSeasonIngester.SEASON_WORKERS ) as executor:
         return list(
            executor.map(
               lambda season: cls._rows_for_season( season, pace_games, force ),
               seasons ) )


   @classmethod
   def _rows_for_season(
         cls,
         season: SeasonLength,
         pace_games: int,
         force: bool ) -> list[ NhlSkaterSeason ]:
      print( f'Fetching skaters { Season.label( season.season_id ) }...', flush=True )
      return cls.build_rows(
         NhlClient.skater_summary( season.season_id, force=force ),
         NhlClient.skater_bios( season.season_id, force=force ),
         season,
         pace_games )


   @classmethod
   def build_rows(
         cls,
         summaries: list[ SkaterSummary ],
         bios: list[ SkaterBio ],
         season: SeasonLength,
         pace_games: int ) -> list[ NhlSkaterSeason ]:
      bios_by_player = { bio.player_id: bio for bio in bios }
      rows: list[ NhlSkaterSeason ] = []

      for summary in summaries:
         if summary.player_id not in bios_by_player:
            continue

         bio = bios_by_player[ summary.player_id ]
         games_played = float( summary.games_played )
         goals = float( summary.goals )
         assists = float( summary.assists )
         points = float( summary.points )
         birth_date = bio.birth_date
         age = Season.age_on( birth_date, season.start_date )
         gp_share = games_played / float( season.number_of_games )

         rows.append( NhlSkaterSeason(
            player_id=summary.player_id,
            season_id=season.season_id,
            player_name=summary.player_name,
            position=summary.position,
            birth_date=birth_date,
            age=age,
            team=Season.primary_team( summary.team_abbrevs ),
            games_played=summary.games_played,
            goals=summary.goals,
            assists=summary.assists,
            points=summary.points,
            schedule_games=season.number_of_games,
            pace_games=pace_games,
            g_pace=Season.pace( goals, games_played, pace_games ),
            a_pace=Season.pace( assists, games_played, pace_games ),
            p_pace=Season.pace( points, games_played, pace_games ),
            gp_share=gp_share ) )

      return rows


   @classmethod
   def _seasons( cls, seasons: list[ SeasonLength ] ) -> list[ SeasonLength ]:
      return sorted(
         [
            season for season in seasons
            if season.season_id >= Config.FIRST_SEASON_ID
         ],
         key=lambda season: season.season_id )


   @classmethod
   def _player_ids(
         cls,
         rows: list[ NhlSkaterSeason ],
         roster_rows: list[ RosterSkater ] ) -> list[ int ]:
      return sorted(
         { row.player_id for row in rows } | { row.player_id for row in roster_rows } )


if __name__ == '__main__':
   SkaterSeasonIngester.main()
