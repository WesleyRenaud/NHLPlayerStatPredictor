from __future__ import annotations

from api.games_share import GamesShare
from api.ice_usage import IceUsage
from api.last_core import LastCore
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _usage( toi: float, games: int ) -> IceUsage:
   return IceUsage(
      toi,
      games,
      list( Team )[ Position.FIRST ],
      SkaterPosition( 'D' ) )


def Test_Shares_TestRankedByToi_ExpectDressedGamesShare() -> None:
   team = list( Team )[ Position.FIRST ]
   shares = LastCore.shares(
      team,
      {
         1: _usage( 24.0, 41 ),
         2: _usage( 20.0, 82 ),
         3: _usage( 26.0, 82 ),
      },
      82,
      NhlLineupSelector.DRESSED_DEFENSE,
      NhlLineupSelector.DEFENSE_POSITIONS )
   assert shares[ Position.FIRST ] == 1.0
   assert shares[ Position.SECOND ] == 0.5
   assert shares[ Position.THIRD ] == 1.0
   assert len( shares ) == NhlLineupSelector.DRESSED_DEFENSE
   assert shares[ -1 ] == GamesShare.FULL


def Test_Shares_TestLowGames_ExpectRankedByToi() -> None:
   team = list( Team )[ Position.FIRST ]
   shares = LastCore.shares(
      team,
      {
         1: _usage( 30.0, 6 ),
         2: _usage( 16.0, 82 ),
      },
      82,
      NhlLineupSelector.DRESSED_DEFENSE,
      NhlLineupSelector.DEFENSE_POSITIONS )
   assert shares[ Position.FIRST ] == 6 / 82
   assert shares[ Position.SECOND ] == 1.0


def Test_Teammates_TestTopSix_ExpectPacesAndShares() -> None:
   team = list( Team )[ Position.FIRST ]
   ice_usages = {
      player_id: _usage( 30.0 - player_id, 82 - player_id )
      for player_id in range( 1, 8 )
   }
   regulars, extras = LastCore.teammates(
      team,
      ice_usages,
      { player_id: 40.0 - player_id for player_id in range( 1, 8 ) },
      82,
      False,
      NhlLineupSelector.DRESSED_DEFENSE,
      LastCore.EXTRA,
      NhlLineupSelector.DEFENSE_POSITIONS )
   assert [ skater.player_id for skater in regulars ] == list( range( 1, 7 ) )
   assert regulars[ Position.FIRST ].availability == 81 / 82
   assert extras[ Position.FIRST ].player_id == 7
   assert extras[ Position.FIRST ].availability == 1.0
   assert extras[ Position.FIRST ].contribution == 33.0


def Test_Teammates_TestHealthy_ExpectFullShare() -> None:
   team = list( Team )[ Position.FIRST ]
   regulars, _extras = LastCore.teammates(
      team,
      {
         player_id: _usage( 30.0 - player_id, 41 )
         for player_id in range( 1, 7 )
      },
      { player_id: 20.0 for player_id in range( 1, 7 ) },
      82,
      True,
      NhlLineupSelector.DRESSED_DEFENSE,
      LastCore.EXTRA,
      NhlLineupSelector.DEFENSE_POSITIONS )
   assert regulars[ Position.FIRST ].availability == GamesShare.FULL


def Test_Shares_TestForwardOnTeam_ExpectDefenseOnly() -> None:
   team = list( Team )[ Position.FIRST ]
   shares = LastCore.shares(
      team,
      {
         1: _usage( 24.0, 82 ),
         2: IceUsage(
            30.0,
            82,
            team,
            SkaterPosition( 'C' ) ),
      },
      82,
      NhlLineupSelector.DRESSED_DEFENSE,
      NhlLineupSelector.DEFENSE_POSITIONS )
   assert shares[ Position.FIRST ] == 1.0
   assert shares[ Position.SECOND ] == GamesShare.FULL
