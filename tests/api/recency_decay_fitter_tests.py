from __future__ import annotations

from datetime import date

from api.recency_decay_fitter import RecencyDecayFitter
from api.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.team import Team


def _season(
      player_id: int,
      season_id: int,
      g_pace: float,
      a_pace: float ) -> SkaterSeason:
   return SkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
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


def Test_Weights_TestDecay_ExpectNormalizedGeometric() -> None:
   decay = 0.5
   raw = [
      decay ** lag
      for lag in range( RecencyDecayFitter.WINDOW )
   ]
   total = sum( raw )
   assert RecencyDecayFitter.weights( decay ) == [
      RecencyWeight( lag=lag, weight=raw[ lag ] / total )
      for lag in range( RecencyDecayFitter.WINDOW )
   ]


def Test_Fit_TestLastYearMatches_ExpectZeroDecay() -> None:
   seasons = [
      _season( 1, 20202021, 10.0, 10.0 ),
      _season( 1, 20212022, 80.0, 80.0 ),
      _season( 1, 20222023, 80.0, 80.0 ),
   ]
   assert RecencyDecayFitter.fit( seasons ) == 0.0


def Test_Fit_TestMeanOfWindow_ExpectFullDecay() -> None:
   seasons = [
      _season( 1, 20182019, 70.0, 70.0 ),
      _season( 1, 20192020, 70.0, 70.0 ),
      _season( 1, 20202021, 70.0, 70.0 ),
      _season( 1, 20212022, 10.0, 10.0 ),
      _season( 1, 20222023, 55.0, 55.0 ),
   ]
   assert RecencyDecayFitter.fit( seasons ) == 1.0
