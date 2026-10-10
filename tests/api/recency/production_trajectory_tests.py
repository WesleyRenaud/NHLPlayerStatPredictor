from __future__ import annotations

import pytest

from api.recency.production_season import ProductionSeason
from api.recency.production_trajectory import ProductionTrajectory
from api.recency.production_trajectory_fit import ProductionTrajectoryFit
from api.recency.production_trajectory_share import ProductionTrajectoryShare


def _season( age: int, pace: float, games: int = 82 ) -> ProductionSeason:
   return ProductionSeason( age, pace, games )


def _fit(
      age: int,
      rise: float | None,
      drop: float | None,
      trust: float | None = None ) -> ProductionTrajectoryFit:
   return ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( age, rise, drop, trust ) ] )


def _flatness( prior: ProductionSeason, earlier: ProductionSeason, move: float ) -> float:
   peak = max( prior.pace, earlier.pace )
   return 1.0 - abs( prior.pace - earlier.pace ) / peak / move


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


def Test_Shares_TestLevelThenDip_ExpectDipDropped() -> None:
   history = [ _season( 30, 50.0 ), _season( 29, 80.0 ), _season( 28, 80.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70
   trust = 1.0
   _latest, prior, earlier = history
   fit = _fit( 30, None, drop, trust )
   given_back = trust * _flatness( prior, earlier, fit.move )
   latest = drop * ( 1.0 - given_back ) * sum( bases )
   rest = sum( bases ) - latest
   older = sum( bases[ 1 : ] )

   shares = ProductionTrajectory.shares( history, bases, fit )

   assert shares[ 0 ] == pytest.approx( latest )
   assert shares[ 1 ] == pytest.approx( rest * bases[ 1 ] / older )
   assert shares[ 2 ] == pytest.approx( rest * bases[ 2 ] / older )


def Test_Shares_TestHalfLevel_ExpectHalfTheDropWeight() -> None:
   history = [ _season( 27, 40.0 ), _season( 26, 74.0 ), _season( 25, 80.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70
   trust = 1.0
   _latest, prior, earlier = history
   fit = _fit( 27, None, drop, trust )
   given_back = trust * _flatness( prior, earlier, fit.move )

   shares = ProductionTrajectory.shares( history, bases, fit )

   assert shares[ 0 ] == pytest.approx( drop * ( 1.0 - given_back ) * len( bases ) )


def Test_Shares_TestScoringLevel_ExpectComponentDipFaded() -> None:
   history = [ _season( 29, 40.0 ), _season( 28, 60.0 ), _season( 27, 90.0 ) ]
   curve = [ _season( 29, 60.0 ), _season( 28, 90.0 ), _season( 27, 92.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70
   trust = 1.0
   _latest, prior, earlier = curve
   fit = _fit( 29, None, drop, trust )
   given_back = trust * _flatness( prior, earlier, fit.move )

   shares = ProductionTrajectory.shares( history, bases, fit, curve )

   assert shares[ 0 ] == pytest.approx( drop * ( 1.0 - given_back ) * len( bases ) )


def Test_Shares_TestScoringAlreadyFalling_ExpectComponentDropKept() -> None:
   history = [ _season( 30, 50.0 ), _season( 29, 80.0 ), _season( 28, 80.0 ) ]
   curve = [ _season( 30, 50.0 ), _season( 29, 70.0 ), _season( 28, 90.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70

   shares = ProductionTrajectory.shares( history, bases, _fit( 30, None, drop ), curve )

   assert shares[ 0 ] == pytest.approx( drop * len( bases ) )


def Test_Shares_TestSmallScoringDip_ExpectComponentDropKept() -> None:
   history = [ _season( 30, 10.0 ), _season( 29, 20.0 ), _season( 28, 21.0 ) ]
   curve = [ _season( 30, 42.0 ), _season( 29, 43.0 ), _season( 28, 40.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70

   shares = ProductionTrajectory.shares( history, bases, _fit( 30, None, drop ), curve )

   assert shares[ 0 ] == pytest.approx( drop * len( bases ) )


def Test_Shares_TestNoLevelTrust_ExpectDropKept() -> None:
   history = [ _season( 24, 60.0 ), _season( 23, 90.0 ), _season( 22, 90.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70

   shares = ProductionTrajectory.shares( history, bases, _fit( 24, None, drop, 0.0 ) )

   assert shares[ 0 ] == pytest.approx( drop * len( bases ) )


def Test_Shares_TestAgeBetweenTrusts_ExpectInterpolatedPull() -> None:
   history = [ _season( 32, 60.0 ), _season( 31, 90.0 ), _season( 30, 90.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70
   young_age = 30
   old_age = 34
   young_trust = 1.0
   old_trust = 0.0
   fit = ProductionTrajectoryFit( 0.15, [
      ProductionTrajectoryShare( young_age, None, drop, young_trust ),
      ProductionTrajectoryShare( old_age, None, drop, old_trust ),
   ] )
   latest, prior, earlier = history
   span = old_age - young_age
   trust = young_trust + ( old_trust - young_trust ) * ( latest.age - young_age ) / span
   given_back = trust * _flatness( prior, earlier, fit.move )

   shares = ProductionTrajectory.shares( history, bases, fit )

   assert shares[ 0 ] == pytest.approx( drop * ( 1.0 - given_back ) * len( bases ) )


def Test_Shares_TestOlderThanFittedTrust_ExpectEndpoint() -> None:
   history = [ _season( 36, 60.0 ), _season( 35, 90.0 ), _season( 34, 90.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70
   oldest_trust = 0.2
   fit = ProductionTrajectoryFit( 0.15, [
      ProductionTrajectoryShare( 30, None, drop, 1.0 ),
      ProductionTrajectoryShare( 34, None, drop, oldest_trust ),
   ] )
   _latest, prior, earlier = history
   given_back = oldest_trust * _flatness( prior, earlier, fit.move )

   shares = ProductionTrajectory.shares( history, bases, fit )

   assert shares[ 0 ] == pytest.approx( drop * ( 1.0 - given_back ) * len( bases ) )


def Test_Shares_TestPrimeDropOffSpike_ExpectDropKept() -> None:
   history = [ _season( 30, 50.0 ), _season( 29, 90.0 ), _season( 28, 60.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70

   shares = ProductionTrajectory.shares( history, bases, _fit( 30, None, drop ) )

   assert shares[ 0 ] == pytest.approx( drop * len( bases ) )


def Test_Shares_TestPrimeSlide_ExpectDropKept() -> None:
   history = [ _season( 31, 50.0 ), _season( 30, 70.0 ), _season( 29, 90.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70

   shares = ProductionTrajectory.shares( history, bases, _fit( 31, None, drop ) )

   assert shares[ 0 ] == pytest.approx( drop * len( bases ) )


def Test_Shares_TestAgingSlide_ExpectDropKept() -> None:
   history = [ _season( 33, 60.0 ), _season( 32, 75.0 ), _season( 31, 95.0 ) ]
   bases = [ 1.0, 1.0, 1.0 ]
   drop = 0.70

   shares = ProductionTrajectory.shares( history, bases, _fit( 33, None, drop ) )

   assert shares[ 0 ] == pytest.approx( drop * len( bases ) )


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
