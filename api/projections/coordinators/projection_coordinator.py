from __future__ import annotations

from ...aging.league_factor_store import LeagueFactorStore
from ..baseline_pace_resolver import BaselinePaceResolver
from ...depth.ice_pace_scaler import IcePaceScaler
from ...depth.skater_ice_store import SkaterIceStore
from ...pace_games_resolver import PaceGamesResolver
from ...paths import Paths
from ..projection import Projection
from ...recency.pace_regression_store import PaceRegressionStore
from ...recency_target_resolver import RecencyTargetResolver
from ...skaters.other_league_season_provider import OtherLeagueSeasonProvider
from ...skaters.skater import Skater
from ...skaters.skater_season_provider import SkaterSeasonProvider


class ProjectionCoordinator():
   @classmethod
   def get_projection( cls, player_id: int ) -> Projection | None:
      db_path = str( Paths.DB_PATH )
      pace = BaselinePaceResolver.resolve(
         Skater(
            [
               *SkaterSeasonProvider.seasons_for_player_id( player_id, db_path ),
               *OtherLeagueSeasonProvider.seasons_for_player_id( player_id, db_path ),
            ] ),
         RecencyTargetResolver.resolve(),
         LeagueFactorStore.read(),
         PaceRegressionStore.read() )

      if pace is None:
         return None

      ice = SkaterIceStore.by_player().get( player_id )

      if ice is not None and ice.last_toi:
         pace = IcePaceScaler.adjust(
            pace,
            ice.last_toi,
            ice.projected_toi )

      goals = round( pace.goals )
      assists = round( pace.assists )
      return Projection(
         goals=goals,
         assists=assists,
         points=goals + assists,
         games_played=PaceGamesResolver.resolve() )
