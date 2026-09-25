from __future__ import annotations

from datetime import date
from pathlib import Path

from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season_provider import SkaterSeasonProvider
from api.skaters.skater_season_store import SkaterSeasonStore
from api.skaters.team import Team


def _season( player_id: int, season_id: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=82,
      goals=10,
      assists=20,
      points=30,
      schedule_games=82,
      pace_games=84,
      g_pace=10.0,
      a_pace=20.0,
      p_pace=30.0,
      gp_share=1.0 )


def Test_SeasonsForName_TestInsertedPlayer_ExpectLookupByName( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   SkaterSeasonStore.insert_rows(
      [ NhlSkaterSeason(
         player_id=8478402,
         season_id=20252026,
         player_name='Connor McDavid',
         position=list( SkaterPosition )[ Position.FIRST ],
         birth_date=date( 1997, 1, 13 ),
         age=28.7,
         team=list( Team )[ Position.FIRST ],
         games_played=82,
         goals=48,
         assists=90,
         points=138,
         schedule_games=82,
         pace_games=84,
         g_pace=48.0,
         a_pace=90.0,
         p_pace=138.0,
         gp_share=1.0 ) ],
      db_path=db_path )

   rows = SkaterSeasonProvider.seasons_for_name( 'mcdavid', db_path=db_path )
   assert len( rows ) == 1
   assert rows[ Position.FIRST ].points == 138


def Test_SeasonsForPlayerId_TestInsertedPlayer_ExpectLookupById( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   row = _season( 7, 20202021 )
   SkaterSeasonStore.insert_rows( [ row ], db_path=db_path )

   rows = SkaterSeasonProvider.seasons_for_player_id( row.player_id, db_path=db_path )
   assert len( rows ) == 1
   assert rows[ Position.FIRST ].player_id == row.player_id
   assert rows[ Position.FIRST ].points == row.points


def Test_SeasonsForSeasonId_TestMixedSeasons_ExpectMatchingYear( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   wanted = 20252026
   matching = _season( 1, wanted )
   other = _season( 2, 20242025 )
   SkaterSeasonStore.insert_rows( [ matching, other ], db_path=db_path )
   rows = SkaterSeasonProvider.seasons_for_season_id( wanted, db_path )
   assert rows == [ matching ]


def Test_SeasonsForPlayerIds_TestMixedPlayers_ExpectRequested(
      tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   wanted = _season( 1, 20252026 )
   other = _season( 2, 20252026 )
   SkaterSeasonStore.insert_rows( [ wanted, other ], db_path=db_path )
   rows = SkaterSeasonProvider.seasons_for_player_ids(
      [ wanted.player_id ],
      db_path )
   assert rows == [ wanted ]
