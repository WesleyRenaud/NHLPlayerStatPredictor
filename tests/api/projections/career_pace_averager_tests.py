from __future__ import annotations

from datetime import date

from api.projections.career_pace_averager import CareerPaceAverager
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.team import Team


def _season( g_pace: float, a_pace: float, season_id: int = 20202021 ) -> SkaterSeason:
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
      pace_games=84,
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0 )


def Test_Average_TestSeasons_ExpectMeanGoalsAssistsAndSummedPoints() -> None:
   first = _season( 40.0, 50.0, 20202021 )
   second = _season( 60.0, 70.0, 20212022 )
   projection = CareerPaceAverager.average( [ first, second ] )
   goals = round( ( first.g_pace + second.g_pace ) / 2 )
   assists = round( ( first.a_pace + second.a_pace ) / 2 )
   assert projection.goals == goals
   assert projection.assists == assists
   assert projection.points == goals + assists
