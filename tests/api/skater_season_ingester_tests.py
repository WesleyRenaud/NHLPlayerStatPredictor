from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from api.aging_curve_fitter import AgingCurveFitter
from api.aging_factor import AgingFactor
from api.aging_factor_store import AgingFactorStore
from api.availability_decay_fitter import AvailabilityDecayFitter
from api.availability_weight_store import AvailabilityWeightStore
from api.league_factor import LeagueFactor
from api.league_factor_fitter import LeagueFactorFitter
from api.league_factor_store import LeagueFactorStore
from api.nhl_only_season_filter import NhlOnlySeasonFilter
from api.nhl_skater_season import NhlSkaterSeason
from api.paths import Paths
from api.player_status import PlayerStatus
from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.recency_decay_fitter import RecencyDecayFitter
from api.recency_weight import RecencyWeight
from api.roster_skater import RosterSkater
from api.scoring_weight_store import ScoringWeightStore
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.skater_bio import SkaterBio
from api.skater_position import SkaterPosition
import api.skater_season_ingester as skater_season_ingester
from api.skater_season_ingester import SkaterSeasonIngester
from api.skater_summary import SkaterSummary
from api.team import Team
from api.team_factor import TeamFactor
from api.team_factor_store import TeamFactorStore


def _season(
      season_id: int,
      p_pace: float,
      gp_share: float,
      player_id: int = 1 ) -> NhlSkaterSeason:
   half = p_pace / 2.0
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=half,
      a_pace=half,
      p_pace=p_pace,
      gp_share=gp_share )


def Test_BuildRows_TestRegularSeason_ExpectPacedTotals() -> None:
   team = list( Team )[ Position.FIRST ]
   rows = SkaterSeasonIngester.build_rows(
      [ SkaterSummary(
         8478402,
         'Connor McDavid',
         list( SkaterPosition )[ Position.FIRST ],
         [ team ],
         82,
         44,
         79,
         123 ) ],
      [ SkaterBio( 8478402, date( 1997, 1, 13 ) ) ],
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      84 )

   assert len( rows ) == 1
   row = rows[ Position.FIRST ]
   assert row.g_pace == 44 / 82 * 84
   assert row.a_pace == 79 / 82 * 84
   assert row.p_pace == 123 / 82 * 84
   assert row.pace_games == 84
   assert row.team == team


def Test_BuildRows_TestShortSeason_ExpectPacedTotals() -> None:
   rows = SkaterSeasonIngester.build_rows(
      [ SkaterSummary(
         1,
         'Sample Player',
         list( SkaterPosition )[ Position.SECOND ],
         [ list( Team )[ Position.SECOND ] ],
         4,
         1,
         1,
         2 ) ],
      [ SkaterBio( 1, date( 1999, 1, 1 ) ) ],
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      84 )

   assert rows[ Position.FIRST ].p_pace == 2 / 4 * 84


def Test_BuildRows_TestMissingBio_ExpectSkipped() -> None:
   team = list( Team )[ Position.FIRST ]
   position = list( SkaterPosition )[ Position.FIRST ]
   rows = SkaterSeasonIngester.build_rows(
      [
         SkaterSummary( 1, 'Has Bio', position, [ team ], 82, 1, 1, 2 ),
         SkaterSummary( 2, 'No Bio', position, [ team ], 82, 1, 1, 2 ),
      ],
      [ SkaterBio( 1, date( 1999, 1, 1 ) ) ],
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      84 )

   assert len( rows ) == 1
   assert rows[ Position.FIRST ].player_id == 1


def Test_Seasons_TestBeforeFirstSeason_ExpectExcluded(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( skater_season_ingester.Config, 'FIRST_SEASON_ID', 20102011 )
   meta = SkaterSeasonIngester._seasons(
      [
         SeasonLength( 20092010, 82, date( 2009, 10, 1 ), date( 2010, 4, 15 ) ),
         SeasonLength( 20102011, 82, date( 2010, 10, 7 ), date( 2011, 4, 17 ) ),
         SeasonLength( 20112012, 82, date( 2011, 10, 6 ), date( 2012, 4, 10 ) ),
      ] )

   assert [ item.season_id for item in meta ] == [ 20102011, 20112012 ]


def Test_Main_TestRows_ExpectInsertedAndWeightsAndFactorsStored(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   rows: list[ NhlSkaterSeason ] = []

   for lag in range( AvailabilityDecayFitter.WINDOW ):
      shares = [ 0.0 ] * ( AvailabilityDecayFitter.WINDOW + 1 )
      current = 0.10 * ( lag + 1 )
      shares[ AvailabilityDecayFitter.WINDOW ] = current
      shares[ AvailabilityDecayFitter.WINDOW - 1 ] = current

      if lag:
         shares[ AvailabilityDecayFitter.WINDOW - 1 - lag ] = 0.05

      for offset, share in enumerate( shares ):
         year = 2010 + offset
         rows.append(
            _season(
               year * 10000 + year + 1,
               20.0 + lag * 8.0 + offset * 3.0,
               share,
               lag + 1 ) )
   db_path = tmp_path / 'skaters.sqlite'
   inserted: list[ tuple[ list[ NhlSkaterSeason ], str ] ] = []
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   monkeypatch.setattr(
      SkaterSeasonIngester,
      'build_all_rows',
      lambda force=False: rows )
   monkeypatch.setattr(
      skater_season_ingester.SkaterSeasonStore,
      'insert_rows',
      lambda written, path: inserted.append( ( written, path ) ) )
   landing = { 'playerId': 1, 'position': SkaterPosition( 'C' ).value, 'isActive': True }
   roster_landing = {
      'playerId': 2,
      'position': SkaterPosition( 'C' ).value,
      'isActive': True,
   }
   statuses: list[ tuple[ list[ object ], str ] ] = []
   fetched: list[ list[ int ] ] = []
   roster_rows = [
      RosterSkater(
         player_id=2,
         player_name='Roster Rookie',
         position=list( SkaterPosition )[ Position.FIRST ],
         team=list( Team )[ Position.FIRST ] )
   ]
   roster_inserted: list[ tuple[ list[ RosterSkater ], str ] ] = []
   monkeypatch.setattr(
      skater_season_ingester.RosterSkaterIngester,
      'build_rows',
      lambda force=False: roster_rows )
   monkeypatch.setattr(
      skater_season_ingester.RosterSkaterStore,
      'insert_rows',
      lambda written, path: roster_inserted.append( ( written, path ) ) )
   monkeypatch.setattr(
      skater_season_ingester.PlayerLandingFetcher,
      'fetch',
      lambda player_ids, force=False: (
         fetched.append( player_ids )
         or { 1: landing, 2: roster_landing } ) )
   other_rows = []
   monkeypatch.setattr(
      skater_season_ingester.OtherLeagueSeasonIngester,
      'build_rows',
      lambda player_ids, landings, seasons, pace_games: other_rows )
   monkeypatch.setattr(
      skater_season_ingester.OtherLeagueSeasonStore,
      'insert_rows',
      lambda written, path: None )
   monkeypatch.setattr(
      skater_season_ingester.PlayerStatusStore,
      'insert_rows',
      lambda written, path: statuses.append( ( written, path ) ) )
   monkeypatch.setattr(
      skater_season_ingester.NhlClient,
      'seasons',
      lambda force=False: [] )
   monkeypatch.setattr(
      skater_season_ingester.Season,
      'pace_games',
      lambda seasons: 84 )
   previous_season_id = 20212022
   current_season = 20222023
   monkeypatch.setattr(
      skater_season_ingester.Season,
      'prior',
      lambda seasons: SeasonLength(
         previous_season_id,
         82,
         date( 2021, 10, 12 ),
         date( 2022, 4, 29 ) ) )
   team_factors = [
      TeamFactor(
         previous_season_id,
         list( Team )[ Position.FIRST ],
         0.87,
         [] )
   ]
   roster_paces = [
      CurrentSeasonNhlSkater(
         2,
         SeasonPace( 10.0, 20.0 ),
         list( Team )[ Position.FIRST ],
         list( SkaterPosition )[ Position.FIRST ] )
   ]
   built: list[ tuple[
      list[ RosterSkater ],
      list[ NhlSkaterSeason ],
      list[ RecencyWeight ],
      int,
      list[ LeagueFactor ],
      list[ AgingFactor ] ] ] = []
   fitted: list[ tuple[
      int,
      int,
      list[ PreviousSeasonNhlSkater ],
      list[ CurrentSeasonNhlSkater ],
      object,
      object ] ] = []
   monkeypatch.setattr(
      skater_season_ingester.RecencyTargetResolver,
      'prior',
      lambda: previous_season_id )
   monkeypatch.setattr(
      skater_season_ingester.RecencyTargetResolver,
      'resolve',
      lambda: current_season )
   monkeypatch.setattr(
      skater_season_ingester.BaselineRosterPaceBuilder,
      'build',
      lambda roster, seasons, recency_weights, target, leagues, aging: built.append(
         ( roster, seasons, recency_weights, target, leagues, aging ) )
      or roster_paces )
   monkeypatch.setattr(
      skater_season_ingester.NhlClient,
      'skater_timeonice',
      lambda season_id, force=False: [] )
   monkeypatch.setattr(
      skater_season_ingester.TeamFactorFitter,
      'fit',
      lambda current, previous, splits, paces, season_length, slots, charts,
            usages, ice: fitted.append(
         (
            current,
            previous,
            splits,
            paces,
            season_length,
            slots,
            charts,
            usages,
            ice ) ) or team_factors )
   recorded: list[ bool ] = []
   monkeypatch.setattr(
      skater_season_ingester.DepthChartRecorder,
      'record',
      lambda force=False, pace_games=None: recorded.append( force ) or [] )
   monkeypatch.setattr(
      skater_season_ingester.DepthChartStore,
      'write',
      lambda charts: None )
   monkeypatch.setattr(
      skater_season_ingester.SkaterIceRecorder,
      'record',
      lambda charts: [] )
   monkeypatch.setattr(
      skater_season_ingester.SkaterIceStore,
      'write',
      lambda rows: None )
   SkaterSeasonIngester.main()
   assert inserted == [ ( rows, str( db_path ) ) ]
   assert roster_inserted == [ ( roster_rows, str( db_path ) ) ]
   assert fetched == [ list( range( 1, AvailabilityDecayFitter.WINDOW + 1 ) ) ]
   assert statuses == [
      ( [ PlayerStatus( 1, True ), PlayerStatus( 2, True ) ], str( db_path ) )
   ]
   weights = RecencyDecayFitter.fit( rows )
   assert ScoringWeightStore.read() == weights
   availability_weights = AvailabilityDecayFitter.fit(
      NhlOnlySeasonFilter.keep( rows, other_rows ) )
   assert AvailabilityWeightStore.read() == availability_weights
   aging_factors = AgingCurveFitter.fit( rows, other_rows )
   assert AgingFactorStore.read() == aging_factors
   league_factors = LeagueFactorFitter.fit(
      rows,
      other_rows,
      aging_factors )
   assert LeagueFactorStore.read() == league_factors
   assert TeamFactorStore.read() == team_factors
   assert built == [
      (
         roster_rows,
         rows,
         weights,
         current_season,
         league_factors,
         aging_factors )
   ]
   assert fitted == [
      (
         current_season,
         previous_season_id,
         [],
         roster_paces,
         82,
         [],
         [],
         {},
         {} )
   ]
   assert recorded == [ False ]
