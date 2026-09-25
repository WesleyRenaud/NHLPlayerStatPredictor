from __future__ import annotations

from datetime import date
from pathlib import Path

from api.player_names.data_access.player_name_provider import PlayerNameProvider
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_season_store import OtherLeagueSeasonStore
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.roster_skater import RosterSkater
from api.skaters.roster_skater_store import RosterSkaterStore
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season_store import SkaterSeasonStore
from api.skaters.team import Team


def _season(
      player_id: int,
      season_id: int,
      player_name: str,
      position: SkaterPosition,
      team: Team ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name=player_name,
      position=position,
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=team,
      games_played=82,
      goals=48,
      assists=90,
      points=138,
      schedule_games=82,
      pace_games=84,
      g_pace=48.0,
      a_pace=90.0,
      p_pace=138.0,
      gp_share=1.0 )


def _other( player_id: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id,
      season_id=20252026,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )


def _roster(
      player_id: int,
      player_name: str,
      position: SkaterPosition,
      team: Team ) -> RosterSkater:
   return RosterSkater(
      player_id=player_id,
      player_name=player_name,
      position=position,
      team=team )


def Test_Summaries_TestMissingTable_ExpectEmptyList( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   target_season_id = 20262027
   assert PlayerNameProvider.summaries( db_path, target_season_id ) == []


def Test_Summaries_TestDuplicateSeasons_ExpectRosterTeamAndFirstSeason(
      tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   first_team = list( Team )[ Position.FIRST ]
   latest_team = list( Team )[ Position.SECOND ]
   roster_team = list( Team )[ Position.THIRD ]
   position = list( SkaterPosition )[ Position.FIRST ]
   first_season_id = 20202021
   latest_season_id = 20252026
   target_season_id = 20262027
   player_name = 'Stub Skater'
   SkaterSeasonStore.insert_rows(
      [
         _season( 1, latest_season_id, player_name, position, latest_team ),
         _season( 1, first_season_id, player_name, position, first_team ),
      ],
      db_path=db_path )
   RosterSkaterStore.insert_rows(
      [ _roster( 1, player_name, position, roster_team ) ],
      db_path=db_path )
   summaries = PlayerNameProvider.summaries( db_path, target_season_id )
   assert len( summaries ) == 1
   summary = summaries[ Position.FIRST ]
   assert summary.player_id == 1
   assert summary.team == roster_team
   assert summary.first_season_id == first_season_id
   assert summary.position == position


def Test_Summaries_TestSharedName_ExpectSeparatePlayers( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   shared_name = 'Shared Skater'
   first_position = list( SkaterPosition )[ Position.FIRST ]
   second_position = list( SkaterPosition )[ Position.SECOND ]
   first_team = list( Team )[ Position.FIRST ]
   second_team = list( Team )[ Position.SECOND ]
   current_season_id = 20252026
   target_season_id = 20262027
   first_debut_id = 20182019
   second_debut_id = 20232024
   SkaterSeasonStore.insert_rows(
      [
         _season( 2, current_season_id, shared_name, second_position, second_team ),
         _season( 2, second_debut_id, shared_name, second_position, second_team ),
         _season( 1, current_season_id, shared_name, first_position, first_team ),
         _season( 1, first_debut_id, shared_name, first_position, first_team ),
      ],
      db_path=db_path )
   RosterSkaterStore.insert_rows(
      [
         _roster( 1, shared_name, first_position, first_team ),
         _roster( 2, shared_name, second_position, second_team ),
      ],
      db_path=db_path )
   summaries = PlayerNameProvider.summaries( db_path, target_season_id )
   assert [ summary.player_id for summary in summaries ] == [ 1, 2 ]
   assert summaries[ Position.FIRST ].position == first_position
   assert summaries[ Position.SECOND ].position == second_position
   assert summaries[ Position.FIRST ].first_season_id == first_debut_id
   assert summaries[ Position.SECOND ].first_season_id == second_debut_id


def Test_Summaries_TestMissingRoster_ExpectExcluded( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   current_season_id = 20252026
   target_season_id = 20262027
   SkaterSeasonStore.insert_rows(
      [
         _season( 1, current_season_id, 'Rostered Skater', position, team ),
         _season( 2, current_season_id, 'Unrostered Skater', position, team ),
      ],
      db_path=db_path )
   RosterSkaterStore.insert_rows(
      [ _roster( 1, 'Rostered Skater', position, team ) ],
      db_path=db_path )
   summaries = PlayerNameProvider.summaries( db_path, target_season_id )
   assert [ summary.player_id for summary in summaries ] == [ 1 ]


def Test_Summaries_TestOtherLeagueOnly_ExpectTargetFirstSeason( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   target_season_id = 20262027
   player_name = 'Rostered Rookie'
   OtherLeagueSeasonStore.insert_rows( [ _other( 2 ) ], db_path=db_path )
   RosterSkaterStore.insert_rows(
      [ _roster( 2, player_name, position, team ) ],
      db_path=db_path )
   summaries = PlayerNameProvider.summaries( db_path, target_season_id )
   assert len( summaries ) == 1
   summary = summaries[ Position.FIRST ]
   assert summary.player_id == 2
   assert summary.player_name == player_name
   assert summary.team == team
   assert summary.first_season_id == target_season_id


def Test_Summaries_TestRosterWithoutSeasons_ExpectExcluded( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   target_season_id = 20262027
   RosterSkaterStore.insert_rows(
      [ _roster( 3, 'Empty Roster Skater', position, team ) ],
      db_path=db_path )
   summaries = PlayerNameProvider.summaries( db_path, target_season_id )
   assert summaries == []
