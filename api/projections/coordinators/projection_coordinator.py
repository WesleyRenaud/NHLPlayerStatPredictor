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
   def get_projection( cls, player_id: int ) -> Projection | None:
      db_path = str( Paths.DB_PATH )
      seasons = SkaterSeasonProvider.seasons_for_player_id( player_id, db_path )
      other_seasons = OtherLeagueSeasonProvider.seasons_for_player_id(
         player_id,
         db_path )
      pace = TranslatedPaceAverager.average(
         seasons,
         other_seasons,
         RecencyWeightStore.read(),
         RecencyTargetResolver.resolve(),
         LeagueFactorStore.read() )

      if pace is None:
         return None

      age_source = seasons if seasons else other_seasons
      aged = AgingPaceAdjuster.adjust(
         pace,
         int( age_source[ Position.LAST ].age ),
         AgingFactorStore.read(),
         seasons )
      goals = round( aged.goals )
      assists = round( aged.assists )
      return Projection(
         goals=goals,
         assists=assists,
         points=goals + assists,
         games_played=PaceGamesResolver.resolve() )
