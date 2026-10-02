from __future__ import annotations

from datetime import datetime
from io import BytesIO
import json
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest

import api.projections.controllers.projections_controller as projections_controller
from api.projections.controllers.projections_controller import ProjectionsController
from api.projections.projection import Projection
from api.server.json_handler_mixin import JsonHandlerMixin


class _RecordingHandler( JsonHandlerMixin ):
   def __init__( self, payload: dict[ str, object ] | None = None ) -> None:
      encoded = json.dumps( payload or {} ).encode( 'utf-8' )
      self.status: int | None = None
      self.headers: dict[ str, str ] = {
         'Content-Length': str( len( encoded ) ),
      }
      self.body = bytearray()
      self.wfile = self
      self.rfile = BytesIO( encoded )


   def send_response( self, code: int, message: str | None = None ) -> None:
      self.status = code


   def send_header( self, key: str, value: str ) -> None:
      self.headers[ key ] = value


   def end_headers( self ) -> None:
      return


   def write( self, data: bytes ) -> int:
      self.body.extend( data )
      return len( data )


def Test_GetProjection_TestCoordinatorProjection_ExpectJsonPayload(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   player_id = 7
   projection = Projection(
      even_strength_goals=6,
      even_strength_points=31,
      penalty_minutes=18,
      games_played=70,
      power_play_goals=5,
      power_play_points=12,
      short_handed_goals=1,
      short_handed_points=3,
      projected_toi=None )
   captured: list[ int ] = []
   season_stats = { 'seasonLabel': '2025-26', 'gamesPlayed': 80, 'goals': 40 }
   now = datetime( 2026, 10, 2, tzinfo=ZoneInfo( 'America/Toronto' ) )
   clock = Mock()
   clock.now.return_value = now
   resolver = Mock( return_value=season_stats )
   history = { 'seasons': [], 'career': {} }
   monkeypatch.setattr( projections_controller.PlayerHistoryResolver, 'resolve', Mock( return_value=history ) )
   monkeypatch.setattr( projections_controller, 'datetime', clock )
   monkeypatch.setattr(
      projections_controller.SeasonStatsResolver,
      'resolve',
      resolver )

   def fake_get_projection( player_id: int ) -> Projection:
      captured.append( player_id )
      return projection

   monkeypatch.setattr(
      projections_controller.ProjectionCoordinator,
      'get_projection',
      fake_get_projection )
   handler = _RecordingHandler( { 'playerId': player_id } )

   ProjectionsController.get_projection( handler )

   assert captured == [ player_id ]
   resolver.assert_called_once_with( player_id, now.date() )
   clock.now.assert_called_once_with( ZoneInfo( 'America/Toronto' ) )
   assert handler.status == 200
   assert json.loads( handler.body.decode( 'utf-8' ) ) == {
      **projection.to_dict(), 'seasonStats': season_stats, 'playerHistory': history,
   }


def Test_GetProjection_TestMissingProjection_ExpectNotFound(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   player_id = 7
   resolver = Mock()
   clock = Mock()
   monkeypatch.setattr( projections_controller.SeasonStatsResolver, 'resolve', resolver )
   monkeypatch.setattr( projections_controller, 'datetime', clock )
   monkeypatch.setattr(
      projections_controller.ProjectionCoordinator,
      'get_projection',
      lambda player_id: None )
   handler = _RecordingHandler( { 'playerId': player_id } )

   ProjectionsController.get_projection( handler )

   assert handler.status == 404
   resolver.assert_not_called()
   clock.now.assert_not_called()
