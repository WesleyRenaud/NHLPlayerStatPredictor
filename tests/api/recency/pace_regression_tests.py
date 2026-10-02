from __future__ import annotations

from api.projections.scoring_stat import ScoringStat
from api.recency.pace_regression import PaceRegression
from api.recency.prior_source import PriorSource
from api.recency.production_coefficient import ProductionCoefficient


def Test_FromRow_TestAgePairs_ExpectRoundTrip() -> None:
   regression = PaceRegression(
      PriorSource.NHL,
      ScoringStat.GOALS,
      [ ProductionCoefficient( 18, 19, 1.2, 0.8, 100 ), ProductionCoefficient( 19, 21, 1.1, 0.6, 80 ) ] )

   assert PaceRegression.from_row( regression.to_dict() ) == regression
   assert regression.to_dict()[ 'stat' ] == 'goals'
   assert PaceRegression.from_row( regression.to_dict() ).stat is ScoringStat.GOALS
