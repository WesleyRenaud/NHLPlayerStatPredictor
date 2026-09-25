from __future__ import annotations

import json

import pytest

import api.player_names.controllers.player_names_controller as player_names_controller
from api.player_names.controllers.player_names_controller import PlayerNamesController
from api.player_names.player_name_summary import PlayerNameSummary
from api.server.json_handler_mixin import JsonHandlerMixin
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


class _RecordingHandler( JsonHandlerMixin ):
   def __init__( self ) -> None:
      self.status: int | None = None
      self.headers: dict[ str, str ] = {}
      self.body = bytearray()
      self.wfile = self


   def send_response( self, code: int, message: str | None = None ) -> None:
      self.status = code


   def send_header( self, key: str, value: str ) -> None:
      self.headers[ key ] = value


   def end_headers( self ) -> None:
      return


   def write( self, data: bytes ) -> int:
      self.body.extend( data )
      return len( data )


def Test_GetPlayerNames_TestCoordinatorSummaries_ExpectJsonPayload(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   stub_summaries = [
      PlayerNameSummary(
         1,
         'Stub Alpha',
         SkaterPosition( 'C' ),
         Team( 'MTL' ),
         20202021 ),
   ]
   handler = _RecordingHandler()
   monkeypatch.setattr(
      player_names_controller.PlayerNamesCoordinator,
      'get_player_summaries',
      lambda: stub_summaries )

   PlayerNamesController.get_player_names( handler )

   assert json.loads( handler.body.decode( 'utf-8' ) ) == [
      summary.to_dict() for summary in stub_summaries
   ]
