from __future__ import annotations

from pathlib import Path

import pytest

from api.paths import Paths
from api.projections.career_pace import CareerPace
import api.projections.coordinators.projection_coordinator as projection_coordinator
from api.projections.coordinators.projection_coordinator import ProjectionCoordinator
from api.projections.projection import Projection
from api.recency_weight import RecencyWeight
from api.skater_season import SkaterSeason


def Test_GetProjection_TestSeasons_ExpectAveragedProjection(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   seasons: list[ SkaterSeason ] = []
   weights = [ RecencyWeight( 0, 1.0 ) ]
   target_season_id = 20232024
   pace = CareerPace( 1, 2, 3 )
   games_played = 70
   captured: list[ tuple[ int, str ] ] = []
   averaged: list[ tuple[ list[ SkaterSeason ], list[ RecencyWeight ], int ] ] = []

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
      projection_coordinator.CareerPaceAverager,
      'average',
      lambda rows, recency_weights, target: averaged.append(
         ( rows, recency_weights, target ) ) or pace )
   monkeypatch.setattr(
      projection_coordinator.PaceGamesResolver,
      'resolve',
      lambda: games_played )
   assert ProjectionCoordinator.get_projection( player_id ) == Projection(
      goals=pace.goals,
      assists=pace.assists,
      points=pace.points,
      games_played=games_played )
   assert captured == [ ( player_id, str( db_path ) ) ]
   assert averaged == [ ( seasons, weights, target_season_id ) ]
