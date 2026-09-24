from __future__ import annotations

from ...aging_factor_store import AgingFactorStore
from ..baseline_pace_resolver import BaselinePaceResolver
from ...ice_pace_scaler import IcePaceScaler
from ...league_factor_store import LeagueFactorStore
from ...other_league_season_provider import OtherLeagueSeasonProvider
from ...pace_games_resolver import PaceGamesResolver
from ...paths import Paths
from ..projection import Projection
from ...recency_target_resolver import RecencyTargetResolver
from ...roster_skater_provider import RosterSkaterProvider
from ...scoring_weight_store import ScoringWeightStore
from ...shared.enums.position import Position
from ...skater import Skater
from ...skater_ice_store import SkaterIceStore
from ...skater_season_provider import SkaterSeasonProvider
from ...team_factor import TeamFactor
from ...team_factor_store import TeamFactorStore
from ..team_pace_adjuster import TeamPaceAdjuster


class ProjectionCoordinator():
   @classmethod
   def get_projection( cls, player_id: int ) -> Projection | None:
      db_path = str( Paths.DB_PATH )
      nhl = SkaterSeasonProvider.seasons_for_player_id( player_id, db_path )
      target_season_id = RecencyTargetResolver.resolve()
      aged = BaselinePaceResolver.resolve(
         Skater(
            [
               *nhl,
               *OtherLeagueSeasonProvider.seasons_for_player_id( player_id, db_path ),
            ] ),
         ScoringWeightStore.read(),
         target_season_id,
         LeagueFactorStore.read(),
         AgingFactorStore.read() )

      if aged is None:
         return None

      current_team = RosterSkaterProvider.team( player_id, db_path )
      scaled = aged

      if current_team is not None and nhl:
         previous = nhl[ Position.LAST ]
         factors = TeamFactorStore.read()
         scaled = TeamPaceAdjuster.adjust(
            aged,
            TeamFactor.teammate_rate(
               factors,
               target_season_id,
               current_team,
               player_id ),
            TeamFactor.teammate_rate(
               factors,
               previous.season_id,
               previous.team,
               player_id ) )

      ice = SkaterIceStore.by_player().get( player_id )

      if ice is not None and ice.last_toi is not None:
         scaled = IcePaceScaler.adjust(
            scaled,
            ice.last_toi,
            ice.projected_toi )

      goals = round( scaled.goals )
      assists = round( scaled.assists )
      return Projection(
         goals=goals,
         assists=assists,
         points=goals + assists,
         games_played=PaceGamesResolver.resolve() )
