from __future__ import annotations

from typing import ClassVar

from .controllers.player_names_controller import PlayerNamesController
from ..server.json_request_handler import PostRouteHandler


class PlayerNamesRoutes():
   GET_PLAYER_NAMES = '/get-player-names'
   ROUTES: ClassVar[ dict[ str, PostRouteHandler ] ] = {
      GET_PLAYER_NAMES: PlayerNamesController.get_player_names,
   }
