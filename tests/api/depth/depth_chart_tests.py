from __future__ import annotations

from api.depth.depth_chart import DepthChart
from api.depth.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _skater( player_id: int ) -> IceSkater:
   return IceSkater(
      player_id,
      'A',
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      20.0,
      20.0,
      1.0 )


def Test_ToDict_TestChart_ExpectTeamAndRegulars() -> None:
   team = list( Team )[ Position.FIRST ]
   regulars = [ ( _skater( 1 ), 25.0 ), ( _skater( 2 ), 23.0 ) ]
   extras = [ _skater( 3 ) ]
   games_out = [ 42.0, 42.0 ]
   chart = DepthChart(
      team,
      regulars,
      extras,
      games_out,
      SkaterGroup( 'D' ) )

   payload = chart.to_dict()

   assert payload[ 'team' ] == team.value
   assert len( payload[ 'regulars' ] ) == len( regulars )
   assert len( payload[ 'extras' ] ) == len( extras )
   assert payload[ 'games_out' ] == games_out
