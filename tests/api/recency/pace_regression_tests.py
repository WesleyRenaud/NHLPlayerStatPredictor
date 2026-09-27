from __future__ import annotations

import pytest

from api.projections.season_pace import SeasonPace
from api.recency.age_band import AgeBand
from api.recency.pace_regression import PaceRegression
from api.recency.prior_source import PriorSource
from api.recency.prior_year import PriorYear


def _prior( year: int, goals: float, assists: float ) -> PriorYear:
   return PriorYear( year, SeasonPace( goals, assists ), 82, 82, 27.5 )


def Test_FromRow_TestDict_ExpectRoundTrip() -> None:
   regression = PaceRegression(
      PriorSource.TRANSLATED,
      AgeBand( 20, 21 ),
      2.8,
      [ 0.59, 0.22 ],
      3.1,
      [ 0.6, 0.2 ] )

   loaded = PaceRegression.from_row( regression.to_dict() )

   assert loaded == regression


def Test_Covers_TestSourceAgeAndWidth_ExpectAllMatch() -> None:
   regression = PaceRegression( PriorSource.NHL, AgeBand( 25, 26 ), 0.0, [ 0.5, 0.3 ], 0.0, [ 0.5, 0.3 ] )

   assert regression.covers( PriorSource.NHL, 25, 2 )
   assert regression.covers( PriorSource.NHL, 26, 2 )
   assert not regression.covers( PriorSource.NHL, 27, 2 )
   assert not regression.covers( PriorSource.NHL, 25, 1 )
   assert not regression.covers( PriorSource.TRANSLATED, 25, 2 )


def Test_Pace_TestPriors_ExpectConstantPlusWeightedPriors() -> None:
   regression = PaceRegression( PriorSource.NHL, AgeBand( 25, 26 ), 2.0, [ 0.5, 0.25 ], 1.0, [ 0.4, 0.2 ] )

   paced = regression.pace( [ _prior( 2024, 20.0, 30.0 ), _prior( 2023, 12.0, 10.0 ) ] )

   assert paced.goals == pytest.approx( 15.0 )
   assert paced.assists == pytest.approx( 15.0 )

