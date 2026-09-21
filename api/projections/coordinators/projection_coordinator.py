from __future__ import annotations

from ...aging_factor_store import AgingFactorStore
from ..aging_pace_adjuster import AgingPaceAdjuster
from ..last_season_skater_builder import LastSeasonSkaterBuilder
from ...league_factor_store import LeagueFactorStore
from ...other_league_season_provider import OtherLeagueSeasonProvider
from ...pace_games_resolver import PaceGamesResolver
from ...paths import Paths
from ..projection import Projection
from ...recency_target_resolver import RecencyTargetResolver
from ...recency_weight_store import RecencyWeightStore
from ...roster_skater_provider import RosterSkaterProvider
from ...shared.enums.position import Position
from ...skater_season_provider import SkaterSeasonProvider
from ..team_environment_resolver import TeamEnvironmentResolver
from ..team_pace_adjuster import TeamPaceAdjuster
from ..translated_pace_averager import TranslatedPaceAverager


class ProjectionCoordinator():
   @classmethod
   def get_projection( cls, player_id: int ) -> Projection | None:
      db_path = str( Paths.DB_PATH )
      seasons = SkaterSeasonProvider.seasons_for_player_id( player_id, db_path )
      other_seasons = OtherLeagueSeasonProvider.seasons_for_player_id(
         player_id,
         db_path )
      target_season_id = RecencyTargetResolver.resolve()
      league_factors = LeagueFactorStore.read()
      pace = TranslatedPaceAverager.average(
         seasons,
         other_seasons,
         RecencyWeightStore.read(),
         target_season_id,
         league_factors )

      if pace is None:
         return None

      age_source = seasons if seasons else other_seasons
      aged = AgingPaceAdjuster.adjust(
         pace,
         int( age_source[ Position.LAST ].age ),
         AgingFactorStore.read(),
         seasons )
      last_season_id = RecencyTargetResolver.prior()
      scaled = TeamPaceAdjuster.adjust(
         aged,
         TeamEnvironmentResolver.resolve(
            player_id,
            RosterSkaterProvider.skaters( db_path ),
            LastSeasonSkaterBuilder.build(
               SkaterSeasonProvider.seasons_for_season_id( last_season_id, db_path ),
               OtherLeagueSeasonProvider.seasons_for_season_id(
                  last_season_id,
                  db_path ),
               league_factors ) ) )
      goals = round( scaled.goals )
      assists = round( scaled.assists )
      return Projection(
         goals=goals,
         assists=assists,
         points=goals + assists,
         games_played=PaceGamesResolver.resolve() )
