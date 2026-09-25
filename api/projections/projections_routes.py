from __future__ import annotations

from typing import ClassVar

from .controllers.projections_controller import ProjectionsController
from ..server.json_request_handler import PostRouteHandler


class ProjectionsRoutes():
   GET_PROJECTION = '/get-projection'
   ROUTES: ClassVar[ dict[ str, PostRouteHandler ] ] = {
      GET_PROJECTION: ProjectionsController.get_projection,
   }
