from __future__ import annotations

from api.projections.controllers.projections_controller import ProjectionsController
from api.projections.projections_routes import ProjectionsRoutes


def Test_Routes_TestEntries_ExpectCallableHandlers() -> None:
   assert ProjectionsRoutes.ROUTES
   assert ProjectionsRoutes.ROUTES[ ProjectionsRoutes.GET_PROJECTION ] is (
      ProjectionsController.get_projection )

   for path, route in ProjectionsRoutes.ROUTES.items():
      assert isinstance( path, str )
      assert path.startswith( '/' )
      assert callable( route )
