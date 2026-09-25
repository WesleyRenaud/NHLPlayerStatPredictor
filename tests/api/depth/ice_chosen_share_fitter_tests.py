from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_group import DepthGroup
from api.depth.ice_chosen_share_fitter import IceChosenShareFitter
from api.depth.ice_usage import IceUsage
from api.depth.usable_nhl_ice import UsableNhlIce
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _usage(
      player_id: int,
      toi: float,
      games: int,
      team: Team,
      position: SkaterPosition ) -> tuple[ int, IceUsage ]:
   return player_id, IceUsage( toi, games, team, position )


def Test_Fit_TestTwoToi_ExpectDressMeansAndChosen() -> None:
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'D' )
   shares = IceChosenShareFitter.fit(
      dict( [
         _usage( 1, 24.0, 82, team, position ),
         _usage( 2, 18.0, 41, team, position ),
      ] ),
      82,
      DepthGroup.defense() )
   assert [ share.toi for share in shares ] == [ 18.0, 24.0 ]
   assert shares[ Position.FIRST ].skater_group is SkaterGroup( 'D' )
   assert abs( shares[ Position.FIRST ].dress_share - 41.0 / 82.0 ) < 0.001
   assert abs( shares[ Position.FIRST ].chosen - 0.5 ) < 0.001
   assert shares[ Position.LAST ].dress_share == GamesShare.FULL
   assert shares[ Position.LAST ].chosen == GamesShare.FULL


def Test_Fit_TestHigherToiFewerGames_ExpectChosenCapped() -> None:
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'D' )
   shares = IceChosenShareFitter.fit(
      dict( [
         _usage( 1, 24.0, 70, team, position ),
         _usage( 2, 18.0, 80, team, position ),
      ] ),
      82,
      DepthGroup.defense() )
   assert shares[ Position.FIRST ].chosen == GamesShare.FULL
   assert shares[ Position.LAST ].chosen == GamesShare.FULL


def Test_Fit_TestShortSample_ExpectOmitted() -> None:
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'D' )
   shares = IceChosenShareFitter.fit(
      dict( [
         _usage( 1, 21.0, UsableNhlIce.MIN_GAMES - 1, team, position ),
         _usage( 2, 18.0, 80, team, position ),
      ] ),
      82,
      DepthGroup.defense() )
   assert [ share.toi for share in shares ] == [ 18.0 ]
   assert abs( shares[ Position.FIRST ].dress_share - 80.0 / 82.0 ) < 0.001
   assert shares[ Position.FIRST ].chosen == GamesShare.FULL


def Test_Fit_TestNearbyToi_ExpectSameBin() -> None:
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'D' )
   shares = IceChosenShareFitter.fit(
      dict( [
         _usage( 1, 17.6, 82, team, position ),
         _usage( 2, 17.8, 40, team, position ),
      ] ),
      82,
      DepthGroup.defense() )
   assert [ share.toi for share in shares ] == [ 18.0 ]
   assert abs( shares[ Position.FIRST ].dress_share - 61.0 / 82.0 ) < 0.001


def Test_Fit_TestEmpty_ExpectEmpty() -> None:
   assert IceChosenShareFitter.fit( {}, 82, DepthGroup.forwards() ) == []
