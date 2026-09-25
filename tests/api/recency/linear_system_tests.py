from __future__ import annotations

from api.recency.linear_system import LinearSystem


def Test_Solve_TestDiagonal_ExpectQuotients() -> None:
   products = [
      [ 2.0, 0.0 ],
      [ 0.0, 4.0 ],
   ]
   targets = [ 2.0, 8.0 ]
   assert LinearSystem.solve( products, targets ) == [ 1.0, 2.0 ]


def Test_Solve_TestOffDiagonal_ExpectUniqueSolution() -> None:
   products = [
      [ 2.0, 1.0 ],
      [ 1.0, 2.0 ],
   ]
   targets = [ 5.0, 4.0 ]
   assert LinearSystem.solve( products, targets ) == [ 2.0, 1.0 ]
