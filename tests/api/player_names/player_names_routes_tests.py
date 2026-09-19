from __future__ import annotations

from api.player_names.controllers.player_names_controller import PlayerNamesController
from api.player_names.player_names_routes import PlayerNamesRoutes


def Test_Routes_TestEntries_ExpectCallableHandlers() -> None:
   assert PlayerNamesRoutes.ROUTES
   assert PlayerNamesRoutes.ROUTES[ PlayerNamesRoutes.GET_PLAYER_NAMES ] is (
      PlayerNamesController.get_player_names )

   for path, route in PlayerNamesRoutes.ROUTES.items():
      assert isinstance( path, str )
      assert path.startswith( '/' )
      assert callable( route )
