from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from api.aging.league_factor import LeagueFactor
from api.depth.skater_ice import SkaterIce
from api.paths import Paths
import api.projections.coordinators.projection_coordinator as projection_coordinator
from api.projections.coordinators.projection_coordinator import ProjectionCoordinator
from api.projections.pace_values import PaceValues
from api.projections.power_play_pace import PowerPlayPace
from api.projections.projection import Projection
from api.projections.season_pace import SeasonPace
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pim_regression_model import PimRegressionModel
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater import Skater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _stub_ice( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      projection_coordinator.SkaterIceStore,
      'by_player',
      lambda: {} )


def _season( age: float ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=20232024,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
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
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      penalty_minutes=0 )


def Test_GetProjection_TestSeasons_ExpectAgedRoundedProjection(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   seasons = [ _season( 27.2 ), _season( 28.7 ) ]
   target_season_id = 20232024
   aged = SeasonPace( 10.4, 20.6 )
   pim_pace = 18.7
   games_played = 70
   captured: list[ tuple[ int, str ] ] = []
   resolved: list[ tuple[
      Skater,
      int,
      list[ LeagueFactor ],
      PaceRegressionModel,
      PimRegressionModel ] ] = []
   other_seasons: list[ OtherLeagueSkaterSeason ] = []
   league_factors: list[ LeagueFactor ] = []
   model = PaceRegressionModel( [], 0.8, 0.85, 0.8, 0.85, 1.0, 1.0, 1.0, 1.0 )

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_ice( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: captured.append( ( requested_id, path ) ) or seasons )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: target_season_id )
   monkeypatch.setattr(
      projection_coordinator.BaselinePaceResolver,
      'resolve',
      lambda skater, target, leagues, pace_model, pim_model: resolved.append(
         ( skater, target, leagues, pace_model, pim_model ) ) or PaceValues(
            goals=aged.goals,
            assists=aged.assists,
            power_play_goals=0.0,
            power_play_assists=0.0,
            short_handed_goals=0.0,
            short_handed_assists=0.0,
            penalty_minutes=pim_pace ) )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: other_seasons )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: league_factors )
   monkeypatch.setattr(
      projection_coordinator.PaceRegressionStore,
      'read',
      lambda: model )
   monkeypatch.setattr(
      projection_coordinator.PimRegressionStore,
      'read',
      lambda: PimRegressionModel( [], 1.0 ) )
   monkeypatch.setattr(
      projection_coordinator.PaceGamesResolver,
      'resolve',
      lambda: games_played )

   projection = ProjectionCoordinator.get_projection( player_id )

   assert projection == Projection(
      goals=round( aged.goals ),
      assists=round( aged.assists ),
      points=round( aged.goals ) + round( aged.assists ),
      penalty_minutes=round( pim_pace ),
      games_played=games_played,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      projected_toi=None )
   assert captured == [ ( player_id, str( db_path ) ) ]
   assert resolved == [
      (
         Skater( [ *seasons, *other_seasons ] ),
         target_season_id,
         league_factors,
         model,
         PimRegressionModel( [], 1.0 ) )
   ]


def Test_GetProjection_TestMissingPace_ExpectNone(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   target_season_id = 20262027
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_ice( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: target_season_id )
   monkeypatch.setattr(
      projection_coordinator.BaselinePaceResolver,
      'resolve',
      lambda skater, target, leagues, pace_model, pim_model: None )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.PaceRegressionStore,
      'read',
      lambda: PaceRegressionModel( [], 0.8, 0.85, 0.8, 0.85, 1.0, 1.0, 1.0, 1.0 ) )
   monkeypatch.setattr(
      projection_coordinator.PimRegressionStore,
      'read',
      lambda: PimRegressionModel( [], 1.0 ) )

   projection = ProjectionCoordinator.get_projection( player_id )

   assert projection is None


def Test_GetProjection_TestIceChange_ExpectLastToiScale(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   seasons = [ _season( 27.2 ) ]
   aged = SeasonPace( 30.0, 40.0 )
   pim_pace = 18.7
   games_played = 84
   last = 20.0
   implied = 16.0
   projected = 24.0
   target_season_id = 20232024
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_ice( monkeypatch )
   monkeypatch.setattr(
      projection_coordinator.SkaterIceStore,
      'by_player',
      lambda: { player_id: SkaterIce( player_id, last, implied, projected ) } )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: seasons )
   monkeypatch.setattr(
      projection_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: target_season_id )
   monkeypatch.setattr(
      projection_coordinator.BaselinePaceResolver,
      'resolve',
      lambda skater, target, leagues, pace_model, pim_model: PaceValues(
         goals=aged.goals,
         assists=aged.assists,
         power_play_goals=0.0,
         power_play_assists=0.0,
         short_handed_goals=0.0,
         short_handed_assists=0.0,
         penalty_minutes=pim_pace ) )
   monkeypatch.setattr(
      projection_coordinator.OtherLeagueSeasonProvider,
      'seasons_for_player_id',
      lambda requested_id, path: [] )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.PaceRegressionStore,
      'read',
      lambda: PaceRegressionModel( [], 0.8, 0.85, 0.8, 0.85, 1.0, 1.0, 1.0, 1.0 ) )
   monkeypatch.setattr(
      projection_coordinator.PimRegressionStore,
      'read',
      lambda: PimRegressionModel( [], 1.0 ) )
   monkeypatch.setattr(
      projection_coordinator.PaceGamesResolver,
      'resolve',
      lambda: games_played )

   projection = ProjectionCoordinator.get_projection( player_id )

   assert projection == Projection(
      goals=round( aged.goals * projected / last ),
      assists=round( aged.assists * projected / last ),
      points=(
         round( aged.goals * projected / last )
         + round( aged.assists * projected / last ) ),
      penalty_minutes=round( pim_pace * projected / last ),
      games_played=games_played,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      projected_toi=projected )
