from __future__ import annotations

import pytest

from api.projections.prospect_eligibility import ProspectEligibility
from api.projections.scoring_paces import ScoringPaces
from api.recency.prior_year import PriorYear
from api.recency.production_coefficient_fitter import ProductionCoefficientFitter
from api.recency.production_growth import ProductionGrowth
from api.recency.production_trajectory_change import ProductionTrajectoryChange
from api.recency.production_trajectory_fitter import ProductionTrajectoryFitter
from api.shared.enums.position import Position


def _change(
      age: int,
      prior: float,
      latest: float,
      following: float,
      multiplier: float = 1.0,
      games: int = 1 ) -> ProductionTrajectoryChange:
   return ProductionTrajectoryChange( age, prior, latest, following, multiplier, games )


def _pace( prior: PriorYear ) -> float:
   return prior.scoring.goals + prior.scoring.assists


def _prior(
      year: int,
      age: float,
      points: float,
      games: int = 82,
      nhl_games: int | None = None ) -> PriorYear:
   return PriorYear(
      year, ScoringPaces( points, 0.0, 0.0, 0.0, 0.0, 0.0 ),
      0.0, games, games if nhl_games is None else nhl_games, age )


def Test_Fit_TestRetainedFraction_ExpectGamesWeightedShare() -> None:
   kept = [ _change( 24, 10.0, 20.0, 20.0 ) for _index in range( ProductionCoefficientFitter.MIN_SUPPORT - 1 ) ]
   given_back = _change( 24, 10.0, 20.0, 10.0, games=19 )

   fit = ProductionTrajectoryFitter.fit( [ *kept, given_back ] )

   assert fit is not None
   assert fit.retained( 24, True ) == pytest.approx( 0.5 )
   assert fit.retained( 24, False ) is None


def Test_Fit_TestSmallSwing_ExpectExcluded() -> None:
   support = ProductionCoefficientFitter.MIN_SUPPORT
   loud = [ _change( 24, 40.0, 80.0, 140.0, multiplier=2.0 ) for _index in range( support ) ]
   tiny = [ _change( 24, 50.0, 50.5, 0.0 ) for _index in range( support ) ]

   fit = ProductionTrajectoryFitter.fit( [ *loud, *tiny ] )

   assert fit is not None
   assert fit.retained( 24, True ) == pytest.approx( 0.75 )


def Test_Fit_TestTypicalSwing_ExpectMedianMove() -> None:
   changes = [
      _change( 24, 80.0, 100.0, 100.0 ),
      _change( 24, 50.0, 100.0, 100.0 ),
   ]

   for _index in range( ProductionCoefficientFitter.MIN_SUPPORT - 1 ):
      changes.append( _change( 24, 40.0, 80.0, 80.0 ) )

   fit = ProductionTrajectoryFitter.fit( changes )

   assert fit is not None
   assert fit.move == pytest.approx( 0.5 )


def Test_Fit_TestThinHistory_ExpectNoAgeShares() -> None:
   changes = [
      _change( 24, 10.0, 20.0, 20.0 )
      for _index in range( ProductionCoefficientFitter.MIN_SUPPORT - 1 )
   ]

   assert ProductionTrajectoryFitter.fit( changes ).by_age == []


def Test_Observe_TestConsecutiveSeasons_ExpectQualifiedChangesOnly() -> None:
   short = PriorYear.MIN_GAMES - 1
   prior = _prior( 2020, 18.2, 30.0 )
   latest = _prior( 2021, 19.2, 60.0 )
   following = _prior( 2022, 20.2, 90.0 )
   growth = ProductionGrowth( 19, 20, 2.0, 10 )
   history = {
      1: [ prior, latest, following ],
      2: [ _prior( 2020, 18.2, 30.0 ), _prior( 2022, 20.2, 60.0 ), _prior( 2023, 21.2, 90.0 ) ],
      3: [
         _prior( 2020, 18.2, 30.0, short ),
         _prior( 2021, 19.2, 60.0, short ),
         _prior( 2022, 20.2, 90.0, short ),
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


def Test_ObserveDebuts_TestFirstNhlSeason_ExpectTranslatedRiseOnly() -> None:
   established = ProspectEligibility.MAX_NHL_GAMES + 1
   prior = _prior( 2020, 18.2, 30.0, nhl_games=0 )
   latest = _prior( 2021, 19.2, 60.0, nhl_games=0 )
   following = _prior( 2022, 20.2, 90.0 )
   history = {
      1: [ prior, latest, following ],
      2: [
         _prior( 2020, 18.2, 30.0, nhl_games=0 ),
         _prior( 2022, 20.2, 60.0, nhl_games=0 ),
         _prior( 2023, 21.2, 90.0 ),
      ],
      3: [ _prior( 2020, 18.2, 30.0 ), _prior( 2021, 19.2, 60.0 ), _prior( 2022, 20.2, 90.0 ) ],
      4: [
         _prior( 2020, 18.2, 30.0, nhl_games=established ),
         _prior( 2021, 19.2, 60.0, nhl_games=0 ),
         _prior( 2022, 20.2, 90.0 ),
      ],
      5: [
         _prior( 2020, 25.2, 30.0, nhl_games=0 ),
         _prior( 2021, 26.2, 60.0, nhl_games=0 ),
         _prior( 2022, 27.2, 90.0 ),
      ],
   }

   changes = ProductionTrajectoryFitter.observe_debuts( history, [ ProductionGrowth( 19, 20, 2.0, 10 ) ] )

   assert len( changes ) == 1
   change = changes[ Position.FIRST ]
   assert change.age == int( latest.age )
   assert change.prior_pace == pytest.approx( _pace( prior ) )
   assert change.latest_pace == pytest.approx( _pace( latest ) )
   assert change.following_pace == pytest.approx( _pace( following ) )


def Test_ObserveShortNhl_TestShortStint_ExpectSplitYearOnly() -> None:
   prior = _prior( 2020, 18.2, 30.0, nhl_games=0 )
   latest = _prior( 2021, 19.2, 60.0, games=50, nhl_games=9 )
   following = _prior( 2022, 20.2, 90.0 )
   history = {
      1: [ prior, latest, following ],
      2: [
         _prior( 2020, 18.2, 30.0, nhl_games=0 ),
         _prior( 2021, 19.2, 60.0, nhl_games=0 ),
         _prior( 2022, 20.2, 90.0 ),
      ],
      3: [
         _prior( 2020, 18.2, 30.0, nhl_games=0 ),
         _prior( 2021, 19.2, 60.0, games=25, nhl_games=15 ),
         _prior( 2022, 20.2, 90.0 ),
      ],
      4: [
         _prior( 2020, 18.2, 30.0 ),
         _prior( 2021, 19.2, 60.0 ),
         _prior( 2022, 20.2, 90.0 ),
      ],
   }

   changes = ProductionTrajectoryFitter.observe_short_nhl( history, [ ProductionGrowth( 19, 20, 2.0, 10 ) ] )

   assert len( changes ) == 1
   change = changes[ Position.FIRST ]
   assert change.age == int( latest.age )
   assert change.prior_pace == pytest.approx( _pace( prior ) )
   assert change.latest_pace == pytest.approx( _pace( latest ) )
   assert change.following_pace == pytest.approx( _pace( following ) )
