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
      return cls._reduce( matrix, size )


   @classmethod
   def _reduce( cls, matrix: list[ list[ float ] ], size: int ) -> list[ float ]:
      pivot_row = 0
      pivot_columns: list[ int ] = []

      for column in range( size ):
         selected_row = cls._pivot( matrix, pivot_row, column, size )

         if matrix[ selected_row ][ column ] == 0.0:
            continue

         matrix[ pivot_row ], matrix[ selected_row ] = (
            matrix[ selected_row ], matrix[ pivot_row ] )
         cls._scale( matrix, pivot_row, column )
         cls._eliminate( matrix, pivot_row, column, size )
         pivot_columns.append( column )
         pivot_row += 1

         if pivot_row == size:
            break

      solution = [ 0.0 ] * size

      for row, column in enumerate( pivot_columns ):
         solution[ column ] = matrix[ row ][ size ]

      return solution


   @classmethod
   def _pivot(
         cls,
         matrix: list[ list[ float ] ],
         pivot_row: int,
         column: int,
         size: int ) -> int:
      selected_row = pivot_row

      for row in range( pivot_row + 1, size ):
         if abs( matrix[ row ][ column ] ) > abs( matrix[ selected_row ][ column ] ):
            selected_row = row

      return selected_row


   @classmethod
   def _scale(
         cls,
         matrix: list[ list[ float ] ],
         pivot_row: int,
         column: int ) -> None:
      pivot = matrix[ pivot_row ][ column ]
      matrix[ pivot_row ] = [ value / pivot for value in matrix[ pivot_row ] ]


   @classmethod
   def _eliminate(
         cls,
         matrix: list[ list[ float ] ],
         pivot_row: int,
         column: int,
         size: int ) -> None:
      for row in range( size ):
         if row == pivot_row:
            continue

         factor = matrix[ row ][ column ]
         matrix[ row ] = [
            value - factor * matrix[ pivot_row ][ offset ]
            for offset, value in enumerate( matrix[ row ] )
         ]
