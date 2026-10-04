from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path
from unittest.mock import Mock

import pytest

from api.aging.league_factor import LeagueFactor
from api.depth.skater_ice import SkaterIce
from api.ingest.nhl_client import NhlClient
from api.paths import Paths
import api.projections.coordinators.projection_coordinator as projection_coordinator
from api.projections.coordinators.projection_coordinator import ProjectionCoordinator
from api.projections.draft_pick import DraftPick
from api.projections.pace_values import PaceValues
from api.projections.power_play_pace import PowerPlayPace
from api.projections.projection import Projection
from api.projections.prospect_calibration_model import ProspectCalibrationModel
from api.projections.prospect_calibration_sample import ProspectCalibrationSample
from api.projections.prospect_calibration_store import ProspectCalibrationStore
from api.projections.prospect_profile import ProspectProfile
from api.projections.season_pace import SeasonPace
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.production_coefficient import ProductionCoefficient
from api.recency.production_growth import ProductionGrowth
from api.recency.production_weight import ProductionWeight
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater import Skater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _stub_ice( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( ProspectCalibrationStore, 'read',
      Mock( side_effect=AssertionError( 'Non-prospect projections must not read calibration.' ) ) )
   monkeypatch.setattr(
      projection_coordinator.SkaterIceStore,
      'by_player',
      lambda: {} )


def _stub_roster( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      projection_coordinator.RosterSkaterProvider,
      'team',
      lambda player_id, path: list( Team )[ Position.FIRST ] )


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
      even_strength_goals=0,
      even_strength_points=0,
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
      shots=0,
      penalty_minutes=0 )


def Test_GetProjection_TestProspectCurve_ExpectCalibrationBeforeIceAndRounding(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   scoring_factor = 1.5
   baseline_toi = 10.0
   projected_toi = 20.0
   ice_scale = projected_toi / baseline_toi
   pace_games = 84
   source = OtherLeagueSkaterSeason(
      player_id=1, season_id=20252026, age=18.0, games_played=40,
      goals=10, assists=20, points=30, g_pace=21.0, a_pace=42.0,
      position=SkaterPosition.CENTER, league='SHL' )
   calibration = ProspectCalibrationModel(
      20262027, [ ProspectProfile( 1, 2025, DraftPick( 3 ), [] ) ],
      [
         ProspectCalibrationSample( 2, 20242025, DraftPick( 1 ), 20.0, 20.0 * scoring_factor, 'SHL' ),
         ProspectCalibrationSample( 3, 20242025, DraftPick( 20 ), 40.0, 40.0 * scoring_factor, 'OHL' ),
      ] )
   paces = PaceValues( 1.2, 2.4, 0.6, 1.4, 0.2, 0.4, 30.0, 200.0 )
   _stub_roster( monkeypatch )
   _stub_ice( monkeypatch )
   monkeypatch.setattr( projection_coordinator.SkaterSeasonProvider, 'seasons_for_player_id',
      lambda player_id, path: [] )
   monkeypatch.setattr( projection_coordinator.OtherLeagueSeasonProvider, 'seasons_for_player_id',
      lambda player_id, path: [ source ] )
   monkeypatch.setattr( projection_coordinator.RecencyTargetResolver, 'resolve', lambda: 20262027 )
   monkeypatch.setattr( projection_coordinator.LeagueFactorStore, 'read', lambda: [ LeagueFactor( 'SHL', 0.5 ) ] )
   monkeypatch.setattr( projection_coordinator.ProductionModelProvider, 'read', lambda: PaceRegressionModel( [] ) )
   monkeypatch.setattr( projection_coordinator.BaselinePaceResolver, 'resolve',
      lambda skater, target, leagues, model, player_ice_scales: paces )
   monkeypatch.setattr( ProspectCalibrationStore, 'read', lambda: calibration )
   monkeypatch.setattr( projection_coordinator.SkaterIceStore, 'by_player',
      lambda: { 1: SkaterIce( 1, baseline_toi, baseline_toi, projected_toi ) } )
   monkeypatch.setattr( projection_coordinator.PaceGamesResolver, 'resolve', lambda: pace_games )

   projection = ProjectionCoordinator.get_projection( 1 )

   assert projection is not None
   assert projection.even_strength_goals == round( paces.even_strength_goals * scoring_factor * ice_scale )
   assert projection.even_strength_points == (
      round( paces.even_strength_goals * scoring_factor * ice_scale )
      + round( paces.even_strength_assists * scoring_factor * ice_scale ) )
   assert projection.power_play_points == (
      round( paces.power_play_goals * scoring_factor * ice_scale )
      + round( paces.power_play_assists * scoring_factor * ice_scale ) )
   assert projection.short_handed_points == (
      round( paces.short_handed_goals * scoring_factor * ice_scale )
      + round( paces.short_handed_assists * scoring_factor * ice_scale ) )
   assert projection.shots == round( paces.shots * ice_scale )
   assert projection.penalty_minutes == round( paces.penalty_minutes * ice_scale )
   assert projection.games_played == pace_games
   assert projection.projected_toi == projected_toi
   assert projection.shooting_percentage == pytest.approx( 100 * paces.goals * scoring_factor / paces.shots )


@pytest.mark.parametrize( 'shots_pace', [ None, 0.0, 205.3 ] )
def Test_GetProjection_TestSeasons_ExpectAgedRoundedProjection(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path,
      shots_pace: float | None ) -> None:
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
      PaceRegressionModel ] ] = []
   other_seasons: list[ OtherLeagueSkaterSeason ] = []
   league_factors: list[ LeagueFactor ] = []
   model = PaceRegressionModel( [] )

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_roster( monkeypatch )
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
      lambda skater, target, leagues, pace_model, player_ice_scales=None: resolved.append(
         ( skater, target, leagues, pace_model ) ) or PaceValues(
            even_strength_goals=aged.goals,
            even_strength_assists=aged.assists,
            power_play_goals=0.0,
            power_play_assists=0.0,
            short_handed_goals=0.0,
            short_handed_assists=0.0,
            shots=shots_pace,
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
      projection_coordinator.ProductionModelProvider,
      'read',
      lambda: model )
   monkeypatch.setattr(
      projection_coordinator.PaceGamesResolver,
      'resolve',
      lambda: games_played )

   projection = ProjectionCoordinator.get_projection( player_id )

   assert replace( projection, shooting_percentage=None ) == Projection(
      even_strength_goals=round( aged.goals ),
      even_strength_points=round( aged.goals ) + round( aged.assists ),
      shots=None if shots_pace is None else round( shots_pace ),
      penalty_minutes=round( pim_pace ),
      games_played=games_played,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      projected_toi=None )
   if not shots_pace:
      assert projection.shooting_percentage is None
   else:
      assert projection.shooting_percentage == pytest.approx( 100 * aged.goals / shots_pace )
   assert captured == [ ( player_id, str( db_path ) ) ]
   assert resolved == [
      (
         Skater( [ *seasons, *other_seasons ] ),
         target_season_id,
         league_factors,
         model )
   ]


def Test_GetProjection_TestMissingPace_ExpectNone(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   target_season_id = 20262027
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_roster( monkeypatch )
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
      lambda skater, target, leagues, pace_model, player_ice_scales=None: None )
   monkeypatch.setattr(
      projection_coordinator.LeagueFactorStore,
      'read',
      lambda: [] )
   monkeypatch.setattr(
      projection_coordinator.ProductionModelProvider,
      'read',
      lambda: PaceRegressionModel( [] ) )

   projection = ProjectionCoordinator.get_projection( player_id )

   assert projection is None


@pytest.mark.parametrize(
   'goal_pace, pp_pace, sh_pace',
   [ ( 30.0, 0.0, 0.0 ), ( 1.2, 0.6, 0.6 ), ( 1.0, 2.0, 0.0 ) ] )
def Test_GetProjection_TestIceChange_ExpectLastToiScale(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path,
      goal_pace: float,
      pp_pace: float,
      sh_pace: float ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   seasons = [ _season( 27.2 ) ]
   aged = SeasonPace( goal_pace, 40.0 )
   pim_pace = 18.7
   shots_pace = 205.3
   games_played = 84
   last = 20.0
   implied = 16.0
   projected = 24.0
   target_season_id = 20232024
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   _stub_roster( monkeypatch )
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
      lambda skater, target, leagues, pace_model, player_ice_scales=None: PaceValues(
         even_strength_goals=aged.goals,
         even_strength_assists=aged.assists,
         power_play_goals=pp_pace,
         power_play_assists=0.0,
         short_handed_goals=sh_pace,
         short_handed_assists=0.0,
         shots=shots_pace,
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
      projection_coordinator.ProductionModelProvider,
      'read',
      lambda: PaceRegressionModel( [] ) )
   monkeypatch.setattr(
      projection_coordinator.PaceGamesResolver,
      'resolve',
      lambda: games_played )

   projection = ProjectionCoordinator.get_projection( player_id )

   expected_pp = round( pp_pace * projected / last )
   expected_sh = round( sh_pace * projected / last )
   assert replace( projection, shooting_percentage=None ) == Projection(
      even_strength_goals=round( aged.goals * projected / last ),
      even_strength_points=(
         round( aged.goals * projected / last )
         + round( aged.assists * projected / last ) ),
      shots=round( shots_pace * projected / last ),
      penalty_minutes=round( pim_pace * projected / last ),
      games_played=games_played,
      power_play_goals=expected_pp,
      power_play_points=expected_pp,
      short_handed_goals=expected_sh,
      short_handed_points=expected_sh,
      projected_toi=projected )
   assert projection.shooting_percentage == pytest.approx(
      100 * ( goal_pace + pp_pace + sh_pace ) / shots_pace )


def Test_GetProjection_TestUnrosteredPlayer_ExpectNoneWithoutCalculation(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   roster_team = Mock( return_value=None )
   season_lookup = Mock()
   baseline = Mock()
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   monkeypatch.setattr( projection_coordinator.RosterSkaterProvider, 'team', roster_team )
   monkeypatch.setattr( projection_coordinator.SkaterSeasonProvider, 'seasons_for_player_id', season_lookup )
   monkeypatch.setattr( projection_coordinator.BaselinePaceResolver, 'resolve', baseline )

   assert ProjectionCoordinator.get_projection( player_id ) is None
   roster_team.assert_called_once_with( player_id, str( db_path ) )
   season_lookup.assert_not_called()
   baseline.assert_not_called()


@pytest.mark.parametrize( 'projected_toi', [ 10.0, 20.0 ] )
def Test_GetProjection_TestHistoricalRates_ExpectNormalizedThenProjectedStats(
      monkeypatch: pytest.MonkeyPatch,
      projected_toi: float ) -> None:
   latest_toi = 20.0
   older_toi = 10.0
   latest = replace( _season( 27.2 ), season_id=20242025, games_played=82,
      pace_games=82, even_strength_goals=20, even_strength_points=40,
      shots=200, penalty_minutes=20 )
   older = replace( latest, season_id=20232024, age=26.2 )
   model = PaceRegressionModel( [ ProductionGrowth( 27, 28, 1.0, 100 ) ],
      history_weights=[ ProductionWeight( 27, 28, 1.0, 100 ), ProductionWeight( 26, 28, 1.0, 100 ) ],
      pim_coefficients=[ ProductionCoefficient( 27, 28, 1.0, 1.0, 100 ),
         ProductionCoefficient( 26, 28, 1.0, 1.0, 100 ) ],
      shots_coefficients=[ ProductionCoefficient( 27, 28, 1.0, 1.0, 100 ),
         ProductionCoefficient( 26, 28, 1.0, 1.0, 100 ) ] )
   _stub_roster( monkeypatch )
   monkeypatch.setattr( projection_coordinator.SkaterSeasonProvider, 'seasons_for_player_id',
      lambda player_id, path: [ latest, older ] )
   monkeypatch.setattr( projection_coordinator.OtherLeagueSeasonProvider, 'seasons_for_player_id',
      lambda player_id, path: [] )
   monkeypatch.setattr( projection_coordinator.SkaterIceStore, 'by_player',
      lambda: { 1: SkaterIce( 1, latest_toi, latest_toi, projected_toi ) } )
   monkeypatch.setattr( projection_coordinator.RecencyTargetResolver, 'resolve', lambda: 20252026 )
   monkeypatch.setattr( projection_coordinator.ProductionModelProvider, 'read', lambda: model )
   monkeypatch.setattr( projection_coordinator.LeagueFactorStore, 'read', lambda: [] )
   monkeypatch.setattr( projection_coordinator.PaceGamesResolver, 'resolve', lambda: 82 )
   monkeypatch.setattr( NhlClient, 'skater_timeonice', lambda season_id: [
      { 'playerId': 1, 'timeOnIcePerGame': ( latest_toi if season_id == latest.season_id else older_toi ) * 60,
         'gamesPlayed': latest.games_played, 'teamAbbrevs': 'COL', 'positionCode': 'C' } ] )

   projection = ProjectionCoordinator.get_projection( 1 )

   assert projection is not None
   result = projection.to_dict()
   ratio = projected_toi / latest_toi
   older_ice_scale = latest_toi / older_toi
   expected_points = ( latest.even_strength_points + older.even_strength_points * older_ice_scale ) / 2
   expected_shots = ( latest.shots + older.shots * older_ice_scale ) / 2
   expected_pim = ( latest.penalty_minutes + older.penalty_minutes * older_ice_scale ) / 2
   assert result[ 'points' ] == expected_points * ratio
   assert result[ 'shots' ] == expected_shots * ratio
   assert result[ 'penaltyMinutes' ] == expected_pim * ratio
