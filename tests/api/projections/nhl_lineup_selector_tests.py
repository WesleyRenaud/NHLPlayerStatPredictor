from __future__ import annotations

from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _split(
      player_id: int,
      team: Team,
      points: float,
      games: int,
      position: SkaterPosition = SkaterPosition( 'C' ) ) -> PreviousSeasonNhlSkater:
   return PreviousSeasonNhlSkater(
      player_id,
      games,
      SeasonPace( points / 2.0, points / 2.0 ),
      position,
      team )


def _pace(
      player_id: int,
      team: Team,
      points: float,
      position: SkaterPosition = SkaterPosition( 'C' ) ) -> CurrentSeasonNhlSkater:
   return CurrentSeasonNhlSkater(
      player_id,
      SeasonPace( points / 2.0, points / 2.0 ),
      team,
      position )


def Test_Select_TestExcessDepth_ExpectTopForwardsAndDefense() -> None:
   team = list( Team )[ Position.FIRST ]
   forwards = [
      _pace( player_id, team, 100.0 - player_id )
      for player_id in range( 1, NhlLineupSelector.FORWARDS + 2 )
   ]
   defense = [
      _pace(
         player_id,
         team,
         80.0 - player_id,
         position=SkaterPosition( 'D' ) )
      for player_id in range( 101, 101 + NhlLineupSelector.DEFENSE + 1 )
   ]
   assert NhlLineupSelector.select( [ *forwards, *defense ] ) == [
      *forwards[ :NhlLineupSelector.FORWARDS ],
      *defense[ :NhlLineupSelector.DEFENSE ],
   ]


def Test_Select_TestWings_ExpectForwardSlots() -> None:
   team = list( Team )[ Position.FIRST ]
   centers = [
      _pace( player_id, team, 100.0 - player_id )
      for player_id in range( 1, NhlLineupSelector.FORWARDS + 1 )
   ]
   wing = _pace(
      NhlLineupSelector.FORWARDS + 1,
      team,
      5.0,
      position=SkaterPosition( 'L' ) )
   defense = _pace( 50, team, 40.0, position=SkaterPosition( 'D' ) )
   assert NhlLineupSelector.select(
      [ *centers, wing, defense ] ) == [ *centers, defense ]


def Test_Select_TestTeams_ExpectIsolatedCuts() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   now_forwards = [
      _pace( player_id, now, 100.0 - player_id )
      for player_id in range( 1, NhlLineupSelector.FORWARDS + 2 )
   ]
   previous_forwards = [
      _pace( player_id, previous, 50.0 - player_id )
      for player_id in range( 21, 21 + NhlLineupSelector.FORWARDS + 1 )
   ]
   assert NhlLineupSelector.select(
      [ *now_forwards, *previous_forwards ] ) == [
         *now_forwards[ :NhlLineupSelector.FORWARDS ],
         *previous_forwards[ :NhlLineupSelector.FORWARDS ],
      ]


def Test_Select_TestSweaterPoints_ExpectGamesWeightedRank() -> None:
   team = list( Team )[ Position.FIRST ]
   injured = _split( 1, team, 80.0, 10 )
   regular = _split( 2, team, 20.0, 82 )
   assert NhlLineupSelector.select( [ injured, regular ] ) == [ regular, injured ]
