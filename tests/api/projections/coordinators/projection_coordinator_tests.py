from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from api.aging_factor import AgingFactor
from api.league_factor import LeagueFactor
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.paths import Paths
from api.projections.career_pace import CareerPace
import api.projections.coordinators.projection_coordinator as projection_coordinator
from api.projections.coordinators.projection_coordinator import ProjectionCoordinator
from api.projections.projection import Projection
from api.projections.team_environment import TeamEnvironment
from api.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _stub_team_scaling( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'prior',
      lambda: 20252026 )
   monkeypatch.setattr(
      projection_coordinator.RosterSkaterProvider,
      'skaters',
      lambda path: [] )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_season_id',
      lambda season_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_season_id',
      lambda season_id, path: [] )


def _season( age: float ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=20232024,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=age,
      team=list( Team )[ Position.FIRST ],
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
   pace = CareerPace( 31.4, 42.1 )
   aged = CareerPace( 10.4, 20.6 )
   games_played = 70
   captured: list[ tuple[ int, str ] ] = []
   averaged: list[ tuple[
      list[ NhlSkaterSeason ],
      list[ OtherLeagueSkaterSeason ],
      list[ RecencyWeight ],
      int,
      list[ LeagueFactor ] ] ] = []
   adjusted: list[ tuple[ CareerPace, int, list[ AgingFactor ], list[ NhlSkaterSeason ] ] ] = []
   other_seasons: list[ OtherLeagueSkaterSeason ] = []
   league_factors: list[ LeagueFactor ] = []

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_team_scaling( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: captured.append( ( requested_id, path ) ) or seasons )
   monkeypatch.setattr(
      projection_coordinator.RecencyWeightStore,
      'read',
      lambda: weights )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: target_season_id )
   monkeypatch.setattr(
      projection_coordinator.TranslatedPaceAverager,
      'average',
      lambda rows, others, recency_weights, target, leagues: averaged.append(
         ( rows, others, recency_weights, target, leagues ) ) or pace )
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
      projection_coordinator.AgingPaceAdjuster,
      'adjust',
      lambda recency_pace, completed_age, aging_factors, player_seasons: adjusted.append(
         ( recency_pace, completed_age, aging_factors, player_seasons ) ) or aged )
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
   assert averaged == [
      ( seasons, other_seasons, weights, target_season_id, league_factors )
   ]
   assert adjusted == [
      ( pace, int( seasons[ Position.LAST ].age ), factors, seasons )
   ]


def Test_GetProjection_TestOtherLeagueOnly_ExpectOtherLeagueAge(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   other_age = 20.8
   other_seasons = [
      OtherLeagueSkaterSeason(
         player_id=player_id,
         season_id=20252026,
         league='AAA',
         age=other_age,
         games_played=46,
         goals=6,
         assists=13,
         points=19,
         g_pace=10.0,
         a_pace=20.0 )
   ]
   weights = [ RecencyWeight( 0, 1.0 ) ]
   factors = [ AgingFactor( 20, 0.12, 0.09 ) ]
   target_season_id = 20262027
   pace = CareerPace( 31.4, 42.1 )
   aged = CareerPace( 10.4, 20.6 )
   games_played = 84
   adjusted: list[ tuple[ CareerPace, int, list[ AgingFactor ], list[ NhlSkaterSeason ] ] ] = []

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_team_scaling( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.RecencyWeightStore,
      'read',
      lambda: weights )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: target_season_id )
   monkeypatch.setattr(
      projection_coordinator.TranslatedPaceAverager,
      'average',
      lambda rows, others, recency_weights, target, leagues: pace )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: other_seasons )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.AgingFactorStore,
      'read',
      lambda: factors )
   monkeypatch.setattr(
      projection_coordinator.AgingPaceAdjuster,
      'adjust',
      lambda recency_pace, completed_age, aging_factors, player_seasons: adjusted.append(
         ( recency_pace, completed_age, aging_factors, player_seasons ) ) or aged )
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
   assert adjusted == [
      ( pace, int( other_age ), factors, [] )
   ]


def Test_GetProjection_TestMissingPace_ExpectNone(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   adjusted: list[ object ] = []
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_team_scaling( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.RecencyWeightStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: 20262027 )
   monkeypatch.setattr(
      projection_coordinator.TranslatedPaceAverager,
      'average',
      lambda rows, others, recency_weights, target, leagues: None )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.AgingPaceAdjuster,
      'adjust',
      lambda recency_pace, completed_age, aging_factors, player_seasons: adjusted.append(
         recency_pace ) )
   assert ProjectionCoordinator.get_projection( 7 ) is None
   assert adjusted == []


def Test_GetProjection_TestTeamEnvironment_ExpectScaledProjection(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   seasons = [ _season( 27.2 ) ]
   weights = [ RecencyWeight( 0, 1.0 ) ]
   factors = [ AgingFactor( 27, 0.0, 0.0 ) ]
   target_season_id = 20232024
   pace = CareerPace( 31.4, 42.1 )
   aged = CareerPace( 10.4, 20.6 )
   scaled = CareerPace( 12.1, 28.4 )
   environment = TeamEnvironment( 80.0, 40.0 )
   games_played = 84
   adjusted: list[ tuple[ CareerPace, TeamEnvironment ] ] = []

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_team_scaling( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: seasons )
   monkeypatch.setattr(
      projection_coordinator.RecencyWeightStore,
      'read',
      lambda: weights )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: target_season_id )
   monkeypatch.setattr(
      projection_coordinator.TranslatedPaceAverager,
      'average',
      lambda rows, others, recency_weights, target, leagues: pace )
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
      projection_coordinator.AgingPaceAdjuster,
      'adjust',
      lambda recency_pace, completed_age, aging_factors, player_seasons: aged )
   monkeypatch.setattr(
      projection_coordinator.TeamEnvironmentResolver,
      'resolve',
      lambda requested_id, roster, last_season: environment )
   monkeypatch.setattr(
      projection_coordinator.TeamPaceAdjuster,
      'adjust',
      lambda recency_pace, team_environment: adjusted.append(
         ( recency_pace, team_environment ) ) or scaled )
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
   assert adjusted == [ ( aged, environment ) ]
