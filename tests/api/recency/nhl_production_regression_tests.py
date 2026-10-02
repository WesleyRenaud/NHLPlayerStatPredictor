from __future__ import annotations

from dataclasses import replace
from datetime import date
from unittest.mock import Mock

import pytest

from api.recency.nhl_production_regression import NhlProductionRegression
from api.recency.nhl_production_stat import NhlProductionStat
from api.recency.prior_year_builder import PriorYearBuilder
from api.recency.production_coefficient import ProductionCoefficient
from api.recency.production_history_predictor import ProductionHistoryPredictor
from api.season import Season
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


ANNUAL_MULTIPLIER = 2


def _season( player_id: int, year: int, age: float, production: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=year * 10000 + year + 1,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=age,
      team=list( Team )[ Position.FIRST ],
      games_played=82,
      even_strength_goals=0,
      even_strength_points=0,
      goals=0,
      assists=0,
      points=0,
      schedule_games=82,
      pace_games=82,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      penalty_minutes=production,
      shots=production,
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0 )


def _training_seasons() -> list[ NhlSkaterSeason ]:
   return [
      _season( player_id, year, 18.4 + year - 2020, player_id * ANNUAL_MULTIPLIER ** ( year - 2020 ) )
      for player_id in range( 1, 31 )
      for year in range( 2020, 2023 )
   ]


def _pace(
      coefficients: list[ ProductionCoefficient ],
      seasons: list[ NhlSkaterSeason ],
      target_season_id: int,
      stat: NhlProductionStat ) -> float | None:
   year = Season.start_year( target_season_id )
   priors = PriorYearBuilder.build( seasons, [], year, [] )
   return NhlProductionRegression.pace( coefficients, priors, year, stat )


@pytest.mark.parametrize( 'stat', list( NhlProductionStat ) )
def Test_Fit_TestMultiplicativeProduction_ExpectAgeMultipliers( stat: NhlProductionStat ) -> None:
   coefficients = NhlProductionRegression.fit( _training_seasons(), stat )

   assert next( coefficient for coefficient in coefficients if coefficient.from_age == 18 and coefficient.to_age == 19 ).multiplier == pytest.approx( ANNUAL_MULTIPLIER )
   assert next( coefficient for coefficient in coefficients if coefficient.from_age == 18 and coefficient.to_age == 20 ).multiplier == pytest.approx( ANNUAL_MULTIPLIER ** 2 )
   assert next( coefficient for coefficient in coefficients if coefficient.from_age == 18 and coefficient.to_age == 20 ).weight == pytest.approx( 1.0 )


@pytest.mark.parametrize( 'stat', list( NhlProductionStat ) )
def Test_Fit_TestNoPairs_ExpectEmptyCoefficients( stat: NhlProductionStat ) -> None:
   assert NhlProductionRegression.fit( [], stat ) == []


def Test_Fit_TestMultipleYears_ExpectOneHistoryPreparationPerPlayer(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   seasons = _training_seasons()
   history = Mock( wraps=PriorYearBuilder.history )
   monkeypatch.setattr( PriorYearBuilder, 'history', history )

   coefficients = NhlProductionRegression.fit( seasons, NhlProductionStat.SHOTS )

   assert history.call_count == len( { season.player_id for season in seasons } )
   assert coefficients
   assert all(
      0 < coefficient.to_age - coefficient.from_age <= PriorYearBuilder.WIDTH
      for coefficient in coefficients )


@pytest.mark.parametrize( 'stat', list( NhlProductionStat ) )
@pytest.mark.parametrize( 'target_year', [ 2021, 2022 ] )
def Test_Pace_TestElapsedAgeGrowth_ExpectCompoundedMultiplier(
      stat: NhlProductionStat,
      target_year: int ) -> None:
   coefficients = NhlProductionRegression.fit( _training_seasons(), stat )
   prior = _season( 100, 2020, 18.7, 25 )
   elapsed_seasons = target_year - 2020
   expected = prior.shots_pace() * ANNUAL_MULTIPLIER ** elapsed_seasons

   projected = _pace(
      coefficients, [ prior ], target_year * 10000 + target_year + 1, stat )

   assert projected == pytest.approx( expected )


@pytest.mark.parametrize( 'stat', list( NhlProductionStat ) )
def Test_Pace_TestNoHistory_ExpectNone( stat: NhlProductionStat ) -> None:
   assert _pace( [], [], 20212022, stat ) is None


def Test_Pace_TestSmallNhlStint_ExpectNone() -> None:
   season = replace( _season( 1, 2020, 18.4, 20 ), games_played=9 )

   assert _pace( [], [ season ], 20212022, NhlProductionStat.SHOTS ) is None


def Test_Pace_TestZeroShots_ExpectZeroNotMissing() -> None:
   season = _season( 1, 2020, 18.4, 0 )

   assert _pace( [], [ season ], 20212022, NhlProductionStat.SHOTS ) == 0.0


def Test_Pace_TestWeightedShotHistory_ExpectNormalizedAverageThenGrowth() -> None:
   latest = _season( 1, 2021, 19.4, 160 )
   older = replace( _season( 1, 2020, 18.4, 50 ), games_played=41 )
   coefficients = [
      ProductionCoefficient( 18, 19, 1.2, 0.8, 100 ),
      ProductionCoefficient( 19, 20, 1.1, 0.9, 100 ),
      ProductionCoefficient( 18, 20, 1.32, 0.5, 100 ),
   ]
   latest_relationship = ProductionHistoryPredictor.coefficient( coefficients, 19, 20 )
   older_relationship = ProductionHistoryPredictor.coefficient( coefficients, 18, 20 )
   older_to_latest = ProductionHistoryPredictor.coefficient( coefficients, 18, 19 )
   latest_weight = latest.games_played * latest_relationship.weight
   older_weight = older.games_played * older_relationship.weight
   expected = (
      latest.shots_pace() * latest_weight
      + older.shots_pace() * older_to_latest.multiplier * older_weight
   ) / ( latest_weight + older_weight ) * latest_relationship.multiplier

   projected = _pace(
      coefficients, [ older, latest ], 20222023, NhlProductionStat.SHOTS )

   assert projected == pytest.approx( expected )


def Test_Pace_TestCurrentAndFutureRows_ExpectExcluded() -> None:
   previous = _season( 1, 2020, 18.4, 100 )
   current = _season( 1, 2021, 19.4, 1000 )
   future = _season( 1, 2022, 20.4, 2000 )

   projected = _pace(
      [], [ previous, current, future ], 20212022, NhlProductionStat.SHOTS )

   assert projected == previous.shots_pace()
