from __future__ import annotations

from datetime import date

from api.projections.career_pace_averager import CareerPaceAverager
from api.recency_weight import RecencyWeight
from api.season import Season
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.team import Team


def _season( g_pace: float, a_pace: float, season_id: int ) -> SkaterSeason:
   return SkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=82,
      goals=int( g_pace ),
      assists=int( a_pace ),
      points=int( g_pace + a_pace ),
      schedule_games=82,
      pace_games=82,
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0 )


def Test_Average_TestWeightedSeasons_ExpectWeightedGoalsAssistsAndSummedPoints() -> None:
   later = _season( 10.0, 20.0, 20222023 )
   earlier = _season( 40.0, 50.0, 20212022 )
   target_season_id = 20232024
   weights = [ RecencyWeight( 0, 0.75 ), RecencyWeight( 1, 0.25 ) ]
   by_lag = { weight.lag: weight.weight for weight in weights }
   later_weight = by_lag[ Season.recency_lag( target_season_id, later.season_id ) ]
   earlier_weight = by_lag[ Season.recency_lag( target_season_id, earlier.season_id ) ]
   total = later_weight + earlier_weight
   pace = CareerPaceAverager.average( [ later, earlier ], weights, target_season_id )
   assert pace.goals == (
      later.g_pace * later_weight + earlier.g_pace * earlier_weight ) / total
   assert pace.assists == (
      later.a_pace * later_weight + earlier.a_pace * earlier_weight ) / total


def Test_Average_TestMissingLag_ExpectRenormalizedOverPresentWeights() -> None:
   kept = _season( 10.0, 20.0, 20222023 )
   dropped = _season( 90.0, 90.0, 20202021 )
   target_season_id = 20232024
   weights = [ RecencyWeight( 0, 0.75 ), RecencyWeight( 1, 0.25 ) ]
   pace = CareerPaceAverager.average( [ kept, dropped ], weights, target_season_id )
   assert pace.goals == kept.g_pace
   assert pace.assists == kept.a_pace
