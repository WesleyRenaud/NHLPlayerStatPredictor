from __future__ import annotations

from ..coordinators.player_names_coordinator import PlayerNamesCoordinator
from ...json_request_handler import JsonRequestHandler


class PlayerNamesController():
   @staticmethod
   def get_player_names( handler: JsonRequestHandler ) -> None:
      handler._write_json( [
         summary.as_json()
         for summary in PlayerNamesCoordinator.get_player_summaries()
      ] )
