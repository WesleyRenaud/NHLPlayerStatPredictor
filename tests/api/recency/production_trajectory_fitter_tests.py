from __future__ import annotations

import pytest

from api.projections.scoring_paces import ScoringPaces
from api.recency.prior_year import PriorYear
from api.recency.production_coefficient_fitter import ProductionCoefficientFitter
from api.recency.production_growth import ProductionGrowth
from api.recency.production_trajectory_change import ProductionTrajectoryChange
from api.recency.production_trajectory_fit import ProductionTrajectoryFit
from api.recency.production_trajectory_fitter import ProductionTrajectoryFitter
from api.recency.production_trajectory_share import ProductionTrajectoryShare
from api.shared.enums.position import Position


def _change(
      age: int,
      prior: float,
      latest: float,
      following: float,
      multiplier: float = 1.0,
      games: int = 1,
      earlier: float | None = None ) -> ProductionTrajectoryChange:
   return ProductionTrajectoryChange( age, prior, latest, following, multiplier, games, earlier )


def _pace( prior: PriorYear ) -> float:
   return prior.scoring.goals + prior.scoring.assists


def _prior(
      year: int,
      age: int,
      points: float,
      games: int = 82,
      nhl_games: int | None = None ) -> PriorYear:
   return PriorYear(
      year, ScoringPaces( points, 0.0, 0.0, 0.0, 0.0, 0.0 ),
      0.0, games, games if nhl_games is None else nhl_games, age )


def _at( fit: ProductionTrajectoryFit, age: int ) -> ProductionTrajectoryShare:
   return next( share for share in fit.by_age if share.age == age )


def Test_Fit_TestRetainedFraction_ExpectGamesWeightedShare() -> None:
   kept = [ _change( 24, 10.0, 20.0, 20.0 ) for _index in range( ProductionCoefficientFitter.MIN_SUPPORT - 1 ) ]
   given_back = _change( 24, 10.0, 20.0, 10.0, games=19 )

   changes = [ *kept, given_back ]
   fit = ProductionTrajectoryFitter.fit( changes )
   still_present = sum( change.games * change.still_present() for change in changes )
   pace_change = sum( change.games * change.pace_change() for change in changes )

   assert fit is not None
   assert _at( fit, 24 ).rise_share == pytest.approx( still_present / pace_change )
   assert _at( fit, 24 ).drop_share is None


def Test_Fit_TestSmallSwing_ExpectExcluded() -> None:
   support = ProductionCoefficientFitter.MIN_SUPPORT
   loud = [ _change( 24, 40.0, 80.0, 140.0, multiplier=2.0 ) for _index in range( support ) ]
   tiny = [ _change( 24, 50.0, 50.5, 0.0 ) for _index in range( support ) ]

   fit = ProductionTrajectoryFitter.fit( [ *loud, *tiny ] )
   sample = loud[ 0 ]

   assert fit is not None
   assert _at( fit, 24 ).rise_share == pytest.approx( sample.still_present() / sample.pace_change() )


def Test_Fit_TestTypicalSwing_ExpectMedianMove() -> None:
   changes = [
      _change( 24, 80.0, 100.0, 100.0 ),
      _change( 24, 50.0, 100.0, 100.0 ),
   ]

   for _index in range( ProductionCoefficientFitter.MIN_SUPPORT - 1 ):
      changes.append( _change( 24, 40.0, 80.0, 80.0 ) )

   fit = ProductionTrajectoryFitter.fit( changes )
   repeated = _change( 24, 40.0, 80.0, 80.0 )

   assert fit is not None
   assert fit.move == pytest.approx( repeated.relative() )


def Test_Fit_TestThinHistory_ExpectNoAgeShares() -> None:
   changes = [
      _change( 24, 10.0, 20.0, 20.0 )
      for _index in range( ProductionCoefficientFitter.MIN_SUPPORT - 1 )
   ]

   assert ProductionTrajectoryFitter.fit( changes ).by_age == []


def Test_Observe_TestConsecutiveSeasons_ExpectQualifiedChangesOnly() -> None:
   short = PriorYear.MIN_GAMES - 1
   prior = _prior( 2020, 18, 30.0 )
   latest = _prior( 2021, 19, 60.0 )
   following = _prior( 2022, 20, 90.0 )
   growth = ProductionGrowth( 19, 20, 2.0, 10 )
   history = {
      1: [ prior, latest, following ],
      2: [ _prior( 2020, 18, 30.0 ), _prior( 2022, 20, 60.0 ), _prior( 2023, 21, 90.0 ) ],
      3: [
         _prior( 2020, 18, 30.0, short ),
         _prior( 2021, 19, 60.0, short ),
         _prior( 2022, 20, 90.0, short ),
      ],
   }

   changes = ProductionTrajectoryFitter.observe( history, [ growth ] )

   assert len( changes ) == 1
   change = changes[ Position.FIRST ]
   assert change.age == int( latest.age )
   assert change.prior_pace == pytest.approx( _pace( prior ) )
   assert change.latest_pace == pytest.approx( _pace( latest ) )
   assert change.following_pace == pytest.approx( _pace( following ) )
   assert change.multiplier == pytest.approx( growth.multiplier )
   assert change.games == min( prior.games, latest.games, following.games )
