from __future__ import annotations

import pytest

from api.recency.production_season import ProductionSeason
from api.recency.production_trajectory import ProductionTrajectory
from api.recency.production_trajectory_fit import ProductionTrajectoryFit
from api.recency.production_trajectory_share import ProductionTrajectoryShare


def _season( age: int, pace: float, games: int = 82 ) -> ProductionSeason:
   return ProductionSeason( age, pace, games )


def _fit( age: int, rise: float | None, drop: float | None ) -> ProductionTrajectoryFit:
   return ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( age, rise, drop ) ] )


def Test_Shares_TestStickyRise_ExpectLatestSeasonRaised() -> None:
   history = [ _season( 24, 80.0 ), _season( 23, 50.0 ), _season( 22, 48.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   rise = 0.65

   shares = ProductionTrajectory.shares( history, bases, _fit( 24, rise, None ) )

   assert shares[ 0 ] == pytest.approx( rise * len( bases ) )
   assert shares[ 0 ] > bases[ 0 ]


def Test_Shares_TestFadedRise_ExpectSpikeReduced() -> None:
   history = [ _season( 34, 80.0 ), _season( 33, 50.0 ), _season( 32, 48.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   rise = 0.25

   shares = ProductionTrajectory.shares( history, bases, _fit( 34, rise, None ) )

   assert shares[ 0 ] == pytest.approx( rise * len( bases ) )
   assert shares[ 0 ] < bases[ 0 ]


def Test_Shares_TestFadedDrop_ExpectDropKeptSmall() -> None:
   history = [ _season( 30, 60.0 ), _season( 29, 90.0 ), _season( 28, 92.0 ) ]
   bases = [ 2.0, 1.0, 1.0 ]
   drop = 0.40

   shares = ProductionTrajectory.shares( history, bases, _fit( 30, None, drop ) )

   assert shares[ 0 ] == pytest.approx( drop * sum( bases ) )
   assert sum( shares[ 1 : ] ) > shares[ 0 ]


def Test_Shares_TestStickyDrop_ExpectDropKept() -> None:
   history = [ _season( 34, 60.0 ), _season( 33, 90.0 ), _season( 32, 92.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70

   shares = ProductionTrajectory.shares( history, bases, _fit( 34, None, drop ) )

   assert shares[ 0 ] == pytest.approx( drop * len( bases ) )
   assert shares[ 0 ] > sum( shares[ 1 : ] )


def Test_Shares_TestSmallMove_ExpectAgeWeightsKept() -> None:
   history = [ _season( 28, 52.0 ), _season( 27, 50.0 ) ]
   bases = [ 0.6, 0.4 ]

   assert ProductionTrajectory.shares( history, bases, _fit( 28, 0.65, 0.70 ) ) == bases


def Test_Shares_TestEmptyFit_ExpectAgeWeightsKept() -> None:
   history = [ _season( 24, 80.0 ), _season( 23, 50.0 ) ]
   bases = [ 1.0, 1.0 ]

   assert ProductionTrajectory.shares( history, bases, ProductionTrajectoryFit.empty() ) == bases


def Test_Shares_TestUnfittedAge_ExpectNearestAge() -> None:
   history = [ _season( 36, 80.0 ), _season( 35, 50.0 ) ]
   bases = [ 1.0, 1.0 ]
   rise = 0.25
   fit = ProductionTrajectoryFit( 0.15, [
      ProductionTrajectoryShare( 30, 0.80, None ),
      ProductionTrajectoryShare( 34, rise, None ),
   ] )

   shares = ProductionTrajectory.shares( history, bases, fit )

   assert shares[ 0 ] == pytest.approx( rise * len( bases ) )
