from __future__ import annotations

from dataclasses import dataclass, field

from .depth_group import DepthGroup
from .skater_group import SkaterGroup
from .team import Team
from .team_factor_skater import TeamFactorSkater
from .teammate_mixer import TeammateMixer
from .teammate_skater import TeammateSkater
from .types import Types


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
         rate=float( row[ 'rate' ] ),
         skaters=[
            TeamFactorSkater.from_row( skater )
            for skater in row[ 'skaters' ] ] )


   def to_dict( self ) -> dict[ str, object ]:
      return {
         'season': self.season,
         'team': self.team.value,
         'rate': self.rate,
         'skaters': [ skater.to_dict() for skater in self.skaters ],
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


   def excluding( self, player_id: int ) -> float:
      total = self.dressed_total()
      return self.rate * self._teammates( player_id ) / total


   def _teammates( self, player_id: int ) -> float:
      f_reg, f_ext, d_reg, d_ext = self._groups()
      forward = TeammateMixer.expected(
         f_reg,
         f_ext,
         [],
         DepthGroup.forwards() )
      defense = TeammateMixer.expected(
         d_reg,
         d_ext,
         [],
         DepthGroup.defense() )

      if self._in( player_id, f_reg, f_ext ):
         return TeammateMixer.teammates(
            player_id,
            f_reg,
            f_ext,
            [],
            DepthGroup.forwards() ) + defense

      if self._in( player_id, d_reg, d_ext ):
         return forward + TeammateMixer.teammates(
            player_id,
            d_reg,
            d_ext,
            [],
            DepthGroup.defense() )

      return forward + defense


   @staticmethod
   def _in(
         player_id: int,
         regulars: list[ TeammateSkater ],
         extras: list[ TeammateSkater ] ) -> bool:
      return any(
         skater.player_id == player_id
         for skater in ( *regulars, *extras ) )


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


   @classmethod
   def rate(
         cls,
         factors: list[ TeamFactor ],
         season: int,
         team: Team ) -> float:
      for factor in factors:
         if factor.season == season and factor.team == team:
            return factor.rate


   @classmethod
   def teammate_rate(
         cls,
         factors: list[ TeamFactor ],
         season: int,
         team: Team,
         player_id: int ) -> float:
      for factor in factors:
         if factor.season == season and factor.team == team:
            return factor.excluding( player_id )
