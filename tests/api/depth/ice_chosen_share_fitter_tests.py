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
   season_length = 82
   high_toi = 24.0
   high_games = 82
   low_toi = 18.0
   low_games = 41

   shares = IceChosenShareFitter.fit(
      dict( [
         _usage( 1, high_toi, high_games, team, position ),
         _usage( 2, low_toi, low_games, team, position ),
      ] ),
      season_length,
      DepthGroup.defense() )

   assert [ share.toi for share in shares ] == [ low_toi, high_toi ]
   assert shares[ Position.FIRST ].skater_group is SkaterGroup( 'D' )
   assert abs(
      shares[ Position.FIRST ].dress_share - low_games / season_length ) < 0.001
   assert abs(
      shares[ Position.FIRST ].chosen - low_games / high_games ) < 0.001
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
   season_length = 82
   toi = 18.0
   games = 80

   shares = IceChosenShareFitter.fit(
      dict( [
         _usage( 1, 21.0, UsableNhlIce.MIN_GAMES - 1, team, position ),
         _usage( 2, toi, games, team, position ),
      ] ),
      season_length,
      DepthGroup.defense() )

   assert [ share.toi for share in shares ] == [ toi ]
   assert abs(
      shares[ Position.FIRST ].dress_share - games / season_length ) < 0.001
   assert shares[ Position.FIRST ].chosen == GamesShare.FULL


def Test_Fit_TestNearbyToi_ExpectSameBin() -> None:
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'D' )
   season_length = 82
   first_toi = 17.6
   first_games = 82
   second_toi = 17.8
   second_games = 40

   shares = IceChosenShareFitter.fit(
      dict( [
         _usage( 1, first_toi, first_games, team, position ),
         _usage( 2, second_toi, second_games, team, position ),
      ] ),
      season_length,
      DepthGroup.defense() )

   dress_share = (
      first_games / season_length + second_games / season_length
   ) / 2
   assert [ share.toi for share in shares ] == [ float( round( first_toi ) ) ]
   assert abs( shares[ Position.FIRST ].dress_share - dress_share ) < 0.001


def Test_Fit_TestEmpty_ExpectEmpty() -> None:
   shares = IceChosenShareFitter.fit( {}, 82, DepthGroup.forwards() )

   assert shares == []
