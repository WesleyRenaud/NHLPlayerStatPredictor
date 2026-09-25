from __future__ import annotations

from ..depth.depth_group import DepthGroup
from .team_factor_skater import TeamFactorSkater
from .teammate_skater import TeammateSkater


class TeamFactorRows():
   @classmethod
   def group(
         cls,
         regulars: list[ TeammateSkater ],
         extras: list[ TeammateSkater ],
         group: DepthGroup ) -> list[ TeamFactorSkater ]:
      return [
         *cls._tagged( regulars, group, False ),
         *cls._tagged( extras, group, True ),
      ]


   @classmethod
   def _tagged(
         cls,
         teammates: list[ TeammateSkater ],
         group: DepthGroup,
         extra: bool ) -> list[ TeamFactorSkater ]:
      return [
         TeamFactorSkater(
            skater.player_id,
            skater.contribution,
            group.skater_group,
            skater.availability,
            extra,
            skater.prior_availability )
         for skater in teammates
      ]
