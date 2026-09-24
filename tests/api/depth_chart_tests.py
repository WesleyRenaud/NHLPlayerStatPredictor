from __future__ import annotations

from api.depth_chart import DepthChart
from api.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skater_group import SkaterGroup
from api.skater_position import SkaterPosition
from api.team import Team


def _skater( player_id: int ) -> IceSkater:
   return IceSkater(
      player_id,
      'A',
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      20.0,
      20.0,
      80,
      False,
      1.0 )


def Test_ToDict_TestChart_ExpectTeamAndRegulars() -> None:
   team = list( Team )[ Position.FIRST ]
   chart = DepthChart(
      team,
      [ ( _skater( 1 ), 25.0 ), ( _skater( 2 ), 23.0 ) ],
      [ _skater( 3 ) ],
      [ 42.0, 42.0 ],
      SkaterGroup( 'D' ) )
   payload = chart.to_dict()
   assert payload[ 'team' ] == team.value
   assert len( payload[ 'regulars' ] ) == 2
   assert len( payload[ 'extras' ] ) == 1
   assert payload[ 'games_out' ] == [ 42.0, 42.0 ]
