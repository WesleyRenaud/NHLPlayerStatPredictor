from __future__ import annotations

from datetime import date
from pathlib import Path

from api.draft_class import DraftClass
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_season_provider import OtherLeagueSeasonProvider
from api.skaters.other_league_season_store import OtherLeagueSeasonStore
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season_store import SkaterSeasonStore
from api.skaters.team import Team


def _season( player_id: int, season_id: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )


def _nhl( player_id: int, birth_date: date ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=20262027,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=birth_date,
      age=18.0,
      team=list( Team )[ Position.FIRST ],
      games_played=2,
      even_strength_goals=0,
      even_strength_points=0,
      goals=0,
      assists=0,
      points=0,
      schedule_games=84,
      pace_games=84,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      shots=0,
      penalty_minutes=0 )


def Test_SeasonsForPlayerId_TestBirthDate_ExpectDraftClassAge( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   player_id = 7
   season_id = 20252026
   birth_date = date( 2008, 3, 12 )
   recorded = _season( player_id, season_id )
   OtherLeagueSeasonStore.insert_rows( [ recorded ], db_path=db_path )
   SkaterSeasonStore.insert_rows( [ _nhl( player_id, birth_date ) ], db_path=db_path )

   rows = OtherLeagueSeasonProvider.seasons_for_player_id( player_id, db_path )

   assert rows[ 0 ].age == DraftClass.age( birth_date, season_id )


def Test_SeasonsForPlayerId_TestInsertedSeason_ExpectLookupById( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   row = _season( 7, 20252026 )
   OtherLeagueSeasonStore.insert_rows( [ row ], db_path=db_path )

   rows = OtherLeagueSeasonProvider.seasons_for_player_id( row.player_id, db_path )

   assert rows == [ row ]


def Test_SeasonsForSeasonId_TestMixedSeasons_ExpectMatchingYear( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   wanted = 20252026
   matching = _season( 1, wanted )
   other = _season( 2, 20242025 )
   OtherLeagueSeasonStore.insert_rows( [ matching, other ], db_path=db_path )

   rows = OtherLeagueSeasonProvider.seasons_for_season_id( wanted, db_path )

   assert rows == [ matching ]


def Test_SeasonsForPlayerIds_TestMixedPlayers_ExpectRequested(
      tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   wanted = _season( 1, 20252026 )
   other = _season( 2, 20252026 )
   OtherLeagueSeasonStore.insert_rows( [ wanted, other ], db_path=db_path )

   rows = OtherLeagueSeasonProvider.seasons_for_player_ids(
      [ wanted.player_id ],
      db_path )

   assert rows == [ wanted ]
