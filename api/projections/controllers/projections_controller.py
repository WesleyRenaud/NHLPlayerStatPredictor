from __future__ import annotations

from ..coordinators.projection_coordinator import ProjectionCoordinator
from ...json_request_handler import JsonRequestHandler


class ProjectionsController():
   @staticmethod
   def get_projection( handler: JsonRequestHandler ) -> None:
      data = handler._read_json_body()

      projection = ProjectionCoordinator.get_projection(
         player_id=data.get( 'playerId' ) )

      handler._write_json( projection.to_dict() )
