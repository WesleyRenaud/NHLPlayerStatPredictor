from __future__ import annotations

from api.projections.projection import Projection


def Test_ToDict_TestProjection_ExpectMappedFields() -> None:
   projection = Projection( 12, 34, 46, 70 )
   payload = projection.to_dict()
   assert payload[ 'goals' ] == projection.goals
   assert payload[ 'assists' ] == projection.assists
   assert payload[ 'points' ] == projection.points
   assert payload[ 'gamesPlayed' ] == projection.games_played
