from __future__ import annotations

from ...aging_factor_store import AgingFactorStore
from ..aging_pace_adjuster import AgingPaceAdjuster
from ...league_factor_store import LeagueFactorStore
from ...other_league_season_provider import OtherLeagueSeasonProvider
from ...pace_games_resolver import PaceGamesResolver
from ...paths import Paths
from ..projection import Projection
from ...recency_target_resolver import RecencyTargetResolver
from ...recency_weight_store import RecencyWeightStore
from ...shared.enums.position import Position
from ...skater_season_provider import SkaterSeasonProvider
from ..translated_pace_averager import TranslatedPaceAverager


class ProjectionCoordinator():
   @classmethod
   def get_projection( cls, player_id: int ) -> Projection:
      db_path = str( Paths.DB_PATH )
      seasons = SkaterSeasonProvider.seasons_for_player_id( player_id, db_path )
      aged = AgingPaceAdjuster.adjust(
         TranslatedPaceAverager.average(
            seasons,
            OtherLeagueSeasonProvider.seasons_for_player_id( player_id, db_path ),
            RecencyWeightStore.read(),
            RecencyTargetResolver.resolve(),
            LeagueFactorStore.read() ),
         int( seasons[ Position.LAST ].age ),
         AgingFactorStore.read() )
      goals = round( aged.goals )
      assists = round( aged.assists )
      return Projection(
         goals=goals,
         assists=assists,
         points=goals + assists,
         games_played=PaceGamesResolver.resolve() )
