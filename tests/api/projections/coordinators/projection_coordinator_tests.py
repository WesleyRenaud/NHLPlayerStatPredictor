from __future__ import annotations

from pathlib import Path

import pytest

from api.paths import Paths
from api.projections.career_pace import CareerPace
import api.projections.coordinators.projection_coordinator as projection_coordinator
from api.projections.coordinators.projection_coordinator import ProjectionCoordinator
from api.projections.projection import Projection
from api.skater_season import SkaterSeason


def Test_GetProjection_TestSeasons_ExpectAveragedProjection(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = tmp_path / 'skaters.sqlite'
   player_id = 7
   seasons: list[ SkaterSeason ] = []
   pace = CareerPace( 1, 2, 3 )
   games_played = 70
   captured: list[ tuple[ int, str ] ] = []

   def fake_seasons( requested_id: int, path: str ) -> list[ SkaterSeason ]:
      captured.append( ( requested_id, path ) )
      return seasons

   def fake_average( rows: list[ SkaterSeason ] ) -> CareerPace:
      assert rows is seasons
      return pace

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   monkeypatch.setattr(
      projection_coordinator.SkaterSeasonProvider,
      'seasons_for_player_id',
      fake_seasons )
   monkeypatch.setattr(
      projection_coordinator.CareerPaceAverager,
      'average',
      fake_average )
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
