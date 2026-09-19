from __future__ import annotations

from ..career_pace_averager import CareerPaceAverager
from ...paths import Paths
from ..projection import Projection
from ...skater_season_provider import SkaterSeasonProvider


class ProjectionCoordinator():
   @classmethod
   def get_projection( cls, player_id: int ) -> Projection:
      return CareerPaceAverager.average(
         SkaterSeasonProvider.seasons_for_player_id(
            player_id,
            str( Paths.DB_PATH ) ) )
