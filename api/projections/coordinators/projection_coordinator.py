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
from ...skaters.roster_skater_provider import RosterSkaterProvider
from ...skaters.skater import Skater
from ...skaters.skater_season_provider import SkaterSeasonProvider


class ProjectionCoordinator():
   @classmethod
   def get_projection( cls, player_id: int ) -> Projection | None:
      db_path = str( Paths.DB_PATH )

      if RosterSkaterProvider.team( player_id, db_path ) is None:
         return None

      seasons = [
         *SkaterSeasonProvider.seasons_for_player_id( player_id, db_path ),
         *OtherLeagueSeasonProvider.seasons_for_player_id( player_id, db_path ),
      ]
      skater = Skater( seasons )
      target_season = RecencyTargetResolver.resolve()
      league_factors = LeagueFactorStore.read()
      model = PaceRegressionStore.read()
      paces = BaselinePaceResolver.resolve(
         skater,
         target_season,
         league_factors,
         model )

      if paces is None:
         return None

      even_strength_pace = paces.even_strength_pace()
      power_play_pace = paces.power_play_pace()
      short_handed_pace = paces.short_handed_pace()
      pim_pace = paces.penalty_minutes
      shots_pace = paces.shots

      ice = SkaterIceStore.by_player().get( player_id )

      if ice is not None and ice.last_toi:
         even_strength_pace = IcePaceScaler.adjust(
            even_strength_pace,
            ice.last_toi,
            ice.projected_toi )
         power_play_pace = IcePaceScaler.adjust(
            power_play_pace,
            ice.last_toi,
            ice.projected_toi )
         short_handed_pace = IcePaceScaler.adjust(
            short_handed_pace,
            ice.last_toi,
            ice.projected_toi )

         if pim_pace is not None:
            pim_pace *= IcePaceScaler.ratio( ice.last_toi, ice.projected_toi )

         if shots_pace is not None:
            shots_pace *= IcePaceScaler.ratio( ice.last_toi, ice.projected_toi )

      power_play_goals = round( power_play_pace.goals )
      power_play_assists = round( power_play_pace.assists )
      short_handed_goals = round( short_handed_pace.goals )
      short_handed_assists = round( short_handed_pace.assists )
      even_strength_goals = round( even_strength_pace.goals )
      even_strength_assists = round( even_strength_pace.assists )
      return Projection(
         even_strength_goals=even_strength_goals,
         even_strength_points=even_strength_goals + even_strength_assists,
         penalty_minutes=None if pim_pace is None else round( pim_pace ),
         games_played=PaceGamesResolver.resolve(),
         projected_toi=None if ice is None else ice.projected_toi,
         power_play_goals=power_play_goals,
         power_play_points=power_play_goals + power_play_assists,
         short_handed_goals=short_handed_goals,
         short_handed_points=short_handed_goals + short_handed_assists,
         shots=None if shots_pace is None else round( shots_pace ),
         shooting_percentage=(
            None if shots_pace is None or shots_pace == 0.0 else
            100 * ( even_strength_pace.goals + power_play_pace.goals + short_handed_pace.goals ) / shots_pace ) )
