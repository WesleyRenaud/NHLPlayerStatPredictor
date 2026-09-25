from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_group import DepthGroup
from api.depth.ice_usage import IceUsage
from api.depth.last_core import LastCore
from api.depth.usable_nhl_ice import UsableNhlIce
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _usage( toi: float, games: int ) -> IceUsage:
   return IceUsage(
      toi,
      games,
      list( Team )[ Position.FIRST ],
      SkaterPosition( 'D' ) )


def Test_Shares_TestRankedByToi_ExpectDressedGamesShare() -> None:
   team = list( Team )[ Position.FIRST ]
   season_length = 82
   dressed_count = NhlLineupSelector.DRESSED_DEFENSE
   high_toi = 26.0
   high_games = 82
   mid_toi = 24.0
   mid_games = 41
   low_toi = 20.0
   low_games = 82

   shares = LastCore.shares(
      team,
      {
         1: _usage( mid_toi, mid_games ),
         2: _usage( low_toi, low_games ),
         3: _usage( high_toi, high_games ),
      },
      season_length,
      dressed_count,
      DepthGroup.defense().positions )

   assert shares[ Position.FIRST ] == high_games / season_length
   assert shares[ Position.SECOND ] == mid_games / season_length
   assert shares[ Position.THIRD ] == low_games / season_length
   assert len( shares ) == dressed_count
   assert shares[ Position.LAST ] == GamesShare.FULL


def Test_Shares_TestLowGames_ExpectRankedByToi() -> None:
   team = list( Team )[ Position.FIRST ]
   season_length = 82
   high_toi = 30.0
   high_games = 6
   low_toi = 16.0
   low_games = 82

   shares = LastCore.shares(
      team,
      {
         1: _usage( high_toi, high_games ),
         2: _usage( low_toi, low_games ),
      },
      season_length,
      NhlLineupSelector.DRESSED_DEFENSE,
      DepthGroup.defense().positions )

   assert shares[ Position.FIRST ] == high_games / season_length
   assert shares[ Position.SECOND ] == low_games / season_length


def Test_Teammates_TestTopSix_ExpectPacesAndShares() -> None:
   team = list( Team )[ Position.FIRST ]
   season_length = 82
   toi_base = 30.0
   pace_base = 40.0
   extra_id = 7
   ice_usages = {
      player_id: _usage( toi_base - player_id, season_length - player_id )
      for player_id in range( 1, extra_id + 1 )
   }
   paces = { player_id: pace_base - player_id for player_id in range( 1, extra_id + 1 ) }

   regulars, extras = LastCore.teammates(
      team,
      ice_usages,
      paces,
      season_length,
      NhlLineupSelector.DRESSED_DEFENSE,
      LastCore.EXTRA,
      DepthGroup.defense().positions )

   assert [ skater.player_id for skater in regulars ] == list( range( 1, 7 ) )
   assert regulars[ Position.FIRST ].availability == (
      season_length - 1 ) / season_length
   assert extras[ Position.FIRST ].player_id == extra_id
   assert extras[ Position.FIRST ].availability == GamesShare.FULL
   assert extras[ Position.FIRST ].contribution == paces[ extra_id ]


def Test_Teammates_TestShortExtra_ExpectNextUsable() -> None:
   team = list( Team )[ Position.FIRST ]
   season_length = 82
   extra_id = 8
   ice_usages = {
      player_id: _usage( 30.0 - player_id, season_length )
      for player_id in range( 1, 7 )
   }
   ice_usages[ 7 ] = _usage( 15.0, UsableNhlIce.MIN_GAMES - 1 )
   ice_usages[ extra_id ] = _usage( 14.0, 80 )
   paces = { player_id: float( player_id ) for player_id in range( 1, extra_id + 1 ) }

   regulars, extras = LastCore.teammates(
      team,
      ice_usages,
      paces,
      season_length,
      NhlLineupSelector.DRESSED_DEFENSE,
      LastCore.EXTRA,
      DepthGroup.defense().positions )

   assert [ skater.player_id for skater in regulars ] == list( range( 1, 7 ) )
   assert extras[ Position.FIRST ].player_id == extra_id
   assert extras[ Position.FIRST ].availability == GamesShare.FULL
   assert extras[ Position.FIRST ].contribution == paces[ extra_id ]


def Test_Teammates_TestOnlyShortExtra_ExpectEmpty() -> None:
   team = list( Team )[ Position.FIRST ]
   season_length = 82
   ice_usages = {
      player_id: _usage( 30.0 - player_id, season_length )
      for player_id in range( 1, 7 )
   }
   ice_usages[ 7 ] = _usage( 15.0, UsableNhlIce.MIN_GAMES - 1 )

   regulars, extras = LastCore.teammates(
      team,
      ice_usages,
      { player_id: float( player_id ) for player_id in range( 1, 8 ) },
      season_length,
      NhlLineupSelector.DRESSED_DEFENSE,
      LastCore.EXTRA,
      DepthGroup.defense().positions )

   assert [ skater.player_id for skater in regulars ] == list( range( 1, 7 ) )
   assert extras == []


def Test_Shares_TestForwardOnTeam_ExpectDefenseOnly() -> None:
   team = list( Team )[ Position.FIRST ]
   season_length = 82
   defense_toi = 24.0
   defense_games = 82

   shares = LastCore.shares(
      team,
      {
         1: _usage( defense_toi, defense_games ),
         2: IceUsage(
            30.0,
            season_length,
            team,
            SkaterPosition( 'C' ) ),
      },
      season_length,
      NhlLineupSelector.DRESSED_DEFENSE,
      DepthGroup.defense().positions )

   assert shares[ Position.FIRST ] == defense_games / season_length
   assert shares[ Position.SECOND ] == GamesShare.FULL
