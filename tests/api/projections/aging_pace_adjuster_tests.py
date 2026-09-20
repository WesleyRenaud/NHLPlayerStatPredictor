from __future__ import annotations

from datetime import date

from api.aging_factor import AgingFactor
from api.nhl_skater_season import NhlSkaterSeason
from api.projections.aging_pace_adjuster import AgingPaceAdjuster
from api.projections.career_pace import CareerPace
from api.projections.player_aging_fitter import PlayerAgingFitter
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _season(
      season_id: int,
      g_pace: float,
      a_pace: float ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.0,
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


def Test_Adjust_TestMatchingAge_ExpectLeagueScaleWithoutPairs() -> None:
   pace = CareerPace( 31.4, 42.1 )
   factor = AgingFactor( 28, -0.07, -0.044 )
   aged = AgingPaceAdjuster.adjust( pace, factor.age, [ factor ], [] )
   assert aged == CareerPace(
      pace.goals * ( 1.0 + factor.goals ),
      pace.assists * ( 1.0 + factor.assists ) )


def Test_Adjust_TestMissingAge_ExpectNearestFactor() -> None:
   younger = AgingFactor( 24, 0.01, 0.02 )
   older = AgingFactor( 28, -0.07, -0.044 )
   pace = CareerPace( 20.0, 30.0 )
   aged = AgingPaceAdjuster.adjust( pace, 39, [ younger, older ], [] )
   assert aged == AgingPaceAdjuster.adjust( pace, older.age, [ younger, older ], [] )


def Test_Adjust_TestRecentPairs_ExpectShrunkBlend() -> None:
   league = AgingFactor( 28, -0.16, -0.15 )
   pace = CareerPace( 40.0, 50.0 )
   seasons = [
      _season( 20222023, 40.0, 50.0 ),
      _season( 20232024, 40.0, 50.0 ),
      _season( 20242025, 40.0, 50.0 ),
   ]
   player_rate = PlayerAgingFitter.fit( seasons )
   assert player_rate is not None
   weight = player_rate.pair_count / ( player_rate.pair_count + AgingPaceAdjuster.SHRINK )
   aged = AgingPaceAdjuster.adjust( pace, league.age, [ league ], seasons )
   assert aged == CareerPace(
      pace.goals * (
         1.0 + weight * player_rate.goals + ( 1.0 - weight ) * league.goals ),
      pace.assists * (
         1.0 + weight * player_rate.assists + ( 1.0 - weight ) * league.assists ) )
