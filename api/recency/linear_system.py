from __future__ import annotations


class LinearSystem():
   @classmethod
   def solve(
         cls,
         products: list[ list[ float ] ],
         targets: list[ float ] ) -> list[ float ]:
      size = len( targets )
      matrix = [
         [ *products[ row ], targets[ row ] ]
         for row in range( size )
      ]
      cls._reduce( matrix, size )
      return [ matrix[ row ][ size ] for row in range( size ) ]


   @classmethod
   def _reduce( cls, matrix: list[ list[ float ] ], size: int ) -> None:
      for column in range( size ):
         cls._pivot( matrix, column, size )
         cls._scale( matrix, column )
         cls._eliminate( matrix, column, size )


   @classmethod
   def _pivot(
         cls,
         matrix: list[ list[ float ] ],
         column: int,
         size: int ) -> None:
      pivot_row = column

      for row in range( column + 1, size ):
         if abs( matrix[ row ][ column ] ) > abs( matrix[ pivot_row ][ column ] ):
            pivot_row = row

      matrix[ column ], matrix[ pivot_row ] = matrix[ pivot_row ], matrix[ column ]


   @classmethod
   def _scale( cls, matrix: list[ list[ float ] ], column: int ) -> None:
      pivot = matrix[ column ][ column ]
      matrix[ column ] = [ value / pivot for value in matrix[ column ] ]


   @classmethod
   def _eliminate(
         cls,
         matrix: list[ list[ float ] ],
         column: int,
         size: int ) -> None:
      for row in range( size ):
         if row == column:
            continue

         factor = matrix[ row ][ column ]
         matrix[ row ] = [
            value - factor * matrix[ column ][ offset ]
            for offset, value in enumerate( matrix[ row ] )
         ]
