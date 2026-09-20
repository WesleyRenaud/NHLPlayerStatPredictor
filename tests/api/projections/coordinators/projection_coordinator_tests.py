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
from api.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


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
