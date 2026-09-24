from __future__ import annotations

from api.depth_chart_builder import DepthChartBuilder
from api.depth_group import DepthGroup
from api.ice_skater import IceSkater
from api.ice_usage import IceUsage
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.shared.enums.position import Position
from api.skater_group import SkaterGroup
from api.skater_position import SkaterPosition
from api.slot_average import SlotAverage
from api.slot_filler import SlotFiller
from api.team import Team


def _skater(
      player_id: int,
      implied: float ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      implied,
      implied,
      1.0 )


def Test_Build_TestSevenRegulars_ExpectSixAndPie() -> None:
   team = list( Team )[ Position.FIRST ]
   pace_games = 4
   chart = DepthChartBuilder.build(
      team,
      [
         _skater( 1, 26.0 ),
         _skater( 2, 24.0 ),
         _skater( 3, 20.0 ),
         _skater( 4, 19.0 ),
         _skater( 5, 16.0 ),
         _skater( 6, 15.0 ),
         _skater( 7, 12.0 ),
         _skater( 8, 11.0 ),
      ],
      [],
      {},
      82,
      DepthGroup.defense(),
      pace_games )
   assert chart.team == team
   assert len( chart.regulars ) == NhlLineupSelector.DRESSED_DEFENSE
   assert len( chart.extras ) == 1
   assert chart.extras[ Position.FIRST ].player_id == 7
   total = sum( toi for _skater_row, toi in chart.regulars )
   assert abs( total - DepthGroup.DEFENSE_ICE_MINUTES ) < 0.001
   assert chart.regulars[ Position.FIRST ][ Position.LAST ] >= (
      chart.regulars[ Position.SECOND ][ Position.LAST ] )
   assert abs( sum( chart.games_out ) - pace_games ) < 0.001
   assert abs( chart.games_out[ Position.FIRST ] - pace_games ) < 0.001


def Test_Build_TestLowGamesHighToi_ExpectRegular() -> None:
   team = list( Team )[ Position.FIRST ]
   chart = DepthChartBuilder.build(
      team,
      [
         _skater( 1, 26.0 ),
         _skater( 2, 24.0 ),
         _skater( 9, 30.0 ),
         _skater( 3, 20.0 ),
         _skater( 4, 19.0 ),
         _skater( 5, 16.0 ),
         _skater( 6, 15.0 ),
      ],
      [],
      {},
      82,
      DepthGroup.defense(),
      Position.SECOND )
   assert chart.regulars[ Position.FIRST ][ Position.FIRST ].player_id == 9


def Test_Build_TestSixRegulars_ExpectLeagueSeventh() -> None:
   team = list( Team )[ Position.FIRST ]
   slot_averages = [ SlotAverage( 7, 15.0, 2.0, 12.0 ) ]
   chart = DepthChartBuilder.build(
      team,
      [
         _skater( 1, 26.0 ),
         _skater( 2, 24.0 ),
         _skater( 3, 20.0 ),
         _skater( 4, 19.0 ),
         _skater( 5, 16.0 ),
         _skater( 6, 15.0 ),
      ],
      slot_averages,
      {},
      82,
      DepthGroup.defense(),
      Position.SECOND )
   extra = chart.extras[ Position.FIRST ]
   assert extra.implied == SlotFiller.implied( slot_averages, 7 )
   assert extra.last_toi == 15.0


def Test_Build_TestPriorEqualsCurrent_ExpectHealthyPie() -> None:
   team = list( Team )[ Position.FIRST ]
   ice_usages = {
      player_id: IceUsage( 20.0, 41, team, SkaterPosition( 'D' ) )
      for player_id in range( 1, 7 )
   }
   chart = DepthChartBuilder.build(
      team,
      [
         IceSkater(
            player_id,
            str( player_id ),
            SkaterPosition( 'D' ),
            team,
            20.0,
            20.0,
            0.5 )
         for player_id in range( 1, 7 )
      ],
      [ SlotAverage( 7, 15.0, 2.0, 12.0 ) ],
      ice_usages,
      82,
      DepthGroup.defense(),
      Position.SECOND )
   total = sum( toi for _skater_row, toi in chart.regulars )
   assert abs( total - DepthGroup.DEFENSE_ICE_MINUTES ) < 0.001
   assert chart.skater_group is SkaterGroup.DEFENSE


def Test_Build_TestTwelveForwards_ExpectForwardPie() -> None:
   team = list( Team )[ Position.FIRST ]
   chart = DepthChartBuilder.build(
      team,
      [ _skater( index, 15.0 ) for index in range( 1, NhlLineupSelector.DRESSED_FORWARDS + 1 ) ],
      [ SlotAverage( 13, 10.0, 1.0, 8.0 ) ],
      {},
      82,
      DepthGroup.forwards(),
      Position.SECOND )
   assert chart.skater_group is SkaterGroup.FORWARD
   assert len( chart.regulars ) == NhlLineupSelector.DRESSED_FORWARDS
   total = sum( toi for _skater_row, toi in chart.regulars )
   assert abs( total - DepthGroup.FORWARD_ICE_MINUTES ) < 0.001
   assert abs( chart.regulars[ Position.FIRST ][ Position.LAST ] - 15.0 ) < 0.001


def Test_Build_TestForwardPriorEqualsCurrent_ExpectHealthyPie() -> None:
   team = list( Team )[ Position.FIRST ]
   ice_usages = {
      player_id: IceUsage( 15.0, 41, team, SkaterPosition( 'C' ) )
      for player_id in range( 1, NhlLineupSelector.DRESSED_FORWARDS + 1 )
   }
   chart = DepthChartBuilder.build(
      team,
      [
         IceSkater(
            player_id,
            str( player_id ),
            SkaterPosition( 'C' ),
            team,
            15.0,
            15.0,
            0.5 )
         for player_id in range( 1, NhlLineupSelector.DRESSED_FORWARDS + 1 )
      ],
      [ SlotAverage( 13, 10.0, 1.0, 8.0 ) ],
      ice_usages,
      82,
      DepthGroup.forwards(),
      Position.SECOND )
   assert abs( chart.regulars[ Position.FIRST ][ Position.LAST ] - 15.0 ) < 0.001
