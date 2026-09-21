from __future__ import annotations

from .career_pace import CareerPace
from .team_environment import TeamEnvironment


class TeamPaceAdjuster():
   @classmethod
   def adjust( cls, pace: CareerPace, environment: TeamEnvironment ) -> CareerPace:
      if not environment.last_season_quality:
         return pace

      ratio = environment.roster_quality / environment.last_season_quality
      return CareerPace(
         goals=pace.goals * ratio,
         assists=pace.assists * ratio )
