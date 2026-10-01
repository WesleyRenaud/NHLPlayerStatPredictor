from __future__ import annotations

from collections.abc import Callable

from .linear_system import LinearSystem
from .pace_sample import PaceSample
from .prior_year import PriorYear
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason


class WeightedPaceSolver():
   @classmethod
   def solve(
         cls,
         samples: list[ PaceSample ],
         prior_value: Callable[ [ PriorYear ], float ],
         actual: Callable[ [ NhlSkaterSeason ], float ] ) -> tuple[ float, list[ float ] ]:
      size = len( samples[ Position.FIRST ].priors ) + 1
      products = [ [ 0.0 ] * size for _ in range( size ) ]
      targets = [ 0.0 ] * size

      for sample in samples:
         features = [ 1.0, *[ prior_value( prior ) for prior in sample.priors ] ]
         games = float( sample.current.games_played )

         for row in range( size ):
            targets[ row ] += games * features[ row ] * actual( sample.current )

            for column in range( size ):
               products[ row ][ column ] += games * features[ row ] * features[ column ]

      constant, *weights = LinearSystem.solve( products, targets )
      return constant, weights