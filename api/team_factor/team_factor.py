from __future__ import annotations

from dataclasses import dataclass, field

from ..depth.depth_group import DepthGroup
from ..skaters.skater_group import SkaterGroup
from ..skaters.team import Team
from .team_factor_skater import TeamFactorSkater
from .teammate_mixer import TeammateMixer
from .teammate_skater import TeammateSkater
from ..types import Types


@dataclass( frozen=True )
class TeamFactor():
   season: int
   team: Team
   rate: float
   skaters: list[ TeamFactorSkater ] = field( default_factory=list )


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> TeamFactor:
      return cls(
         season=int( row[ 'season' ] ),
         team=Team( str( row[ 'team' ] ) ),
         rate=float( row[ 'rate' ] ) )


   def to_dict( self ) -> dict[ str, object ]:
      return {
         'season': self.season,
         'team': self.team.value,
         'rate': self.rate,
      }


   def dressed_total( self ) -> float:
      f_reg, f_ext, d_reg, d_ext = self._groups()
      return TeammateMixer.expected(
         f_reg,
         f_ext,
         [],
         DepthGroup.forwards() ) + TeammateMixer.expected(
            d_reg,
            d_ext,
            [],
            DepthGroup.defense() )


   def _groups(
         self ) -> tuple[
            list[ TeammateSkater ],
            list[ TeammateSkater ],
            list[ TeammateSkater ],
            list[ TeammateSkater ] ]:
      f_reg = []
      f_ext = []
      d_reg = []
      d_ext = []

      for skater in self.skaters:
         teammate = TeammateSkater(
            skater.player_id,
            skater.contribution,
            skater.availability,
            skater.prior_availability )
         extras = d_ext if skater.skater_group is SkaterGroup.DEFENSE else f_ext
         regulars = d_reg if skater.skater_group is SkaterGroup.DEFENSE else f_reg

         if skater.extra:
            extras.append( teammate )
         else:
            regulars.append( teammate )

      return f_reg, f_ext, d_reg, d_ext
