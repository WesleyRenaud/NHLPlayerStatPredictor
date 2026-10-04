from __future__ import annotations

from dataclasses import dataclass

from .draft_pick import DraftPick
from ..types import Types


@dataclass( frozen=True )
class ProspectCalibrationSample():
   player_id: int
   season_id: int
   draft_pick: DraftPick
   predicted_points: float
   actual_points: float
   source_league: str


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProspectCalibrationSample:
      pick = row[ 'draft_pick' ]
      return cls(
         int( row[ 'player_id' ] ), int( row[ 'season_id' ] ),
         DraftPick( None if pick is None else int( pick ) ),
         float( row[ 'predicted_points' ] ), float( row[ 'actual_points' ] ),
         str( row[ 'source_league' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'player_id': self.player_id,
         'season_id': self.season_id,
         'draft_pick': self.draft_pick.value,
         'predicted_points': self.predicted_points,
         'actual_points': self.actual_points,
         'source_league': self.source_league,
      }
