from __future__ import annotations

from datetime import date

from api.recency.recency_decay_fitter import RecencyDecayFitter
from api.recency.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _season(
      player_id: int,
      season_id: int,
      g_pace: float,
      a_pace: float ) -> NhlSkaterSeason:
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
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0 )


def _run( player_id: int, values: list[ float ] ) -> list[ NhlSkaterSeason ]:
   start = 2018
   return [
      _season(
         player_id,
         ( start + offset ) * 10000 + ( start + offset + 1 ),
         value,
         value )
      for offset, value in enumerate( values )
   ]


def Test_Fit_TestLastYearMatches_ExpectFirstWeightOne() -> None:
   seasons: list[ NhlSkaterSeason ] = []

   for lag in range( RecencyDecayFitter.WINDOW ):
      values = [ 0.0 ] * ( RecencyDecayFitter.WINDOW + 1 )
      current = 10.0 * ( lag + 1 )
      values[ RecencyDecayFitter.WINDOW ] = current
      values[ RecencyDecayFitter.WINDOW - 1 ] = current

      if lag:
         values[ RecencyDecayFitter.WINDOW - 1 - lag ] = 5.0

      seasons.extend( _run( lag + 1, values ) )

   assert RecencyDecayFitter.fit( seasons ) == [
      RecencyWeight( lag, 1.0 if lag == Position.FIRST else 0.0 )
      for lag in range( RecencyDecayFitter.WINDOW )
   ]


def Test_Fit_TestMeanOfWindow_ExpectEqualWeights() -> None:
   seasons: list[ NhlSkaterSeason ] = []

   for lag in range( RecencyDecayFitter.WINDOW ):
      values = [ 0.0 ] * ( RecencyDecayFitter.WINDOW + 1 )
      values[ RecencyDecayFitter.WINDOW ] = 1.0
      values[ RecencyDecayFitter.WINDOW - 1 - lag ] = float(
         RecencyDecayFitter.WINDOW )
      seasons.extend( _run( lag + 1, values ) )

   weight = 1.0 / RecencyDecayFitter.WINDOW
   assert RecencyDecayFitter.fit( seasons ) == [
      RecencyWeight( lag, weight )
      for lag in range( RecencyDecayFitter.WINDOW )
   ]
