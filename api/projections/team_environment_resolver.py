from __future__ import annotations

from .previous_season_group import PreviousSeasonGroup
from .previous_season_nhl_skater import PreviousSeasonNhlSkater
from .previous_season_skater import PreviousSeasonSkater
from ..skaters.roster_skater import RosterSkater
from .team_environment import TeamEnvironment
from .team_quality_calculator import TeamQualityCalculator


class TeamEnvironmentResolver():
   @classmethod
   def resolve(
         cls,
         player_id: int,
         roster: list[ RosterSkater ],
         previous_season: PreviousSeasonGroup ) -> TeamEnvironment:
      nhl = previous_season.nhl
      return TeamEnvironment(
         cls._quality(
            player_id,
            previous_season.skaters(),
            cls._roster_ids( player_id, roster ) ),
         cls._quality(
            player_id,
            nhl,
            cls._nhl_ids( player_id, nhl ) ) )


   @classmethod
   def _quality(
         cls,
         player_id: int,
         paces: list[ PreviousSeasonSkater ],
         club_ids: set[ int ] ) -> float:
      return TeamQualityCalculator.average(
         cls._teammates( player_id, paces, club_ids ) )


   @classmethod
   def _roster_ids(
         cls,
         player_id: int,
         roster: list[ RosterSkater ] ) -> set[ int ]:
      for skater in roster:
         if skater.player_id == player_id:
            return {
               other.player_id
               for other in roster
               if other.team == skater.team }


   @classmethod
   def _nhl_ids(
         cls,
         player_id: int,
         nhl: list[ PreviousSeasonNhlSkater ] ) -> set[ int ]:
      team = None

      for skater in nhl:
         if skater.player_id == player_id:
            team = skater.team
            break

      if team is None:
         return { skater.player_id for skater in nhl }

      return {
         skater.player_id
         for skater in nhl
         if skater.team == team }


   @classmethod
   def _teammates(
         cls,
         player_id: int,
         paces: list[ PreviousSeasonSkater ],
         club_ids: set[ int ] ) -> list[ PreviousSeasonSkater ]:
      return [
         skater
         for skater in paces
         if skater.player_id in club_ids and skater.player_id != player_id ]
