from __future__ import annotations

from datetime import date
from pathlib import Path

from api.nhl_skater_season import NhlSkaterSeason
from api.player_names.data_access.player_name_provider import PlayerNameProvider
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.skater_season_store import SkaterSeasonStore
from api.team import Team


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


def Test_Summaries_TestMissingTable_ExpectEmptyList( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   assert PlayerNameProvider.summaries( db_path ) == []


def Test_Summaries_TestDuplicateSeasons_ExpectLatestTeamAndFirstSeason(
      tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   first_team = list( Team )[ Position.FIRST ]
   latest_team = list( Team )[ Position.SECOND ]
   position = list( SkaterPosition )[ Position.FIRST ]
   first_season_id = 20202021
   latest_season_id = 20252026
   SkaterSeasonStore.insert_rows(
      [
         _season( 1, latest_season_id, 'Stub Skater', position, latest_team ),
         _season( 1, first_season_id, 'Stub Skater', position, first_team ),
      ],
      db_path=db_path )
   summaries = PlayerNameProvider.summaries( db_path )
   assert len( summaries ) == 1
   summary = summaries[ Position.FIRST ]
   assert summary.player_id == 1
   assert summary.team == latest_team
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
   summaries = PlayerNameProvider.summaries( db_path )
   assert [ summary.player_id for summary in summaries ] == [ 1, 2 ]
   assert summaries[ Position.FIRST ].position == first_position
   assert summaries[ Position.SECOND ].position == second_position
   assert summaries[ Position.FIRST ].first_season_id == first_debut_id
   assert summaries[ Position.SECOND ].first_season_id == second_debut_id


def Test_Summaries_TestInactivePlayer_ExpectExcluded( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   current_season_id = 20252026
   retired_season_id = 20202021
   SkaterSeasonStore.insert_rows(
      [
         _season( 1, current_season_id, 'Active Skater', position, team ),
         _season( 2, retired_season_id, 'Retired Skater', position, team ),
      ],
      db_path=db_path )
   summaries = PlayerNameProvider.summaries( db_path )
   assert [ summary.player_id for summary in summaries ] == [ 1 ]
