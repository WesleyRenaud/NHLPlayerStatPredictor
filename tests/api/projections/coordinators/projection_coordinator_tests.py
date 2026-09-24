from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from api.aging_factor import AgingFactor
from api.games_share import GamesShare
from api.league_factor import LeagueFactor
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.paths import Paths
import api.projections.coordinators.projection_coordinator as projection_coordinator
from api.projections.coordinators.projection_coordinator import ProjectionCoordinator
from api.projections.projection import Projection
from api.projections.season_pace import SeasonPace
from api.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skater import Skater
from api.skater_group import SkaterGroup
from api.skater_ice import SkaterIce
from api.skater_position import SkaterPosition
from api.team import Team
from api.team_factor import TeamFactor
from api.team_factor_skater import TeamFactorSkater


def _stub_team_factors(
      monkeypatch: pytest.MonkeyPatch,
      factors: list[ TeamFactor ] | None = None,
      team: Team | None = None ) -> None:
   monkeypatch.setattr(
      projection_coordinator.TeamFactorStore,
      'read',
      lambda: [] if factors is None else factors )
   monkeypatch.setattr(
      projection_coordinator.RosterSkaterProvider,
      'team',
      lambda player_id, path: team )
   monkeypatch.setattr(
      projection_coordinator.SkaterIceStore,
      'by_player',
      lambda: {} )


def _season(
      age: float,
      season_id: int = 20232024,
      team: Team | None = None ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=age,
      team=list( Team )[ Position.FIRST ] if team is None else team,
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=1.0 )


def Test_GetProjection_TestSeasons_ExpectAgedRoundedProjection(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   seasons = [ _season( 27.2 ), _season( 28.7 ) ]
   weights = [ RecencyWeight( 0, 1.0 ) ]
   factors = [ AgingFactor( 28, -0.07, -0.044 ) ]
   target_season_id = 20232024
   aged = SeasonPace( 10.4, 20.6 )
   games_played = 70
   captured: list[ tuple[ int, str ] ] = []
   resolved: list[ tuple[
      Skater,
      list[ RecencyWeight ],
      int,
      list[ LeagueFactor ],
      list[ AgingFactor ] ] ] = []
   other_seasons: list[ OtherLeagueSkaterSeason ] = []
   league_factors: list[ LeagueFactor ] = []

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_team_factors( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: captured.append( ( requested_id, path ) ) or seasons )
   monkeypatch.setattr(
      projection_coordinator.ScoringWeightStore,
      'read',
      lambda: weights )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: target_season_id )
   monkeypatch.setattr(
      projection_coordinator.BaselinePaceResolver,
      'resolve',
      lambda skater, recency_weights, target, leagues, aging: resolved.append(
         ( skater, recency_weights, target, leagues, aging ) ) or aged )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: other_seasons )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: league_factors )
   monkeypatch.setattr(
      projection_coordinator.AgingFactorStore,
      'read',
      lambda: factors )
   monkeypatch.setattr(
      projection_coordinator.PaceGamesResolver,
      'resolve',
      lambda: games_played )
   goals = round( aged.goals )
   assists = round( aged.assists )
   assert ProjectionCoordinator.get_projection( player_id ) == Projection(
      goals=goals,
      assists=assists,
      points=goals + assists,
      games_played=games_played )
   assert captured == [ ( player_id, str( db_path ) ) ]
   assert resolved == [
      ( Skater( [ *seasons, *other_seasons ] ), weights, target_season_id, league_factors, factors )
   ]


def Test_GetProjection_TestMissingPace_ExpectNone(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_team_factors( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.ScoringWeightStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: 20262027 )
   monkeypatch.setattr(
      projection_coordinator.BaselinePaceResolver,
      'resolve',
      lambda skater, recency_weights, target, leagues, aging: None )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.AgingFactorStore,
      'read',
      lambda: [] )
   assert ProjectionCoordinator.get_projection( 7 ) is None


def Test_GetProjection_TestTeamFactor_ExpectScaledProjection(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   current_season = 20232024
   previous_season_id = 20222023
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   seasons = [ _season( 27.2, previous_season_id, previous ) ]
   weights = [ RecencyWeight( 0, 1.0 ) ]
   factors = [ AgingFactor( 27, 0.0, 0.0 ) ]
   aged = SeasonPace( 10.4, 20.6 )
   current_rate = 0.87
   previous_rate = 1.12
   delta = current_rate - previous_rate
   team_factors = [
      TeamFactor(
         current_season,
         now,
         current_rate,
         [ TeamFactorSkater( 99, 80.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ) ] ),
      TeamFactor(
         previous_season_id,
         previous,
         previous_rate,
         [ TeamFactorSkater( 99, 80.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ) ] ),
   ]
   scaled = SeasonPace(
      aged.goals * ( 1.0 + delta ),
      aged.assists * ( 1.0 + delta ) )
   games_played = 84

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_team_factors( monkeypatch, team_factors, now )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: seasons )
   monkeypatch.setattr(
      projection_coordinator.ScoringWeightStore,
      'read',
      lambda: weights )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: current_season )
   monkeypatch.setattr(
      projection_coordinator.BaselinePaceResolver,
      'resolve',
      lambda skater, recency_weights, target, leagues, aging: aged )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.AgingFactorStore,
      'read',
      lambda: factors )
   monkeypatch.setattr(
      projection_coordinator.PaceGamesResolver,
      'resolve',
      lambda: games_played )
   goals = round( scaled.goals )
   assists = round( scaled.assists )
   assert ProjectionCoordinator.get_projection( player_id ) == Projection(
      goals=goals,
      assists=assists,
      points=goals + assists,
      games_played=games_played )


def Test_GetProjection_TestPlayerInLineup_ExpectTeammateScaledProjection(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   current_season = 20232024
   previous_season_id = 20222023
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   seasons = [ _season( 27.2, previous_season_id, previous ) ]
   weights = [ RecencyWeight( 0, 1.0 ) ]
   factors = [ AgingFactor( 27, 0.0, 0.0 ) ]
   aged = SeasonPace( 10.4, 20.6 )
   current_rate = 1.2
   previous_rate = 0.9
   current_factor = TeamFactor(
      current_season,
      now,
      current_rate,
      [
         TeamFactorSkater( player_id, 40.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
         TeamFactorSkater( 8, 60.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
      ] )
   previous_factor = TeamFactor(
      previous_season_id,
      previous,
      previous_rate,
      [
         TeamFactorSkater( player_id, 50.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
         TeamFactorSkater( 8, 50.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ),
      ] )
   delta = (
      current_factor.excluding( player_id )
      - previous_factor.excluding( player_id ) )
   scaled = SeasonPace(
      aged.goals * ( 1.0 + delta ),
      aged.assists * ( 1.0 + delta ) )
   games_played = 84

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_team_factors(
      monkeypatch,
      [ current_factor, previous_factor ],
      now )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: seasons )
   monkeypatch.setattr(
      projection_coordinator.ScoringWeightStore,
      'read',
      lambda: weights )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: current_season )
   monkeypatch.setattr(
      projection_coordinator.BaselinePaceResolver,
      'resolve',
      lambda skater, recency_weights, target, leagues, aging: aged )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.AgingFactorStore,
      'read',
      lambda: factors )
   monkeypatch.setattr(
      projection_coordinator.PaceGamesResolver,
      'resolve',
      lambda: games_played )
   goals = round( scaled.goals )
   assists = round( scaled.assists )
   assert ProjectionCoordinator.get_projection( player_id ) == Projection(
      goals=goals,
      assists=assists,
      points=goals + assists,
      games_played=games_played )


def Test_GetProjection_TestIceChange_ExpectRateTimesToi(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   seasons = [ _season( 27.2 ) ]
   aged = SeasonPace( 30.0, 40.0 )
   games_played = 84
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_team_factors( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterIceStore,
      'by_player',
      lambda: { player_id: SkaterIce( player_id, 20.0, 24.0 ) } )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: seasons )
   monkeypatch.setattr(
      projection_coordinator.ScoringWeightStore,
      'read',
      lambda: [ RecencyWeight( 0, 1.0 ) ] )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: 20232024 )
   monkeypatch.setattr(
      projection_coordinator.BaselinePaceResolver,
      'resolve',
      lambda skater, recency_weights, target, leagues, aging: aged )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.AgingFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.PaceGamesResolver,
      'resolve',
      lambda: games_played )
   goals = round( 36.0 )
   assists = round( 48.0 )
   assert ProjectionCoordinator.get_projection( player_id ) == Projection(
      goals=goals,
      assists=assists,
      points=goals + assists,
      games_played=games_played )
