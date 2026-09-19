from __future__ import annotations

from ..career_pace_averager import CareerPaceAverager
from ...pace_games_resolver import PaceGamesResolver
from ...paths import Paths
from ..projection import Projection
from ...skater_season_provider import SkaterSeasonProvider


class ProjectionCoordinator():
   @classmethod
   def get_projection( cls, player_id: int ) -> Projection:
      seasons = SkaterSeasonProvider.seasons_for_player_id(
         player_id,
         str( Paths.DB_PATH ) )
      pace = CareerPaceAverager.average( seasons )
      return Projection(
         goals=pace.goals,
         assists=pace.assists,
         points=pace.points,
         games_played=PaceGamesResolver.resolve() )
