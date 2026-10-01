from __future__ import annotations

import pytest

from api.recency.age_band import AgeBand
from api.recency.pace_regression import PaceRegression
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.prior_source import PriorSource


def Test_FromRow_TestDict_ExpectRoundTrip() -> None:
   model = PaceRegressionModel(
      [
         PaceRegression(
            source=PriorSource.NHL,
            band=AgeBand( 25, 26 ),
            goal_constant=1.0,
            goal_weights=[ 0.5 ],
            assist_constant=1.0,
            assist_weights=[ 0.5 ],
            power_play_goal_constant=0.0,
            power_play_goal_weights=[ 0.0 ],
            power_play_assist_constant=0.0,
            power_play_assist_weights=[ 0.0 ],
            short_handed_goal_constant=0.0,
            short_handed_goal_weights=[ 0.0 ],
            short_handed_assist_constant=0.0,
            short_handed_assist_weights=[ 0.0 ] ),
         PaceRegression(
            source=PriorSource.TRANSLATED,
            band=AgeBand( 24, 40 ),
            goal_constant=3.0,
            goal_weights=[ 0.8, 0.1 ],
            assist_constant=3.0,
            assist_weights=[ 0.8, 0.1 ],
            power_play_goal_constant=0.0,
            power_play_goal_weights=[ 0.0, 0.0 ],
            power_play_assist_constant=0.0,
            power_play_assist_weights=[ 0.0, 0.0 ],
            short_handed_goal_constant=0.0,
            short_handed_goal_weights=[ 0.0, 0.0 ],
            short_handed_assist_constant=0.0,
            short_handed_assist_weights=[ 0.0, 0.0 ] ),
      ],
      0.8,
      0.9,
      1.1,
      0.7,
      0.95,
      1.05,
      1.0,
      1.0 )

   loaded = PaceRegressionModel.from_row( model.to_dict() )

   assert loaded == model


def Test_FromRow_TestMissingPowerPlayGapScale_ExpectKeyError() -> None:
   model = PaceRegressionModel( [], 0.8, 0.9, 1.1, 0.7, 0.95, 1.05, 1.0, 1.0 )
   row = model.to_dict()
   del row[ 'nhl_gap_power_play_goals' ]

   with pytest.raises( KeyError, match='nhl_gap_power_play_goals' ):
      PaceRegressionModel.from_row( row )
