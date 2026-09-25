from __future__ import annotations

from api.player_names.controllers.player_names_controller import PlayerNamesController
from api.player_names.player_names_routes import PlayerNamesRoutes


def Test_Routes_TestEntries_ExpectCallableHandlers() -> None:
   get_player_names = PlayerNamesRoutes.GET_PLAYER_NAMES
   handler = PlayerNamesController.get_player_names

   routes = PlayerNamesRoutes.ROUTES

   assert routes[ get_player_names ] is handler
   assert all(
      isinstance( path, str ) and path.startswith( '/' ) and callable( route )
      for path, route in routes.items() )
