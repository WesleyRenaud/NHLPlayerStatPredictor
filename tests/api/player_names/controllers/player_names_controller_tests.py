from __future__ import annotations

import json

import pytest

from api.json_handler_mixin import JsonHandlerMixin
import api.player_names.controllers.player_names_controller as player_names_controller
from api.player_names.controllers.player_names_controller import PlayerNamesController
from api.player_names.player_name_summary import PlayerNameSummary
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


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
         list( SkaterPosition )[ Position.FIRST ],
         list( Team )[ Position.FIRST ],
         20202021 ),
   ]
   monkeypatch.setattr(
      player_names_controller.PlayerNamesCoordinator,
      'get_player_summaries',
      lambda: stub_summaries )
   handler = _RecordingHandler()
   PlayerNamesController.get_player_names( handler )
   assert json.loads( handler.body.decode( 'utf-8' ) ) == [
      summary.to_dict() for summary in stub_summaries
   ]
