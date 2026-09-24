from __future__ import annotations

from .depth_group import DepthGroup
from .team_factor_skater import TeamFactorSkater
from .teammate_skater import TeammateSkater


class TeamFactorRows():
   @classmethod
   def build(
         cls,
         forwards: list[ TeammateSkater ],
         f_extras: list[ TeammateSkater ],
         regulars: list[ TeammateSkater ],
         extras: list[ TeammateSkater ] ) -> list[ TeamFactorSkater ]:
      rows = cls._tagged( forwards, DepthGroup.forwards(), False )
      rows.extend( cls._tagged( f_extras, DepthGroup.forwards(), True ) )
      rows.extend( cls._tagged( regulars, DepthGroup.defense(), False ) )
      rows.extend( cls._tagged( extras, DepthGroup.defense(), True ) )
      return rows


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
