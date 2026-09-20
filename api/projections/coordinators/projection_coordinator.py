from __future__ import annotations

from ...aging_factor_store import AgingFactorStore
from ..aging_pace_adjuster import AgingPaceAdjuster
from ..career_pace_averager import CareerPaceAverager
from ...pace_games_resolver import PaceGamesResolver
from ...paths import Paths
from ..projection import Projection
from ...recency_target_resolver import RecencyTargetResolver
from ...recency_weight_store import RecencyWeightStore
from ...shared.enums.position import Position
from ...skater_season_provider import SkaterSeasonProvider


class ProjectionCoordinator():
   @classmethod
   def get_projection( cls, player_id: int ) -> Projection:
      seasons = SkaterSeasonProvider.seasons_for_player_id(
         player_id,
         str( Paths.DB_PATH ) )
      aged = AgingPaceAdjuster.adjust(
         CareerPaceAverager.average(
            seasons,
            RecencyWeightStore.read(),
            RecencyTargetResolver.resolve() ),
         int( seasons[ Position.LAST ].age ),
         AgingFactorStore.read() )
      goals = round( aged.goals )
      assists = round( aged.assists )
      return Projection(
         goals=goals,
         assists=assists,
         points=goals + assists,
         games_played=PaceGamesResolver.resolve() )
