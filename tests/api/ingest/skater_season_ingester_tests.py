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
      position=SkaterPosition( 'C' ),
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

   season_player_id = 1
   roster_player_id = 2
   position = SkaterPosition( 'C' )
   team = list( Team )[ Position.FIRST ]
   previous_rate = 0.87
   default_rate = 1.0
   pace_games = 84
   previous_season_id = 20212022
   current_season = 20222023
   db_path = tmp_path / 'skaters.sqlite'
   inserted: list[ tuple[ list[ NhlSkaterSeason ], str ] ] = []
   landing = {
      'playerId': season_player_id,
      'position': position.value,
      'isActive': True,
   }
   roster_landing = {
      'playerId': roster_player_id,
      'position': position.value,
      'isActive': True,
   }
   statuses: list[ tuple[ list[ object ], str ] ] = []
   fetched: list[ list[ int ] ] = []
   roster_rows = [
      RosterSkater(
         player_id=roster_player_id,
         player_name='Roster Rookie',
         position=position,
         team=team )
   ]
   roster_inserted: list[ tuple[ list[ RosterSkater ], str ] ] = []
   other_rows = []
   roster_paces = [
      CurrentSeasonNhlSkater(
         roster_player_id,
         SeasonPace( 10.0, 20.0 ),
         team,
         position )
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
   recorded: list[ bool ] = []
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
         or { season_player_id: landing, roster_player_id: roster_landing } ) )
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
      lambda seasons: pace_games )
   monkeypatch.setattr(
      skater_season_ingester.Season,
      'prior',
      lambda seasons: SeasonLength(
         previous_season_id,
         82,
         date( 2021, 10, 12 ),
         date( 2022, 4, 29 ) ) )
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
         previous_rate if season_id == previous_season_id else default_rate,
         [] )
      for season_id in last_played_ids
   ]
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
   stored_weights = ScoringWeightStore.read()
   stored_availability = AvailabilityWeightStore.read()
   stored_aging = AgingFactorStore.read()
   stored_leagues = LeagueFactorStore.read()
   stored_teams = TeamFactorStore.read()
   stored_ice_shares = IceChosenShareStore.read()

   assert inserted == [ ( rows, str( db_path ) ) ]
   assert roster_inserted == [ ( roster_rows, str( db_path ) ) ]
   assert fetched == [ list( range( season_player_id, AvailabilityDecayFitter.WINDOW + 1 ) ) ]
   assert statuses == [
      (
         [
            PlayerStatus( season_player_id, True ),
            PlayerStatus( roster_player_id, True ),
         ],
         str( db_path ) )
   ]
   assert stored_weights == RecencyDecayFitter.fit( rows )
   assert stored_availability == AvailabilityDecayFitter.fit(
      MixedSeasonShareBinder.bind( rows, other_rows ) )
   assert stored_aging == AgingCurveFitter.fit( rows, other_rows )
   assert stored_leagues == LeagueFactorFitter.fit(
      rows,
      other_rows,
      stored_aging )
   assert stored_teams == team_factors
   assert previous_seasons == last_played_ids
   assert built == [
      (
         roster_rows,
         rows,
         stored_weights,
         current_season,
         stored_leagues,
         stored_aging )
   ]
   assert fitted == [ True ]
   assert recorded == [ False ]
   assert previous_rates == [ { team: previous_rate } ]
   assert stored_ice_shares == []
