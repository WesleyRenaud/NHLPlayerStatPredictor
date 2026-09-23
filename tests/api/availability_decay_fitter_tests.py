from __future__ import annotations

from datetime import date

from api.availability_decay_fitter import AvailabilityDecayFitter
from api.nhl_skater_season import NhlSkaterSeason
from api.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _season(
      player_id: int,
      season_id: int,
      gp_share: float | None ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=gp_share )


def _run( player_id: int, values: list[ float | None ] ) -> list[ NhlSkaterSeason ]:
   start = 2018
   return [
      _season(
         player_id,
         ( start + offset ) * 10000 + ( start + offset + 1 ),
         value )
      for offset, value in enumerate( values )
   ]


def _last_year_seasons() -> list[ NhlSkaterSeason ]:
   seasons: list[ NhlSkaterSeason ] = []

   for lag in range( AvailabilityDecayFitter.WINDOW ):
      values: list[ float | None ] = [ 0.0 ] * ( AvailabilityDecayFitter.WINDOW + 1 )
      current = 0.10 * ( lag + 1 )
      values[ AvailabilityDecayFitter.WINDOW ] = current
      values[ AvailabilityDecayFitter.WINDOW - 1 ] = current

      if lag:
         values[ AvailabilityDecayFitter.WINDOW - 1 - lag ] = 0.05

      seasons.extend( _run( lag + 1, values ) )

   return seasons


def _first_weight_one() -> list[ RecencyWeight ]:
   return [
      RecencyWeight( lag, 1.0 if lag == Position.FIRST else 0.0 )
      for lag in range( AvailabilityDecayFitter.WINDOW )
   ]


def Test_Fit_TestLastYearMatches_ExpectFirstWeightOne() -> None:
   assert AvailabilityDecayFitter.fit( _last_year_seasons() ) == _first_weight_one()


def Test_Fit_TestMeanOfWindow_ExpectEqualWeights() -> None:
   seasons: list[ NhlSkaterSeason ] = []

   for lag in range( AvailabilityDecayFitter.WINDOW ):
      values: list[ float | None ] = [ 0.0 ] * ( AvailabilityDecayFitter.WINDOW + 1 )
      values[ AvailabilityDecayFitter.WINDOW ] = 1.0
      values[ AvailabilityDecayFitter.WINDOW - 1 - lag ] = float(
         AvailabilityDecayFitter.WINDOW )
      seasons.extend( _run( lag + 1, values ) )

   weights = AvailabilityDecayFitter.fit( seasons )
   first = weights[ Position.FIRST ].weight
   assert weights == [
      RecencyWeight( lag, first )
      for lag in range( AvailabilityDecayFitter.WINDOW )
   ]


def Test_Fit_TestMissingShare_ExpectSkipped() -> None:
   seasons = _last_year_seasons()
   seasons.extend(
      _run( 99, [ None, *[ 0.9 ] * AvailabilityDecayFitter.WINDOW ] ) )
   assert AvailabilityDecayFitter.fit( seasons ) == _first_weight_one()


def Test_Fit_TestFewPriors_ExpectSkipped() -> None:
   seasons = _last_year_seasons()
   seasons.extend( _run( 99, [ 0.9, 0.9, 0.9, 0.9, 0.1 ] ) )
   assert AvailabilityDecayFitter.fit( seasons ) == _first_weight_one()
