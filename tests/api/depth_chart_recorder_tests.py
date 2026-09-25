from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from api.availability_weight_store import AvailabilityWeightStore
from api.club_league import ClubLeague
from api.depth_chart_recorder import DepthChartRecorder
from api.depth_chart_store import DepthChartStore
from api.depth_group import DepthGroup
from api.games_share import GamesShare
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.paths import Paths
from api.recency_target_resolver import RecencyTargetResolver
from api.recency_weight import RecencyWeight
from api.roster_skater import RosterSkater
from api.roster_skater_ingester import RosterSkaterIngester
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.skater_group import SkaterGroup
from api.skater_position import SkaterPosition
from api.slot_average import SlotAverage
from api.slot_average_store import SlotAverageStore
from api.slot_chosen_share import SlotChosenShare
from api.slot_chosen_share_store import SlotChosenShareStore
from api.team import Team


def _seasons() -> list[ SeasonLength ]:
   return [
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      SeasonLength( 20252026, 84, date( 2025, 10, 8 ), date( 2026, 4, 17 ) ),
   ]


def _write_slots() -> None:
   SlotAverageStore.write(
      [
         SlotAverage( DepthGroup.forwards().spare_slot, 10.0, 1.0, 8.0 ),
         SlotAverage( DepthGroup.defense().spare_slot, 15.0, 2.0, 12.0 ),
      ] )
   shares = []

   for group in ( DepthGroup.forwards(), DepthGroup.defense() ):
      for slot in range( 1, group.dressed_count + 1 ):
         shares.append(
            SlotChosenShare(
               slot,
               group.skater_group,
               GamesShare.FULL,
               GamesShare.FULL ) )

   SlotChosenShareStore.write( shares )


def Test_Record_TestRosterAndUsage_ExpectStoredChart(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   _write_slots()
   team = list( Team )[ Position.FIRST ]
   monkeypatch.setattr( RecencyTargetResolver, 'prior', lambda: 20252026 )
   monkeypatch.setattr(
      'api.depth_chart_recorder.NhlClient.skater_timeonice',
      lambda season_id, force=False: [
         {
            'playerId': 1,
            'positionCode': 'D',
            'gamesPlayed': 80,
            'timeOnIcePerGame': 1440.0,
            'teamAbbrevs': team.value,
            'shootsCatches': 'L',
         },
         {
            'playerId': 2,
            'positionCode': 'D',
            'gamesPlayed': 80,
            'timeOnIcePerGame': 1320.0,
            'teamAbbrevs': team.value,
            'shootsCatches': 'R',
         },
         {
            'playerId': 3,
            'positionCode': 'C',
            'gamesPlayed': 80,
            'timeOnIcePerGame': 1200.0,
            'teamAbbrevs': team.value,
            'shootsCatches': 'L',
         },
      ] )
   monkeypatch.setattr(
      RosterSkaterIngester,
      'build_rows',
      lambda force=False: [
         RosterSkater( 1, 'Left', SkaterPosition( 'D' ), team ),
         RosterSkater( 2, 'Right', SkaterPosition( 'D' ), team ),
         RosterSkater( 3, 'Center', SkaterPosition( 'C' ), team ),
      ] )
   monkeypatch.setattr(
      DepthChartRecorder,
      '_availabilities',
      lambda roster: { row.player_id: 1.0 for row in roster } )
   monkeypatch.setattr(
      'api.depth_chart_recorder.NhlClient.seasons',
      lambda force=False: _seasons() )
   charts = DepthChartRecorder.record( Position.SECOND )
   defense = next(
      chart
      for chart in charts
      if chart.skater_group is SkaterGroup.DEFENSE )
   assert len( charts ) == 2
   assert defense.team == team
   assert len( defense.regulars ) == 2
   DepthChartRecorder.main()
   assert ( tmp_path / DepthChartStore.FILE_NAME ).exists()


def Test_Record_TestForwardAndDefense_ExpectBothCharts(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   _write_slots()
   team = list( Team )[ Position.FIRST ]
   monkeypatch.setattr( RecencyTargetResolver, 'prior', lambda: 20252026 )
   monkeypatch.setattr(
      'api.depth_chart_recorder.NhlClient.skater_timeonice',
      lambda season_id, force=False: [
         {
            'playerId': 1,
            'positionCode': 'D',
            'gamesPlayed': 80,
            'timeOnIcePerGame': 1440.0,
            'teamAbbrevs': team.value,
            'shootsCatches': 'L',
         },
         {
            'playerId': 3,
            'positionCode': 'C',
            'gamesPlayed': 80,
            'timeOnIcePerGame': 1200.0,
            'teamAbbrevs': team.value,
            'shootsCatches': 'L',
         },
      ] )
   monkeypatch.setattr(
      RosterSkaterIngester,
      'build_rows',
      lambda force=False: [
         RosterSkater( 1, 'Left', SkaterPosition( 'D' ), team ),
         RosterSkater( 3, 'Center', SkaterPosition( 'C' ), team ),
      ] )
   monkeypatch.setattr(
      DepthChartRecorder,
      '_availabilities',
      lambda roster: { row.player_id: 1.0 for row in roster } )
   charts = DepthChartRecorder.record( Position.SECOND )
   assert len( charts ) == 2
   assert charts[ Position.FIRST ].skater_group is SkaterGroup.FORWARD
   assert charts[ Position.SECOND ].skater_group is SkaterGroup.DEFENSE


def Test_Availabilities_TestNhlGames_ExpectShare(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   share = 0.35
   team = list( Team )[ Position.FIRST ]
   monkeypatch.setattr(
      'api.depth_chart_recorder.SkaterSeasonProvider.seasons_for_player_ids',
      lambda player_ids, db_path: [
         NhlSkaterSeason(
            player_id=1,
            season_id=20252026,
            player_name='Stub',
            position=SkaterPosition( 'D' ),
            birth_date=date( 1997, 1, 13 ),
            age=28.7,
            team=team,
            games_played=29,
            goals=0,
            assists=0,
            points=0,
            schedule_games=1,
            pace_games=1,
            g_pace=0.0,
            a_pace=0.0,
            p_pace=0.0,
            gp_share=share )
      ] )
   monkeypatch.setattr(
      'api.depth_chart_recorder.OtherLeagueSeasonProvider.seasons_for_player_ids',
      lambda player_ids, db_path: [] )
   monkeypatch.setattr(
      AvailabilityWeightStore,
      'read',
      lambda: [ RecencyWeight( 0, 1.0 ) ] )
   monkeypatch.setattr( RecencyTargetResolver, 'resolve', lambda: 20262027 )
   roster = [ RosterSkater( 1, 'Stub', SkaterPosition( 'D' ), team ) ]
   assert DepthChartRecorder._availabilities( roster )[ 1 ] == share


def Test_Availabilities_TestMixedYear_ExpectFull(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   team = list( Team )[ Position.FIRST ]
   monkeypatch.setattr(
      'api.depth_chart_recorder.SkaterSeasonProvider.seasons_for_player_ids',
      lambda player_ids, db_path: [
         NhlSkaterSeason(
            player_id=1,
            season_id=20252026,
            player_name='Stub',
            position=SkaterPosition( 'C' ),
            birth_date=date( 1997, 1, 13 ),
            age=20.8,
            team=team,
            games_played=9,
            goals=0,
            assists=0,
            points=0,
            schedule_games=1,
            pace_games=1,
            g_pace=0.0,
            a_pace=0.0,
            p_pace=0.0,
            gp_share=0.11 )
      ] )
   monkeypatch.setattr(
      'api.depth_chart_recorder.OtherLeagueSeasonProvider.seasons_for_player_ids',
      lambda player_ids, db_path: [
         OtherLeagueSkaterSeason(
            player_id=1,
            season_id=20252026,
            league=list( ClubLeague )[ Position.FIRST ].value,
            position=SkaterPosition( 'C' ),
            age=20.8,
            games_played=35,
            goals=0,
            assists=0,
            points=0,
            g_pace=0.0,
            a_pace=0.0 )
      ] )
   monkeypatch.setattr(
      AvailabilityWeightStore,
      'read',
      lambda: [ RecencyWeight( 0, 1.0 ) ] )
   monkeypatch.setattr( RecencyTargetResolver, 'resolve', lambda: 20262027 )
   roster = [ RosterSkater( 1, 'Stub', SkaterPosition( 'C' ), team ) ]
   assert DepthChartRecorder._availabilities( roster )[ 1 ] == GamesShare.FULL
