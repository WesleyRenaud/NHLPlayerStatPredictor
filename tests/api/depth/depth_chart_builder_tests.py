from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_chart_builder import DepthChartBuilder
from api.depth.depth_group import DepthGroup
from api.depth.ice_chosen_share import IceChosenShare
from api.depth.ice_skater import IceSkater
from api.depth.last_core import LastCore
from api.depth.slot_average import SlotAverage
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


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
      GamesShare.FULL )


def _chosen( group: DepthGroup ) -> list[ IceChosenShare ]:
   return [
      IceChosenShare(
         0.0,
         group.skater_group,
         GamesShare.FULL,
         GamesShare.FULL )
   ]


def Test_Build_TestSevenRegulars_ExpectSixAndPie() -> None:
   team = list( Team )[ Position.FIRST ]
   pace_games = 4
   extra_id = 7

   chart = DepthChartBuilder.build(
      team,
      [
         _skater( 1, 26.0 ),
         _skater( 2, 24.0 ),
         _skater( 3, 20.0 ),
         _skater( 4, 19.0 ),
         _skater( 5, 16.0 ),
         _skater( 6, 15.0 ),
         _skater( extra_id, 12.0 ),
         _skater( 8, 11.0 ),
      ],
      [],
      _chosen( DepthGroup.defense() ),
      DepthGroup.defense(),
      pace_games )

   assert chart.team == team
   assert len( chart.regulars ) == NhlLineupSelector.DRESSED_DEFENSE
   assert len( chart.extras ) == LastCore.EXTRA
   assert chart.extras[ Position.FIRST ].player_id == extra_id
   total = sum( toi for _skater_row, toi in chart.regulars )
   assert abs( total - DepthGroup.DEFENSE_ICE_MINUTES ) < 0.001
   assert chart.regulars[ Position.FIRST ][ Position.LAST ] >= (
      chart.regulars[ Position.SECOND ][ Position.LAST ] )
   assert abs( sum( chart.games_out ) - pace_games ) < 0.001
   assert abs( chart.games_out[ Position.FIRST ] - pace_games ) < 0.001


def Test_Build_TestLowGamesHighToi_ExpectRegular() -> None:
   team = list( Team )[ Position.FIRST ]
   high_toi_id = 9

   chart = DepthChartBuilder.build(
      team,
      [
         _skater( 1, 26.0 ),
         _skater( 2, 24.0 ),
         _skater( high_toi_id, 30.0 ),
         _skater( 3, 20.0 ),
         _skater( 4, 19.0 ),
         _skater( 5, 16.0 ),
         _skater( 6, 15.0 ),
      ],
      [],
      _chosen( DepthGroup.defense() ),
      DepthGroup.defense(),
      Position.SECOND )

   assert chart.regulars[ Position.FIRST ][ Position.FIRST ].player_id == high_toi_id


def Test_Build_TestSixRegulars_ExpectLeagueSeventh() -> None:
   team = list( Team )[ Position.FIRST ]
   slot = SlotAverage( 7, 15.0, 2.0, 12.0 )

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
      [ slot ],
      _chosen( DepthGroup.defense() ),
      DepthGroup.defense(),
      Position.SECOND )

   extra = chart.extras[ Position.FIRST ]
   assert extra.implied == slot.toi
   assert extra.last_toi == slot.toi


def Test_Build_TestHalfAvailable_ExpectMoreThanHealthyShare() -> None:
   team = list( Team )[ Position.FIRST ]
   implied = 20.0
   availability = 0.5
   even_share = DepthGroup.DEFENSE_ICE_MINUTES / NhlLineupSelector.DRESSED_DEFENSE

   chart = DepthChartBuilder.build(
      team,
      [
         IceSkater(
            player_id,
            str( player_id ),
            SkaterPosition( 'D' ),
            team,
            implied,
            implied,
            availability )
         for player_id in range( 1, 7 )
      ],
      [ SlotAverage( 7, 15.0, 2.0, 12.0 ) ],
      _chosen( DepthGroup.defense() ),
      DepthGroup.defense(),
      Position.SECOND )

   assert chart.regulars[ Position.FIRST ][ Position.LAST ] > even_share
   assert chart.skater_group is SkaterGroup( 'D' )


def Test_Build_TestTwelveForwards_ExpectForwardPie() -> None:
   team = list( Team )[ Position.FIRST ]
   implied = 15.0

   chart = DepthChartBuilder.build(
      team,
      [ _skater( index, implied ) for index in range( 1, NhlLineupSelector.DRESSED_FORWARDS + 1 ) ],
      [ SlotAverage( 13, 10.0, 1.0, 8.0 ) ],
      _chosen( DepthGroup.forwards() ),
      DepthGroup.forwards(),
      Position.SECOND )

   assert chart.skater_group is SkaterGroup( 'F' )
   assert len( chart.regulars ) == NhlLineupSelector.DRESSED_FORWARDS
   total = sum( toi for _skater_row, toi in chart.regulars )
   assert abs( total - DepthGroup.FORWARD_ICE_MINUTES ) < 0.001
   assert abs( chart.regulars[ Position.FIRST ][ Position.LAST ] - implied ) < 0.001


def Test_Build_TestForwardHalfAvailable_ExpectMoreThanHealthyShare() -> None:
   team = list( Team )[ Position.FIRST ]
   implied = 15.0
   availability = 0.5

   chart = DepthChartBuilder.build(
      team,
      [
         IceSkater(
            player_id,
            str( player_id ),
            SkaterPosition( 'C' ),
            team,
            implied,
            implied,
            availability )
         for player_id in range( 1, NhlLineupSelector.DRESSED_FORWARDS + 1 )
      ],
      [ SlotAverage( 13, 10.0, 1.0, 8.0 ) ],
      _chosen( DepthGroup.forwards() ),
      DepthGroup.forwards(),
      Position.SECOND )

   assert chart.regulars[ Position.FIRST ][ Position.LAST ] > implied


def Test_Build_TestBottomChosen_ExpectRegularScaledAndExtraFull() -> None:
   group = DepthGroup.defense()
   chosen = 0.5
   bottom_toi = 15.0
   shares = [
      IceChosenShare( bottom_toi, group.skater_group, chosen, chosen ),
      IceChosenShare( 16.0, group.skater_group, GamesShare.FULL, GamesShare.FULL ),
   ]

   chart = DepthChartBuilder.build(
      list( Team )[ Position.FIRST ],
      [
         _skater( 1, 26.0 ),
         _skater( 2, 24.0 ),
         _skater( 3, 20.0 ),
         _skater( 4, 19.0 ),
         _skater( 5, 16.0 ),
         _skater( 6, bottom_toi ),
         _skater( 7, 12.0 ),
      ],
      [],
      shares,
      group,
      Position.SECOND )

   by_id = {
      skater.player_id: skater.availability
      for skater, _toi in chart.regulars
   }
   assert by_id[ 1 ] == GamesShare.FULL
   assert by_id[ 6 ] == chosen
   assert chart.extras[ Position.FIRST ].availability == GamesShare.FULL


def Test_Build_TestBottomChosen_ExpectTopGetsMore() -> None:
   group = DepthGroup.defense()
   chosen = 0.5
   skaters = [
      _skater( 1, 26.0 ),
      _skater( 2, 24.0 ),
      _skater( 3, 20.0 ),
      _skater( 4, 19.0 ),
      _skater( 5, 16.0 ),
      _skater( 6, 15.0 ),
      _skater( 7, 12.0 ),
   ]
   team = list( Team )[ Position.FIRST ]
   shares = [
      IceChosenShare( 15.0, group.skater_group, chosen, chosen ),
      IceChosenShare( 16.0, group.skater_group, GamesShare.FULL, GamesShare.FULL ),
   ]

   full = DepthChartBuilder.build(
      team,
      skaters,
      [],
      _chosen( group ),
      group,
      Position.SECOND )
   scratched = DepthChartBuilder.build(
      team,
      skaters,
      [],
      shares,
      group,
      Position.SECOND )

   assert scratched.regulars[ Position.FIRST ][ Position.LAST ] > (
      full.regulars[ Position.FIRST ][ Position.LAST ] )
