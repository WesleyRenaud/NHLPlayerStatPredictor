from __future__ import annotations

from dataclasses import dataclass, field

from .team import Team
from .team_factor_skater import TeamFactorSkater
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


   def excluding( self, player_id: int ) -> float:
      total = 0.0
      contribution = 0.0

      for skater in self.skaters:
         total += skater.contribution

         if skater.player_id == player_id:
            contribution = skater.contribution

      if not total:
         return self.rate

      return self.rate * ( total - contribution ) / total


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
   def mate_rate(
         cls,
         factors: list[ TeamFactor ],
         season: int,
         team: Team,
         player_id: int ) -> float:
      for factor in factors:
         if factor.season == season and factor.team == team:
            return factor.excluding( player_id )
