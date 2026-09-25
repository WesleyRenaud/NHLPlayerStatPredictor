from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from api.aging.aging_curve_fitter import AgingCurveFitter
from api.aging.aging_factor import AgingFactor
from api.aging.aging_factor_store import AgingFactorStore
from api.aging.league_factor import LeagueFactor
from api.aging.league_factor_fitter import LeagueFactorFitter
from api.aging.league_factor_store import LeagueFactorStore
from api.availability.availability_decay_fitter import AvailabilityDecayFitter
from api.availability.availability_weight_store import AvailabilityWeightStore
from api.availability.mixed_season_share_binder import MixedSeasonShareBinder
from api.depth.ice_chosen_share_store import IceChosenShareStore
import api.ingest.skater_season_ingester as skater_season_ingester
from api.ingest.skater_season_ingester import SkaterSeasonIngester
from api.paths import Paths
from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.recency.recency_decay_fitter import RecencyDecayFitter
from api.recency.recency_weight import RecencyWeight
from api.recency.scoring_weight_store import ScoringWeightStore
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.player_status import PlayerStatus
from api.skaters.roster_skater import RosterSkater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team
from api.team_factor.team_factor import TeamFactor
from api.team_factor.team_factor_store import TeamFactorStore


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
      skater_season_ingester.SkaterSeasonBuilder,
      'build_all',
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
   team = list( Team )[ Position.FIRST ]
   roster_rows = RosterSkater.with_last_played( roster_rows, rows )
   last_played_ids = sorted( {
      previous_season_id,
      *(
         row.last_played_season_id
         for row in roster_rows
         if row.last_played_season_id is not None ) } )
   team_factors = [
      TeamFactor(
         season_id,
         team,
         0.87 if season_id == previous_season_id else 1.0,
         [] )
      for season_id in last_played_ids
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
   fitted: list[ bool ] = []
   previous_rates: list[ dict ] = []
   previous_seasons: list[ int ] = []
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
      skater_season_ingester.PreviousTeamFactorBuilder,
      'build',
      lambda season_ids, landings, slots, usages_by_season, seasons, pace_games: (
         previous_seasons.extend( season_ids ) or team_factors ) )
   monkeypatch.setattr(
      skater_season_ingester.TeamFactorFitter,
      'current',
      lambda season, paces, slots, charts, ice: (
         fitted.append( True ) or [] ) )
   recorded: list[ bool ] = []
   monkeypatch.setattr(
      skater_season_ingester.DepthChartRecorder,
      'record',
      lambda pace_games, team_rates, force=False: (
         recorded.append( force )
         or previous_rates.append( team_rates )
         or [] ) )
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
      MixedSeasonShareBinder.bind( rows, other_rows ) )
   assert AvailabilityWeightStore.read() == availability_weights
   aging_factors = AgingCurveFitter.fit( rows, other_rows )
   assert AgingFactorStore.read() == aging_factors
   league_factors = LeagueFactorFitter.fit(
      rows,
      other_rows,
      aging_factors )
   assert LeagueFactorStore.read() == league_factors
   assert TeamFactorStore.read() == sorted(
      team_factors,
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert previous_seasons == last_played_ids
   assert built == [
      (
         roster_rows,
         rows,
         weights,
         current_season,
         league_factors,
         aging_factors )
   ]
   assert fitted == [ True ]
   assert recorded == [ False ]
   assert previous_rates == [ { team: 0.87 } ]
   assert IceChosenShareStore.read() == []
