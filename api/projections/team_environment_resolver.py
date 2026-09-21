from __future__ import annotations

from .last_season_group import LastSeasonGroup
from .last_season_nhl_skater import LastSeasonNhlSkater
from .last_season_skater import LastSeasonSkater
from ..roster_skater import RosterSkater
from ..team import Team
from .team_environment import TeamEnvironment
from .team_quality_calculator import TeamQualityCalculator


class TeamEnvironmentResolver():
   @classmethod
   def resolve(
         cls,
         player_id: int,
         roster: list[ RosterSkater ],
         last_season: LastSeasonGroup ) -> TeamEnvironment:
      return TeamEnvironment(
         cls._roster_quality( player_id, roster, last_season ),
         cls._last_season_quality( player_id, last_season.nhl ) )


   @classmethod
   def _roster_quality(
         cls,
         player_id: int,
         roster: list[ RosterSkater ],
         last_season: LastSeasonGroup ) -> float:
      return cls._quality(
         player_id,
         cls._team( player_id, roster ),
         roster,
         last_season.skaters() )


   @classmethod
   def _last_season_quality(
         cls,
         player_id: int,
         nhl: list[ LastSeasonNhlSkater ] ) -> float:
      return cls._quality(
         player_id,
         cls._team( player_id, nhl ),
         nhl,
         nhl )


   @classmethod
   def _quality(
         cls,
         player_id: int,
         team: Team | None,
         clubs: list[ RosterSkater ] | list[ LastSeasonNhlSkater ],
         paces: list[ LastSeasonSkater ] | list[ LastSeasonNhlSkater ] ) -> float:
      return TeamQualityCalculator.average(
         cls._mates( player_id, paces, cls._ids( team, clubs ) ) )


   @classmethod
   def _ids(
         cls,
         team: Team | None,
         clubs: list[ RosterSkater ] | list[ LastSeasonNhlSkater ] ) -> set[ int ]:
      if team is None:
         return { skater.player_id for skater in clubs }

      return {
         skater.player_id
         for skater in clubs
         if skater.team == team }


   @classmethod
   def _mates(
         cls,
         player_id: int,
         paces: list[ LastSeasonSkater ] | list[ LastSeasonNhlSkater ],
         club_ids: set[ int ] ) -> list[ LastSeasonSkater ] | list[ LastSeasonNhlSkater ]:
      return [
         skater
         for skater in paces
         if skater.player_id in club_ids and skater.player_id != player_id ]


   @classmethod
   def _team(
         cls,
         player_id: int,
         skaters: list[ RosterSkater ] | list[ LastSeasonNhlSkater ] ) -> Team | None:
      for skater in skaters:
         if skater.player_id == player_id:
            return skater.team

      return None
