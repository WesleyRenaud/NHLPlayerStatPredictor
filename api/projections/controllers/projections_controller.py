from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from ..coordinators.projection_coordinator import ProjectionCoordinator
from ..season_stats_resolver import SeasonStatsResolver
from ...server.json_request_handler import JsonRequestHandler


class ProjectionsController():
   @staticmethod
   def get_projection( handler: JsonRequestHandler ) -> None:
      data = handler._read_json_body()
      player_id = data.get( 'playerId' )
      projection = ProjectionCoordinator.get_projection( player_id )

      if projection is None:
         handler._write_json( {}, 404 )
         return

      on_date = datetime.now( ZoneInfo( 'America/Toronto' ) ).date()
      season_stats = SeasonStatsResolver.resolve( player_id, on_date )
      handler._write_json( {
         **projection.to_dict(),
         'seasonStats': season_stats,
      } )
