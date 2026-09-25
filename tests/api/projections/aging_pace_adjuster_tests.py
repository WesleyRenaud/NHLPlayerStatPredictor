from __future__ import annotations

from datetime import date

from api.aging.aging_factor import AgingFactor
from api.projections.aging_pace_adjuster import AgingPaceAdjuster
from api.projections.season_pace import SeasonPace
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _season(
      season_id: int,
      g_pace: float,
      a_pace: float ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
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
   pace = SeasonPace( 31.4, 42.1 )
   factor = AgingFactor( 28, -0.07, -0.044 )

   aged = AgingPaceAdjuster.adjust( pace, factor.age, [ factor ], [] )

   assert aged == SeasonPace(
      pace.goals * ( 1.0 + factor.goals ),
      pace.assists * ( 1.0 + factor.assists ) )


def Test_Adjust_TestMissingAge_ExpectNearestFactor() -> None:
   younger = AgingFactor( 24, 0.01, 0.02 )
   older = AgingFactor( 28, -0.07, -0.044 )
   pace = SeasonPace( 20.0, 30.0 )
   age = 39

   aged = AgingPaceAdjuster.adjust( pace, age, [ younger, older ], [] )

   assert aged == SeasonPace(
      pace.goals * ( 1.0 + older.goals ),
      pace.assists * ( 1.0 + older.assists ) )


def Test_Adjust_TestRecentPairs_ExpectShrunkBlend() -> None:
   league = AgingFactor( 28, -0.16, -0.15 )
   pace = SeasonPace( 40.0, 50.0 )
   first = _season( 20222023, 40.0, 50.0 )
   second = _season( 20232024, 40.0, 50.0 )
   third = _season( 20242025, 40.0, 50.0 )
   seasons = [ first, second, third ]
   pair_count = 2
   player_goals = (
      ( second.g_pace - first.g_pace ) + ( third.g_pace - second.g_pace )
   ) / ( first.g_pace + second.g_pace )
   player_assists = (
      ( second.a_pace - first.a_pace ) + ( third.a_pace - second.a_pace )
   ) / ( first.a_pace + second.a_pace )
   weight = pair_count / ( pair_count + AgingPaceAdjuster.SHRINK )

   aged = AgingPaceAdjuster.adjust( pace, league.age, [ league ], seasons )

   assert aged == SeasonPace(
      pace.goals * (
         1.0 + weight * player_goals + ( 1.0 - weight ) * league.goals ),
      pace.assists * (
         1.0 + weight * player_assists + ( 1.0 - weight ) * league.assists ) )
