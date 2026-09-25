from __future__ import annotations

from io import BytesIO
import json

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
   projection = Projection( 12, 34, 46, 70 )
   captured: list[ int ] = []

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
   assert handler.status == 200
   assert json.loads( handler.body.decode( 'utf-8' ) ) == projection.to_dict()


def Test_GetProjection_TestMissingProjection_ExpectNotFound(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      projections_controller.ProjectionCoordinator,
      'get_projection',
      lambda player_id: None )
   handler = _RecordingHandler( { 'playerId': 7 } )
   ProjectionsController.get_projection( handler )
   assert handler.status == 404
