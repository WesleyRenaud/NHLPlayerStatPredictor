from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_group import DepthGroup
from api.depth.ice_usage import IceUsage
from api.depth.slot_chosen_share_fitter import SlotChosenShareFitter
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


def Test_Fit_TestTwoTeams_ExpectDressMeansAndChosen() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   position = SkaterPosition( 'D' )
   usages = dict( [
      _usage( 1, 24.0, 80, first, position ),
      _usage( 2, 20.0, 40, first, position ),
      _usage( 3, 23.0, 84, second, position ),
      _usage( 4, 18.0, 42, second, position ),
   ] )
   shares = SlotChosenShareFitter.fit( usages, 82, DepthGroup.defense() )
   assert [ share.slot for share in shares ] == [ 1, 2 ]
   assert shares[ Position.FIRST ].skater_group is SkaterGroup( 'D' )
   assert abs( shares[ Position.FIRST ].dress_share - 82.0 / 82.0 ) < 0.001
   assert shares[ Position.FIRST ].chosen == GamesShare.FULL
   assert abs( shares[ Position.LAST ].dress_share - 41.0 / 82.0 ) < 0.001
   assert abs( shares[ Position.LAST ].chosen - 0.5 ) < 0.001


def Test_Fit_TestHigherSlotGames_ExpectChosenCapped() -> None:
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'D' )
   usages = dict( [
      _usage( 1, 24.0, 70, team, position ),
      _usage( 2, 20.0, 80, team, position ),
   ] )
   shares = SlotChosenShareFitter.fit( usages, 82, DepthGroup.defense() )
   assert shares[ Position.FIRST ].chosen == GamesShare.FULL
   assert shares[ Position.LAST ].chosen == GamesShare.FULL


def Test_Fit_TestHighToiFewGames_ExpectLowerSlot() -> None:
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'D' )
   usages = dict( [
      _usage( 1, 21.0, 4, team, position ),
      _usage( 2, 18.0, 80, team, position ),
   ] )
   shares = SlotChosenShareFitter.fit( usages, 82, DepthGroup.defense() )
   assert abs( shares[ Position.FIRST ].dress_share - 80.0 / 82.0 ) < 0.001
   assert abs( shares[ Position.LAST ].dress_share - 4.0 / 82.0 ) < 0.001


def Test_Fit_TestEmpty_ExpectEmpty() -> None:
   assert SlotChosenShareFitter.fit( {}, 82, DepthGroup.forwards() ) == []
