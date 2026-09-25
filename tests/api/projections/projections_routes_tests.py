from __future__ import annotations

from api.projections.controllers.projections_controller import ProjectionsController
from api.projections.projections_routes import ProjectionsRoutes


def Test_Routes_TestEntries_ExpectCallableHandlers() -> None:
   get_projection = ProjectionsRoutes.GET_PROJECTION
   handler = ProjectionsController.get_projection

   routes = ProjectionsRoutes.ROUTES

   assert routes[ get_projection ] is handler
   assert all(
      isinstance( path, str ) and path.startswith( '/' ) and callable( route )
      for path, route in routes.items() )
