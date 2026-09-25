from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_chart import DepthChart
from api.depth.depth_group import DepthGroup
from api.depth.ice_skater import IceSkater
from api.depth.ice_usage import IceUsage
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team
from api.team_factor.team_factor_prior_binder import TeamFactorPriorBinder
from api.team_factor.teammate_skater import TeammateSkater


def _skater( player_id: int, implied: float ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      implied,
      implied,
      1.0 )


def Test_Bind_TestChartRank_ExpectLastYearSlotShares() -> None:
   team = list( Team )[ Position.FIRST ]
   group = DepthGroup.defense()
   bound = TeamFactorPriorBinder.bind(
      [ TeammateSkater( 1, 40.0, GamesShare.FULL, None ), TeammateSkater( 2, 30.0, GamesShare.FULL, None ) ],
      DepthChart(
         team,
         [ ( _skater( 1, 26.0 ), 26.0 ), ( _skater( 2, 20.0 ), 20.0 ) ],
         [],
         [],
         SkaterGroup( 'D' ) ),
      {
         1: IceUsage( 24.0, 41, team, SkaterPosition( 'D' ) ),
         2: IceUsage( 20.0, 82, team, SkaterPosition( 'D' ) ),
         3: IceUsage( 26.0, 82, team, SkaterPosition( 'D' ) ),
      },
      82,
      group )
   assert bound[ Position.FIRST ].prior_availability == GamesShare.FULL
   assert bound[ Position.SECOND ].prior_availability == 41 / 82
   assert bound[ Position.FIRST ].contribution == 40.0
