from __future__ import annotations

from datetime import date

from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.roster_skater import RosterSkater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _season( season_id: int, player_id: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=1.0 )


def Test_FromRow_TestStoredFields_ExpectValues() -> None:
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   row = RosterSkater( 7, 'Stub Skater', position, team )

   loaded = RosterSkater.from_row( {
      'PLAYER_ID': row.player_id,
      'PLAYER_NAME': row.player_name,
      'POSITION': row.position.value,
      'TEAM': row.team.value,
   } )

   assert loaded == row


def Test_WithLastPlayed_TestNhlSeasons_ExpectLatestPerPlayer() -> None:
   roster_id = 2
   other_id = 1
   latest_season_id = 20242025
   earlier_season_id = 20232024
   team = list( Team )[ Position.FIRST ]
   player_name = 'A'
   position = SkaterPosition( 'C' )
   roster = [ RosterSkater( roster_id, player_name, position, team ) ]
   seasons = [
      _season( earlier_season_id, other_id ),
      _season( latest_season_id, roster_id ),
      _season( earlier_season_id, roster_id ),
   ]

   stamped = RosterSkater.with_last_played( roster, seasons )

   assert stamped == [
      RosterSkater(
         roster_id,
         player_name,
         position,
         team,
         last_played_season_id=latest_season_id )
   ]


def Test_WithLastPlayed_TestNoNhl_ExpectNone() -> None:
   other_id = 1
   other_season_id = 20242025
   team = list( Team )[ Position.FIRST ]
   roster = [
      RosterSkater(
         2,
         'A',
         SkaterPosition( 'C' ),
         team )
   ]
   seasons = [ _season( other_season_id, other_id ) ]

   stamped = RosterSkater.with_last_played( roster, seasons )

   assert stamped == roster
