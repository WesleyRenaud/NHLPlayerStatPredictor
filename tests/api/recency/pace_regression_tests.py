from __future__ import annotations

import pytest

from api.projections.power_play_pace import PowerPlayPace
from api.projections.season_pace import SeasonPace
from api.recency.age_band import AgeBand
from api.recency.pace_regression import PaceRegression
from api.recency.prior_source import PriorSource
from api.recency.prior_year import PriorYear


def _prior(
   year: int,
   goals: float,
   assists: float,
   power_play_goals: float = 0.0,
   power_play_assists: float = 0.0 ) -> PriorYear:
   return PriorYear(
      year,
      SeasonPace( goals, assists ),
   PowerPlayPace( power_play_goals, power_play_assists ),
      0.0,
      82,
      82,
      27.5,
      SeasonPace.zero() )


def Test_FromRow_TestDict_ExpectRoundTrip() -> None:
   regression = PaceRegression(
      source=PriorSource.TRANSLATED,
      band=AgeBand( 20, 21 ),
      goal_constant=2.8,
      goal_weights=[ 0.59, 0.22 ],
      assist_constant=3.1,
      assist_weights=[ 0.6, 0.2 ],
      power_play_goal_constant=0.0,
      power_play_goal_weights=[ 0.0, 0.0 ],
      power_play_assist_constant=0.0,
      power_play_assist_weights=[ 0.0, 0.0 ] )

   loaded = PaceRegression.from_row( regression.to_dict() )

   assert loaded == regression


def Test_FromRow_TestMissingPowerPlayCoefficient_ExpectKeyError() -> None:
   regression = PaceRegression(
      source=PriorSource.NHL,
      band=AgeBand( 25, 26 ),
      goal_constant=1.0,
      goal_weights=[ 0.5 ],
      assist_constant=1.0,
      assist_weights=[ 0.5 ],
      power_play_goal_constant=0.2,
      power_play_goal_weights=[ 0.1 ],
      power_play_assist_constant=0.3,
      power_play_assist_weights=[ 0.2 ] )
   row = regression.to_dict()
   del row[ 'power_play_goal_constant' ]

   with pytest.raises( KeyError, match='power_play_goal_constant' ):
      PaceRegression.from_row( row )


def Test_Covers_TestSourceAgeAndWidth_ExpectAllMatch() -> None:
   regression = PaceRegression(
      source=PriorSource.NHL,
      band=AgeBand( 25, 26 ),
      goal_constant=0.0,
      goal_weights=[ 0.5, 0.3 ],
      assist_constant=0.0,
      assist_weights=[ 0.5, 0.3 ],
      power_play_goal_constant=0.0,
      power_play_goal_weights=[ 0.0, 0.0 ],
      power_play_assist_constant=0.0,
      power_play_assist_weights=[ 0.0, 0.0 ] )

   assert regression.covers( PriorSource.NHL, 25, 2 )
   assert regression.covers( PriorSource.NHL, 26, 2 )
   assert not regression.covers( PriorSource.NHL, 27, 2 )
   assert not regression.covers( PriorSource.NHL, 25, 1 )
   assert not regression.covers( PriorSource.TRANSLATED, 25, 2 )


def Test_Pace_TestPriors_ExpectConstantPlusWeightedPriors() -> None:
   regression = PaceRegression(
      source=PriorSource.NHL,
      band=AgeBand( 25, 26 ),
      goal_constant=2.0,
      goal_weights=[ 0.5, 0.25 ],
      assist_constant=1.0,
      assist_weights=[ 0.4, 0.2 ],
      power_play_goal_constant=0.0,
      power_play_goal_weights=[ 0.0, 0.0 ],
      power_play_assist_constant=0.0,
      power_play_assist_weights=[ 0.0, 0.0 ] )

   priors = [ _prior( 2024, 20.0, 30.0 ), _prior( 2023, 12.0, 10.0 ) ]

   paced = regression.paces( priors )

   assert paced.goals == pytest.approx(
      regression.goal_constant
      + sum( weight * prior.pace.goals for weight, prior in zip( regression.goal_weights, priors ) ) )
   assert paced.assists == pytest.approx(
      regression.assist_constant
      + sum( weight * prior.pace.assists for weight, prior in zip( regression.assist_weights, priors ) ) )
   assert paced.power_play_goals == 0.0
   assert paced.power_play_assists == 0.0


def Test_PowerPlayPace_TestPriors_ExpectSeparatePowerPlayValues() -> None:
   regression = PaceRegression(
      source=PriorSource.NHL,
      band=AgeBand( 25, 26 ),
      goal_constant=2.0,
      goal_weights=[ 0.5 ],
      assist_constant=1.0,
      assist_weights=[ 0.25 ],
      power_play_goal_constant=3.0,
      power_play_goal_weights=[ 0.4 ],
      power_play_assist_constant=2.0,
      power_play_assist_weights=[ 0.5 ] )

   prior = _prior( 2024, 20.0, 30.0, 10.0, 8.0 )
   paced = regression.paces( [ prior ] )
   expected_power_play_goals = regression.power_play_goal_constant + sum(
      weight * prior.power_play_pace.goals
      for weight, prior in zip( regression.power_play_goal_weights, [ prior ] ) )
   expected_power_play_assists = regression.power_play_assist_constant + sum(
      weight * prior.power_play_pace.assists
      for weight, prior in zip( regression.power_play_assist_weights, [ prior ] ) )

   assert paced.power_play_goals == pytest.approx( expected_power_play_goals )
   assert paced.power_play_assists == pytest.approx( expected_power_play_assists )

