from __future__ import annotations

from dataclasses import replace

import pytest

from api.recency.production_coefficient_fitter import ProductionCoefficientFitter
from api.recency.scoring_component_share_fitter import ScoringComponentShareFitter
from api.shared.enums.position import Position
from tests.api.recency.pace_regression_fitter_tests import _nhl


def Test_Fit_TestUnequalProduction_ExpectSharesOfCounts() -> None:
   first = _nhl( 1, 2020, 10.0, 20.0, 18.4, 2, 8, 1, 3 )
   second = _nhl( 2, 2020, 30.0, 40.0, 18.4, 10, 22, 2, 6 )

   shares = ScoringComponentShareFitter.fit( [ first, second ] )[ Position.FIRST ]

   expected_es_goals = sum(
      season.even_strength_goals
      for season in [ first, second ] )
   expected_es_assists = sum(
      season.even_strength_points - season.even_strength_goals
      for season in [ first, second ] )
   assert shares.even_strength_goals == pytest.approx( expected_es_goals / ( first.goals + second.goals ) )
   assert shares.even_strength_assists == pytest.approx( expected_es_assists / ( first.assists + second.assists ) )
   assert shares.power_play_goals == pytest.approx(
      ( first.power_play_goals + second.power_play_goals ) / ( first.goals + second.goals ) )
   assert shares.power_play_assists == pytest.approx(
      ( first.power_play_points - first.power_play_goals + second.power_play_points - second.power_play_goals )
      / ( first.assists + second.assists ) )


def Test_Fit_TestSparseAge_ExpectNeighborPooling() -> None:
   young = _nhl( 1, 2020, 10.0, 20.0, 18.4, 10, 20 )
   neighbor = _nhl( 2, 2020, 10.0, 20.0, 19.4, 0, 0 )
   seasons = [ young, *[ neighbor ] * ProductionCoefficientFitter.MIN_SUPPORT ]

   shares = ScoringComponentShareFitter.fit( seasons )[ Position.FIRST ]

   assert shares.power_play_goals == pytest.approx( young.power_play_goals / sum( season.goals for season in seasons ) )


def Test_Fit_TestShortStints_ExpectExcluded() -> None:
   season = replace( _nhl( 1, 2020, 10.0, 20.0, 18.4 ), games_played=9 )

   assert ScoringComponentShareFitter.fit( [ season ] ) == []


def Test_Fit_TestNoGoals_ExpectZeroSpecialGoalShares() -> None:
   season = _nhl( 1, 2020, 0.0, 20.0, 18.4, 0, 4 )

   shares = ScoringComponentShareFitter.fit( [ season ] )[ Position.FIRST ]

   assert shares.power_play_goals == 0.0
   assert shares.even_strength_goals == 1.0
   assert shares.short_handed_goals == 0.0
   assert shares.power_play_assists == pytest.approx( season.power_play_points / season.assists )


def Test_Fit_TestNoAssists_ExpectAllAssistShareEvenStrength() -> None:
   season = _nhl( 1, 2020, 10.0, 0.0, 18.4 )

   shares = ScoringComponentShareFitter.fit( [ season ] )[ Position.FIRST ]

   assert shares.even_strength_assists == 1.0
   assert shares.power_play_assists == 0.0
   assert shares.short_handed_assists == 0.0
