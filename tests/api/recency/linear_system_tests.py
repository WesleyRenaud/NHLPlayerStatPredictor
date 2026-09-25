from __future__ import annotations

from api.recency.linear_system import LinearSystem


def Test_Solve_TestDiagonal_ExpectQuotients() -> None:
   first_product = 2.0
   second_product = 4.0
   first_target = 2.0
   second_target = 8.0
   products = [
      [ first_product, 0.0 ],
      [ 0.0, second_product ],
   ]
   targets = [ first_target, second_target ]

   solution = LinearSystem.solve( products, targets )

   assert solution == [ first_target / first_product, second_target / second_product ]


def Test_Solve_TestOffDiagonal_ExpectUniqueSolution() -> None:
   x = 2.0
   y = 1.0
   first_row = [ 2.0, 1.0 ]
   second_row = [ 1.0, 2.0 ]
   products = [ first_row, second_row ]
   targets = [
      first_row[ 0 ] * x + first_row[ 1 ] * y,
      second_row[ 0 ] * x + second_row[ 1 ] * y,
   ]

   solution = LinearSystem.solve( products, targets )

   assert solution == [ x, y ]
